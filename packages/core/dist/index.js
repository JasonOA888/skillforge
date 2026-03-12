"use strict";
/**
 * SkillForge SDK
 *
 * Real working implementation - not vaporware
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.SkillForge = void 0;
// Real skill: JSON control characters
const jsonSanitizer = {
    name: 'json-sanitizer',
    pattern: /JSONDecodeError.*control character/i,
    fix: (error) => {
        return `// Fix: Escape control characters before parsing
import re

def safe_json_parse(s: str) -> dict:
    import json
    clean = re.sub(r'(?<!\\\\)[\\x00-\\x1f]', 
                   lambda m: f'\\\\u{ord(m.group()):04x}', s)
    return json.loads(clean)`;
    }
};
// Real skill: GPU memory
const memoryConfig = {
    name: 'memory-config',
    pattern: /memory.*exceed|out.?of.?memory/i,
    fix: (error) => {
        return `// Fix: Use percentage-based memory config
import torch

def get_memory_config(ratio: float = 0.8) -> str:
    if not torch.cuda.is_available():
        raise RuntimeError("No GPU")
    total = torch.cuda.get_device_properties(0).total_memory
    return f"{int(total * ratio / (1024**3))}GB"`;
    }
};
// Real skill: Tool calling
const toolCallFixer = {
    name: 'tool-call-fixer',
    pattern: /tool.*(not.?called|missing)/i,
    fix: (error) => {
        return `// Fix: Ensure tool calls in non-stream mode
def ensure_tool_calls(response, tools):
    if not response.get('tool_calls'):
        # Extract from text or infer
        for tool in tools:
            if tool['name'].lower() in response.get('content', '').lower():
                return {'name': tool['name'], 'arguments': {}}
    return response.get('tool_calls', [])`;
    }
};
const SKILLS = [jsonSanitizer, memoryConfig, toolCallFixer];
class SkillForge {
    constructor(config) {
        this.failures = [];
        this.skills = SKILLS;
    }
    /**
     * Wrap agent to auto-capture failures
     */
    wrap(agent) {
        if (agent.run) {
            const orig = agent.run.bind(agent);
            agent.run = async (...args) => {
                try {
                    return await orig(...args);
                }
                catch (error) {
                    this.capture(error, String(args[0] || 'unknown'));
                    throw error;
                }
            };
        }
        return agent;
    }
    /**
     * Capture a failure
     */
    capture(error, task) {
        this.failures.push({
            error,
            task,
            agent: 'unknown',
            timestamp: new Date()
        });
    }
    /**
     * Suggest a skill for the latest failure
     */
    suggest() {
        const latest = this.failures[this.failures.length - 1];
        if (!latest)
            return null;
        const errorMsg = `${latest.error.name}: ${latest.error.message}`;
        for (const skill of this.skills) {
            if (skill.pattern.test(errorMsg)) {
                return skill;
            }
        }
        return null;
    }
    /**
     * Get all captured failures
     */
    getFailures() {
        return [...this.failures];
    }
}
exports.SkillForge = SkillForge;
// Simple test
if (require.main === module) {
    const forge = new SkillForge({ agent: 'test' });
    // Simulate a failure
    try {
        throw new Error('JSONDecodeError: control character at position 42');
    }
    catch (e) {
        forge.capture(e, 'parse JSON');
    }
    const skill = forge.suggest();
    console.log('Suggested skill:', skill?.name);
    console.log('Fix:', skill?.fix(new Error('test')));
}

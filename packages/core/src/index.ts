/**
 * SkillForge SDK
 * 
 * Real working implementation - not vaporware
 */

export interface Failure {
  error: Error;
  task: string;
  agent: string;
  timestamp: Date;
}

export interface Skill {
  name: string;
  pattern: RegExp;
  fix: (error: Error) => string;
}

// Pattern: JSON control characters (generic)
const jsonSanitizer: Skill = {
  name: 'json-sanitizer',
  pattern: /JSONDecodeError.*control character/i,
  fix: (error: Error): string => {
    return `// Fix: Escape control characters before parsing
import re

def safe_json_parse(s: str) -> dict:
    import json
    clean = re.sub(r'(?<!\\\\)[\\x00-\\x1f]', 
                   lambda m: f'\\\\u{ord(m.group()):04x}', s)
    return json.loads(clean)`;
  }
};

// Pattern: GPU memory (generic)
const memoryConfig: Skill = {
  name: 'memory-config', 
  pattern: /memory.*exceed|out.?of.?memory/i,
  fix: (error: Error): string => {
    return `// Fix: Use percentage-based memory config
import torch

def get_memory_config(ratio: float = 0.8) -> str:
    if not torch.cuda.is_available():
        raise RuntimeError("No GPU")
    total = torch.cuda.get_device_properties(0).total_memory
    return f"{int(total * ratio / (1024**3))}GB"`;
  }
};

// Pattern: Tool calling (generic)
const toolCallFixer: Skill = {
  name: 'tool-call-fixer',
  pattern: /tool.*(not.?called|missing)/i,
  fix: (error: Error): string => {
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

const SKILLS: Skill[] = [jsonSanitizer, memoryConfig, toolCallFixer];

export class SkillForge {
  private failures: Failure[] = [];
  private skills: Skill[];

  constructor(config: { agent: string }) {
    this.skills = SKILLS;
  }

  /**
   * Wrap agent to auto-capture failures
   */
  wrap<T extends { run?: Function; execute?: Function }>(agent: T): T {
    if (agent.run) {
      const orig = agent.run.bind(agent);
      agent.run = async (...args: any[]) => {
        try {
          return await orig(...args);
        } catch (error) {
          this.capture(error as Error, String(args[0] || 'unknown'));
          throw error;
        }
      };
    }
    return agent;
  }

  /**
   * Capture a failure
   */
  capture(error: Error, task: string): void {
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
  suggest(): Skill | null {
    const latest = this.failures[this.failures.length - 1];
    if (!latest) return null;

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
  getFailures(): Failure[] {
    return [...this.failures];
  }
}

// Simple test
if (require.main === module) {
  const forge = new SkillForge({ agent: 'test' });
  
  // Simulate a failure
  try {
    throw new Error('JSONDecodeError: control character at position 42');
  } catch (e) {
    forge.capture(e as Error, 'parse JSON');
  }
  
  const skill = forge.suggest();
  console.log('Suggested skill:', skill?.name);
  console.log('Fix:', skill?.fix(new Error('test')));
}

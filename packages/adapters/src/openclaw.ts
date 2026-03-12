/**
 * SkillForge OpenClaw Adapter
 * 
 * Captures failures from OpenClaw agents and suggests skills.
 */

import { SkillForge, Failure } from '@skillforge/sdk';

export class OpenClawAdapter {
  private forge: SkillForge;

  constructor(forge: SkillForge) {
    this.forge = forge;
  }

  /**
   * Wrap an OpenClaw agent to auto-capture failures
   */
  wrapAgent(agent: any): void {
    // OpenClaw agents typically have a 'run' method
    const originalRun = agent.run?.bind(agent);
    
    if (originalRun) {
      agent.run = async (input: string, ...args: any[]) => {
        try {
          return await originalRun(input, ...args);
        } catch (error: any) {
          await this.captureOpenClawFailure(error, {
            input,
            agentState: this.getAgentState(agent),
          });
          throw error;
        }
      };
    }

    // Some OpenClaw agents have 'execute' method
    const originalExecute = agent.execute?.bind(agent);
    
    if (originalExecute) {
      agent.execute = async (task: any, ...args: any[]) => {
        try {
          return await originalExecute(task, ...args);
        } catch (error: any) {
          await this.captureOpenClawFailure(error, {
            task,
            agentState: this.getAgentState(agent),
          });
          throw error;
        }
      };
    }

    // Wrap tool calls
    this.wrapTools(agent);
  }

  /**
   * Wrap tool calls to capture tool-specific failures
   */
  private wrapTools(agent: any): void {
    if (!agent.tools) return;

    for (const tool of agent.tools) {
      const originalCall = tool.call?.bind(tool);
      
      if (originalCall) {
        tool.call = async (...args: any[]) => {
          try {
            return await originalCall(...args);
          } catch (error: any) {
            await this.captureOpenClawFailure(error, {
              tool: tool.name || 'unknown',
              args,
              agentState: this.getAgentState(agent),
            });
            throw error;
          }
        };
      }
    }
  }

  /**
   * Get agent state for debugging
   */
  private getAgentState(agent: any): any {
    try {
      return {
        name: agent.name || 'unknown',
        tools: agent.tools?.map((t: any) => t.name) || [],
        memory: agent.memory?.slice(-10) || [], // Last 10 items
        config: agent.config || {},
      };
    } catch {
      return {};
    }
  }

  /**
   * Capture failure with OpenClaw-specific context
   */
  private async captureOpenClawFailure(error: any, context: any): Promise<Failure> {
    return await this.forge.captureFailure(error, {
      task: context.input || context.task || 'unknown',
      context: {
        framework: 'openclaw',
        ...context,
      },
    });
  }

  /**
   * Apply skill to OpenClaw agent
   */
  async applySkill(skill: any, agent: any): Promise<void> {
    // Inject skill into agent's skill registry
    if (!agent.skills) {
      agent.skills = {};
    }

    agent.skills[skill.name] = skill;

    // Some OpenClaw agents have a skill loader
    if (agent.loadSkill) {
      await agent.loadSkill(skill);
    }
  }

  /**
   * Get skill suggestions for OpenClaw context
   */
  async getSuggestions(errorType: string): Promise<any[]> {
    // OpenClaw-specific skill mapping
    const openClawSkillMap: Record<string, string[]> = {
      'JSONDecodeError': ['json-sanitizer', 'robust-json-parser'],
      'MemoryError': ['adaptive-memory-config'],
      'TimeoutError': ['timeout-handler'],
      'RateLimitError': ['rate-limit-handler'],
      'ToolCallError': ['tool-call-fixer'],
    };

    const skillNames = openClawSkillMap[errorType] || [];
    
    // Fetch skill details from registry
    // In production, this would call the SkillForge API
    return skillNames.map(name => ({ name, framework: 'openclaw' }));
  }
}

// Auto-detection helper
export function detectOpenClawAgent(obj: any): boolean {
  return (
    obj &&
    (typeof obj.run === 'function' || typeof obj.execute === 'function') &&
    (obj.tools || obj.skills || obj.memory)
  );
}

export default OpenClawAdapter;

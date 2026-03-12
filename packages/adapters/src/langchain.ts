/**
 * SkillForge LangChain Adapter
 * 
 * Captures failures from LangChain chains, agents, and tools.
 */

import { SkillForge, Failure } from '@skillforge/sdk';

export class LangChainAdapter {
  private forge: SkillForge;

  constructor(forge: SkillForge) {
    this.forge = forge;
  }

  /**
   * Wrap a LangChain Runnable (chains, agents, etc.)
   */
  wrapRunnable(runnable: any): any {
    const originalInvoke = runnable.invoke?.bind(runnable);
    
    if (originalInvoke) {
      runnable.invoke = async (input: any, options?: any) => {
        try {
          return await originalInvoke(input, options);
        } catch (error: any) {
          await this.captureLangChainFailure(error, {
            input,
            runnableType: this.getRunnableType(runnable),
            options,
          });
          throw error;
        }
      };
    }

    const originalBatch = runnable.batch?.bind(runnable);
    
    if (originalBatch) {
      runnable.batch = async (inputs: any[], options?: any) => {
        try {
          return await originalBatch(inputs, options);
        } catch (error: any) {
          await this.captureLangChainFailure(error, {
            inputs,
            runnableType: this.getRunnableType(runnable),
            failedIndex: this.findFailedIndex(error, inputs.length),
          });
          throw error;
        }
      };
    }

    const originalStream = runnable.stream?.bind(runnable);
    
    if (originalStream) {
      runnable.stream = async function* (input: any, options?: any) {
        try {
          for await (const chunk of originalStream(input, options)) {
            yield chunk;
          }
        } catch (error: any) {
          await this.captureLangChainFailure(error, {
            input,
            runnableType: this.getRunnableType(runnable),
            streamError: true,
          });
          throw error;
        }
      }.bind(this);
    }

    return runnable;
  }

  /**
   * Wrap a LangChain Agent
   */
  wrapAgent(agent: any): any {
    // Wrap the agent executor
    if (agent.agentExecutor) {
      this.wrapRunnable(agent.agentExecutor);
    }

    // Wrap tools
    if (agent.tools) {
      this.wrapTools(agent.tools);
    }

    return agent;
  }

  /**
   * Wrap LangChain tools
   */
  wrapTools(tools: any[]): void {
    for (const tool of tools) {
      const originalCall = tool.call?.bind(tool);
      
      if (originalCall) {
        tool.call = async (input: any) => {
          try {
            return await originalCall(input);
          } catch (error: any) {
            await this.captureLangChainFailure(error, {
              toolName: tool.name,
              toolDescription: tool.description,
              input,
            });
            throw error;
          }
        };
      }

      // Some tools use _call (protected method)
      if (tool._call) {
        const originalUnderscoreCall = tool._call.bind(tool);
        tool._call = async (input: any) => {
          try {
            return await originalUnderscoreCall(input);
          } catch (error: any) {
            await this.captureLangChainFailure(error, {
              toolName: tool.name,
              input,
            });
            throw error;
          }
        };
      }
    }
  }

  /**
   * Wrap a LangChain Chain
   */
  wrapChain(chain: any): any {
    // Modern LangChain uses Runnable
    if (chain.invoke) {
      return this.wrapRunnable(chain);
    }

    // Legacy Chain interface
    const originalCall = chain.call?.bind(chain);
    
    if (originalCall) {
      chain.call = async (args: any) => {
        try {
          return await originalCall(args);
        } catch (error: any) {
          await this.captureLangChainFailure(error, {
            chainType: chain.constructor.name,
            args,
          });
          throw error;
        }
      };
    }

    const originalRun = chain.run?.bind(chain);
    
    if (originalRun) {
      chain.run = async (input: string) => {
        try {
          return await originalRun(input);
        } catch (error: any) {
          await this.captureLangChainFailure(error, {
            chainType: chain.constructor.name,
            input,
          });
          throw error;
        }
      };
    }

    return chain;
  }

  /**
   * Wrap a LangChain LLM
   */
  wrapLLM(llm: any): any {
    const originalGenerate = llm.generate?.bind(llm);
    
    if (originalGenerate) {
      llm.generate = async (prompts: string[], options?: any) => {
        try {
          return await originalGenerate(prompts, options);
        } catch (error: any) {
          await this.captureLangChainFailure(error, {
            llmType: llm.constructor.name,
            promptCount: prompts.length,
            firstPrompt: prompts[0]?.slice(0, 100),
          });
          throw error;
        }
      };
    }

    const originalInvoke = llm.invoke?.bind(llm);
    
    if (originalInvoke) {
      llm.invoke = async (input: any, options?: any) => {
        try {
          return await originalInvoke(input, options);
        } catch (error: any) {
          await this.captureLangChainFailure(error, {
            llmType: llm.constructor.name,
            input: typeof input === 'string' ? input.slice(0, 100) : input,
          });
          throw error;
        }
      };
    }

    return llm;
  }

  /**
   * Get runnable type for debugging
   */
  private getRunnableType(runnable: any): string {
    if (runnable.lc_namespace) {
      return runnable.lc_namespace.join('.');
    }
    return runnable.constructor.name;
  }

  /**
   * Find which batch item failed
   */
  private findFailedIndex(error: any, total: number): number | null {
    // LangChain sometimes includes the index in error
    if (error.index !== undefined) {
      return error.index;
    }
    if (error.message?.match(/item (\d+)/)) {
      return parseInt(error.message.match(/item (\d+)/)[1]);
    }
    return null;
  }

  /**
   * Capture failure with LangChain-specific context
   */
  private async captureLangChainFailure(error: any, context: any): Promise<Failure> {
    return await this.forge.captureFailure(error, {
      task: context.input || context.args || 'LangChain execution',
      context: {
        framework: 'langchain',
        ...context,
        langchainVersion: this.getLangChainVersion(),
      },
    });
  }

  /**
   * Get LangChain version
   */
  private getLangChainVersion(): string {
    try {
      // Try to get from package
      const pkg = require('langchain/package.json');
      return pkg.version;
    } catch {
      return 'unknown';
    }
  }

  /**
   * Apply skill to LangChain chain/agent
   */
  async applySkill(skill: any, target: any): Promise<void> {
    // LangChain uses different mechanisms for different types
    if (target.tools) {
      // Agent - add as tool
      target.tools.push(this.skillToTool(skill));
    } else if (target.callbacks) {
      // Runnable - add callback
      // This is more complex, would need custom callback handler
    }
  }

  /**
   * Convert skill to LangChain tool
   */
  private skillToTool(skill: any): any {
    return {
      name: skill.name,
      description: skill.description,
      call: async (input: string) => {
        // Execute skill
        // In production, would call skill execution engine
        return `Applied skill ${skill.name}`;
      },
    };
  }

  /**
   * Get skill suggestions for LangChain context
   */
  async getSuggestions(errorType: string): Promise<any[]> {
    const langChainSkillMap: Record<string, string[]> = {
      'OutputParserException': ['structured-output-protocol', 'output-fixer'],
      'JSONDecodeError': ['json-sanitizer', 'robust-json-parser'],
      'ToolInputError': ['tool-call-fixer'],
      'TokenLimitError': ['token-optimizer', 'chunking-handler'],
      'RateLimitError': ['rate-limit-handler', 'retry-with-backoff'],
    };

    const skillNames = langChainSkillMap[errorType] || [];
    return skillNames.map(name => ({ name, framework: 'langchain' }));
  }
}

// Auto-detection helper
export function detectLangChain(obj: any): boolean {
  return (
    obj &&
    (obj.lc_namespace || obj.lc_id || 
     obj.constructor?.name?.includes('Chain') ||
     obj.constructor?.name?.includes('Agent'))
  );
}

export default LangChainAdapter;

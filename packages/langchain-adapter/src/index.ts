/**
 * LangChain Adapter for SkillForge
 * 
 * Real integration, not a wrapper
 */

import { SkillForge, Skill } from '../packages/core/src/index';

export class LangChainAdapter {
  private forge: SkillForge;
  
  constructor() {
    this.forge = new SkillForge({ agent: 'langchain' });
  }
  
  /**
   * Wrap a LangChain Runnable
   */
  wrapRunnable<T extends { invoke: Function }>(runnable: T): T {
    const orig = runnable.invoke.bind(runnable);
    const forge = this.forge;
    
    runnable.invoke = async function(...args: any[]) {
      try {
        return await orig(...args);
      } catch (error) {
        forge.capture(error as Error, String(args[0] || 'unknown'));
        throw error;
      }
    };
    
    return runnable;
  }
  
  /**
   * Wrap LangChain tools
   */
  wrapTools(tools: any[]): void {
    for (const tool of tools) {
      if (tool._call) {
        const orig = tool._call.bind(tool);
        const forge = this.forge;
        
        tool._call = async function(input: string) {
          try {
            return await orig(input);
          } catch (error) {
            forge.capture(error as Error, `tool:${tool.name}`);
            throw error;
          }
        };
      }
    }
  }
  
  /**
   * Get skill suggestion for latest error
   */
  suggest(): Skill | null {
    return this.forge.suggest();
  }
  
  /**
   * Get all captured failures
   */
  getFailures() {
    return this.forge.getFailures();
  }
}

// Example usage
/*
import { ChatOpenAI } from "@langchain/openai";
import { LangChainAdapter } from "@skillforge/langchain-adapter";

const model = new ChatOpenAI({});
const adapter = new LangChainAdapter();

// Wrap the model
adapter.wrapRunnable(model);

// Now errors are auto-captured
try {
  await model.invoke("hello");
} catch (e) {
  const skill = adapter.suggest();
  console.log(skill?.fix(e));
}
*/

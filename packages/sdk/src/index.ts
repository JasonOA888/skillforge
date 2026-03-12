/**
 * SkillForge SDK - TypeScript SDK for capturing agent failures
 * 
 * @packageDocumentation
 */

import { v4 as uuidv4 } from 'uuid';

/**
 * Represents a captured agent failure
 */
export interface Failure {
  /** Unique failure ID */
  id: string;
  
  /** Agent name/identifier */
  agent: string;
  
  /** Agent framework (langchain, openclaw, crewai, etc.) */
  framework: string;
  
  /** Error object */
  error: {
    name: string;
    message: string;
    stack?: string;
  };
  
  /** Agent context at time of failure */
  context: any;
  
  /** Task description */
  task: string;
  
  /** Timestamp */
  timestamp: Date;
  
  /** Environment info */
  environment?: {
    node?: string;
    platform?: string;
    versions?: Record<string, string>;
  };
}

/**
 * Represents an evolved skill
 */
export interface Skill {
  /** Skill ID */
  id: string;
  
  /** Skill name */
  name: string;
  
  /** Description */
  description: string;
  
  /** GEP-encoded skill data */
  gene: string;
  
  /** Success rate (0-1) */
  successRate: number;
  
  /** Number of uses */
  uses: number;
  
  /** Token cost reduction (%) */
  tokenEfficiency: number;
  
  /** Creator address */
  creator: string;
  
  /** Version */
  version: string;
  
  /** Tags for searchability */
  tags: string[];
}

/**
 * Skill suggestion result
 */
export interface SkillSuggestion {
  skill: Skill;
  relevance: number;
  reasoning: string;
}

/**
 * SkillForge SDK configuration
 */
export interface SkillForgeConfig {
  /** Agent name */
  agent: string;
  
  /** Agent framework */
  framework?: string;
  
  /** API endpoint (optional, uses default if not provided) */
  endpoint?: string;
  
  /** Auto-capture failures */
  autoCapture?: boolean;
  
  /** Enable debug logging */
  debug?: boolean;
}

/**
 * SkillForge SDK - Main entry point
 * 
 * @example
 * ```typescript
 * import { SkillForge } from '@skillforge/sdk';
 * 
 * const forge = new SkillForge({ agent: 'my-agent' });
 * forge.wrapAgent(agent);
 * ```
 */
export class SkillForge {
  private config: Required<SkillForgeConfig>;
  private failures: Failure[] = [];
  
  constructor(config: SkillForgeConfig) {
    this.config = {
      agent: config.agent,
      framework: config.framework || 'custom',
      endpoint: config.endpoint || 'https://api.skillforge.ai',
      autoCapture: config.autoCapture ?? true,
      debug: config.debug ?? false,
    };
    
    this.log('SkillForge SDK initialized', { config: this.config });
  }
  
  /**
   * Wrap an agent to auto-capture failures
   */
  wrapAgent<T extends { execute?: Function; run?: Function }>(agent: T): T {
    const originalExecute = agent.execute?.bind(agent);
    const originalRun = agent.run?.bind(agent);
    
    if (originalExecute) {
      agent.execute = async (...args: any[]) => {
        try {
          return await originalExecute(...args);
        } catch (error) {
          await this.captureFailure(error as Error, {
            task: args[0] || 'unknown',
            args: args,
          });
          throw error;
        }
      };
    }
    
    if (originalRun) {
      agent.run = async (...args: any[]) => {
        try {
          return await originalRun(...args);
        } catch (error) {
          await this.captureFailure(error as Error, {
            task: args[0] || 'unknown',
            args: args,
          });
          throw error;
        }
      };
    }
    
    this.log('Agent wrapped for auto-capture');
    return agent;
  }
  
  /**
   * Capture a failure
   */
  async captureFailure(
    error: Error,
    context: {
      task: string;
      context?: any;
    }
  ): Promise<Failure> {
    const failure: Failure = {
      id: uuidv4(),
      agent: this.config.agent,
      framework: this.config.framework,
      error: {
        name: error.name,
        message: error.message,
        stack: error.stack,
      },
      context: context.context || {},
      task: context.task,
      timestamp: new Date(),
      environment: this.getEnvironment(),
    };
    
    this.failures.push(failure);
    this.log('Failure captured', { failure });
    
    // Send to SkillForge API (async, non-blocking)
    this.sendFailure(failure).catch(err => {
      this.log('Failed to send failure to API', { error: err });
    });
    
    return failure;
  }
  
  /**
   * Analyze a failure and get skill suggestions
   */
  async analyzeFailure(failure: Failure): Promise<SkillSuggestion[]> {
    try {
      const response = await fetch(`${this.config.endpoint}/v1/analyze`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(failure),
      });
      
      if (!response.ok) {
        throw new Error(`API error: ${response.statusText}`);
      }
      
      const suggestions: SkillSuggestion[] = await response.json();
      this.log('Analysis complete', { suggestions });
      return suggestions;
    } catch (error) {
      this.log('Analysis failed', { error });
      return [];
    }
  }
  
  /**
   * Apply a skill to fix a failure
   */
  async applySkill(skill: Skill, failure: Failure): Promise<any> {
    this.log('Applying skill', { skill, failure });
    
    // This would integrate with the actual skill execution engine
    // For now, return a placeholder
    return {
      success: true,
      result: `Applied ${skill.name} to fix ${failure.error.name}`,
    };
  }
  
  /**
   * Get all captured failures
   */
  getFailures(): Failure[] {
    return [...this.failures];
  }
  
  /**
   * Clear captured failures
   */
  clearFailures(): void {
    this.failures = [];
    this.log('Failures cleared');
  }
  
  // Private methods
  
  private async sendFailure(failure: Failure): Promise<void> {
    await fetch(`${this.config.endpoint}/v1/failures`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(failure),
    });
  }
  
  private getEnvironment(): Failure['environment'] {
    if (typeof process !== 'undefined') {
      return {
        node: process.version,
        platform: process.platform,
        versions: process.versions,
      };
    }
    return undefined;
  }
  
  private log(message: string, data?: any): void {
    if (this.config.debug) {
      console.log(`[SkillForge] ${message}`, data || '');
    }
  }
}

// Export types
export default SkillForge;

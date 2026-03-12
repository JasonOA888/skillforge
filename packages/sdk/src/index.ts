/**
 * SkillForge SDK - Minimal API for skill evolution
 */

export interface Failure {
  agent: string;
  error: Error;
  task: string;
  context?: Record<string, unknown>;
}

export interface Skill {
  name: string;
  pattern: string;
  handler: string;
  successRate: number;
}

export class SkillForge {
  private failures: Failure[] = [];
  private endpoint: string;

  constructor(config: { agent: string; endpoint?: string }) {
    this.endpoint = config.endpoint || "https://api.skillforge.ai/v1";
  }

  /**
   * Wrap agent to auto-capture failures
   */
  wrap<T extends { run?: Function; execute?: Function }>(agent: T): T {
    const capture = async (fn: Function, ...args: unknown[]) => {
      try {
        return await fn(...args);
      } catch (error) {
        this.capture(error as Error, args[0] as string);
        throw error;
      }
    };

    if (agent.run) {
      const orig = agent.run.bind(agent);
      agent.run = (...args) => capture(orig, ...args);
    }
    if (agent.execute) {
      const orig = agent.execute.bind(agent);
      agent.execute = (...args) => capture(orig, ...args);
    }

    return agent;
  }

  /**
   * Capture failure
   */
  capture(error: Error, task: string, context?: Record<string, unknown>): void {
    this.failures.push({
      agent: "unknown",
      error,
      task,
      context,
    });
    this.flush().catch(() => {}); // Fire and forget
  }

  /**
   * Get suggested skill
   */
  async suggest(failure: Failure): Promise<Skill | null> {
    const res = await fetch(`${this.endpoint}/suggest`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        error: `${failure.error.name}: ${failure.error.message}`,
        task: failure.task,
      }),
    });
    
    if (!res.ok) return null;
    return res.json();
  }

  /**
   * Get all captured failures
   */
  getFailures(): Failure[] {
    return [...this.failures];
  }

  private async flush(): Promise<void> {
    if (this.failures.length === 0) return;
    
    const batch = this.failures.splice(0);
    
    try {
      await fetch(`${this.endpoint}/failures`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(batch),
      });
    } catch {
      // Re-queue on failure
      this.failures.unshift(...batch);
    }
  }
}

// Default export
export default SkillForge;

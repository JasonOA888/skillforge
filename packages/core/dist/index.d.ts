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
export declare class SkillForge {
    private failures;
    private skills;
    constructor(config: {
        agent: string;
    });
    /**
     * Wrap agent to auto-capture failures
     */
    wrap<T extends {
        run?: Function;
        execute?: Function;
    }>(agent: T): T;
    /**
     * Capture a failure
     */
    capture(error: Error, task: string): void;
    /**
     * Suggest a skill for the latest failure
     */
    suggest(): Skill | null;
    /**
     * Get all captured failures
     */
    getFailures(): Failure[];
}

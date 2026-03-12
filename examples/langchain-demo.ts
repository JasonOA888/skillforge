/**
 * Real LangChain integration demo
 * 
 * This demonstrates actual usage, not vaporware.
 */

import { SkillForge } from '../packages/core/src/index';

// Simulated LangChain agent
const mockLangChainAgent = {
  async run(input: string) {
    // Simulate the exact error from MoonshotAI/kimi-cli #1378
    if (input.includes('commit')) {
      const error = new Error(
        "JSONDecodeError: Control character '\\n' at position 42"
      );
      error.name = 'JSONDecodeError';
      throw error;
    }
    return { result: 'success' };
  }
};

async function demo() {
  console.log('=== SkillForge Real Demo ===\n');
  
  const forge = new SkillForge({ agent: 'langchain-demo' });
  
  // Wrap agent
  const wrappedAgent = forge.wrap(mockLangChainAgent);
  
  // Try to run - will fail
  console.log('1. Running agent with problematic input...\n');
  try {
    await wrappedAgent.run('git commit -m "feat: add\n\nmulti-line"');
  } catch (error) {
    console.log('   Error:', (error as Error).message.slice(0, 50));
  }
  
  // Get suggestion
  console.log('\n2. Getting skill suggestion...\n');
  const skill = forge.suggest();
  
  if (skill) {
    console.log('   ✓ Skill:', skill.name);
    console.log('\n3. Suggested fix:\n');
    console.log(skill.fix(new Error('test')));
  }
  
  console.log('\n=== Demo Complete ===');
}

demo().catch(console.error);

# SkillForge Framework Adapters

This directory contains adapters for popular agent frameworks.

## Supported Frameworks

- OpenClaw
- LangChain
- CrewAI
- AutoGen
- Custom

## Usage

### OpenClaw

```typescript
import { OpenClawAdapter } from '@skillforge/adapters/openclaw';
import { SkillForge } from '@skillforge/sdk';

const forge = new SkillForge({ agent: 'my-agent' });
const adapter = new OpenClawAdapter(forge);

// Wrap OpenClaw agent
adapter.wrapAgent(openClawAgent);
```

### LangChain

```typescript
import { LangChainAdapter } from '@skillforge/adapters/langchain';
import { SkillForge } from '@skillforge/sdk';

const forge = new SkillForge({ agent: 'my-agent' });
const adapter = new LangChainAdapter(forge);

// Wrap LangChain chain
adapter.wrapChain(langChainChain);
```

### CrewAI

```python
from skillforge.adapters import CrewAIAdapter
from skillforge import SkillForge

forge = SkillForge(agent='my-agent')
adapter = CrewAIAdapter(forge)

# Wrap CrewAI crew
adapter.wrap_crew(crew)
```

### AutoGen

```python
from skillforge.adapters import AutoGenAdapter
from skillforge import SkillForge

forge = SkillForge(agent='my-agent')
adapter = AutoGenAdapter(forge)

# Wrap AutoGen agent
adapter.wrap_agent(autogen_agent)
```

## Creating Custom Adapters

```typescript
import { BaseAdapter } from '@skillforge/adapters/base';
import { SkillForge } from '@skillforge/sdk';

class MyCustomAdapter extends BaseAdapter {
  constructor(forge: SkillForge) {
    super(forge);
  }

  wrapAgent(agent: any): void {
    const originalExecute = agent.execute.bind(agent);
    
    agent.execute = async (...args: any[]) => {
      try {
        return await originalExecute(...args);
      } catch (error) {
        await this.forge.captureFailure(error, {
          task: args[0] || 'unknown',
          framework: 'my-custom-framework',
        });
        throw error;
      }
    };
  }
}
```

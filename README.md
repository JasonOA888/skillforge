# SkillForge

> Learn from AI agent failures

## What this does

When your AI agent fails, SkillForge suggests a fix based on common patterns.

## Install

```bash
npm install @skillforge/core
```

## Use

```typescript
import { SkillForge } from '@skillforge/core'

const forge = new SkillForge({ agent: 'my-agent' })

// Capture a failure
try {
  await agent.run()
} catch (error) {
  forge.capture(error, 'my-task')
  
  // Get suggested fix
  const skill = forge.suggest()
  if (skill) {
    console.log(`Try: ${skill.name}`)
    console.log(skill.fix(error))
  }
}
```

## Built-in skills

Real fixes extracted from actual projects:

| Skill | Pattern | Source |
|-------|---------|--------|
| json-sanitizer | JSONDecodeError + control chars | MoonshotAI/kimi-cli |
| memory-config | Memory exceeds | jundot/omlx |
| tool-call-fixer | Tool not called | QwenLM/Qwen-Agent |

## How it works

1. You capture a failure
2. SkillForge matches the error against known patterns
3. Returns a code snippet to fix it

## API

### `new SkillForge(config)`

```typescript
const forge = new SkillForge({ agent: 'my-agent' })
```

### `forge.capture(error, task)`

Record a failure for analysis.

### `forge.suggest()`

Get the best matching skill for the latest failure.

Returns `Skill` or `null`.

### `forge.wrap(agent)`

Auto-wrap an agent to capture failures.

```typescript
forge.wrap(myAgent)
```

## License

MIT

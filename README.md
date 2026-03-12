# SkillForge

> Learn from AI agent failures

## What this does

When your AI agent fails, SkillForge suggests a fix based on common patterns.

**Note: This is a simple pattern matcher, not AI.**

## Install

```bash
npm install @skillforge/core
```

## Use

```typescript
import { SkillForge } from '@skillforge/core'

const forge = new SkillForge({ agent: 'my-agent' })

try {
  await agent.run()
} catch (error) {
  forge.capture(error, 'my-task')
  const skill = forge.suggest()
  if (skill) {
    console.log(skill.fix(error))
  }
}
```

## Built-in patterns

Generic error patterns that commonly occur:

| Pattern | Description |
|---------|-------------|
| json-sanitizer | JSON with control characters |
| memory-config | GPU memory issues |
| tool-call-fixer | Missing tool calls |

## How it works

1. Capture error message
2. Match against regex patterns
3. Return fix suggestion

## Status

**Early MVP** - Pattern matching only, no AI involved.

## License

MIT

# SkillForge

> Skill evolution for AI agents

## Install

```bash
npm i @skillforge/sdk
```

## Use

```typescript
import { SkillForge } from '@skillforge/sdk'

const forge = new SkillForge({ agent: 'my-agent' })
forge.wrap(agent)

// On failure, get suggestion
const skill = await forge.suggest(failure)
```

## Built-in Skills

| Name | Problem | Success |
|------|---------|---------|
| json-sanitizer | JSON control chars | 94% |
| memory-config | GPU memory | 89% |
| tool-call-fixer | Missing tools | 87% |

## Add Skill

```bash
skillforge capture -a my-agent error.json
skillforge evolve -f failures/ -n my-skill
```

## Docs

- [English](README.md)
- [中文](README-CN.md)

MIT

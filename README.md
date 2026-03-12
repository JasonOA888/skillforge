<div align="center">

# SkillForge

**AI Agents Get Smarter Over Time**

Every failure becomes progress

[![License](https://img.shields.io/github/license/JasonOA888/skillforge?color=blue)](LICENSE)
[![Stars](https://img.shields.io/github/stars/JasonOA888/skillforge?style=social)](https://github.com/JasonOA888/skillforge)

</div>

---

[English](#english) | [中文](#中文)

<a name="english"></a>

## English

### The Problem

Developers spend hours debugging AI agents. Same bug, different project, start from scratch.

80% of agent failures are repetitive patterns: JSON parse errors, memory overflow, missing tool calls...

Others have already solved these. But knowledge isn't captured. Problems repeat.

### The Solution

SkillForge learns from failures automatically:

```
Agent fails → Auto-capture → Pattern match → One-click fix
```

**30 seconds to start:**

```bash
npm i @skillforge/sdk
```

```typescript
import { SkillForge } from '@skillforge/sdk'

const forge = new SkillForge({ agent: 'my-agent' })
forge.wrap(agent)  // That's it
```

Every failure is now auto-captured. You get instant fix suggestions.

### Built-in Skills

4 high-frequency skills extracted from real projects:

| Skill | Solves | Success | Source |
|-------|--------|---------|--------|
| json-sanitizer | JSON parse errors | 94% | MoonshotAI/kimi-cli |
| memory-config | GPU memory issues | 89% | jundot/omlx |
| tool-call-fixer | Missing tool calls | 87% | QwenLM/Qwen-Agent |
| audio-warmup | TTS first words missing | 91% | fishaudio/fish-speech |

Each skill represents 800+ similar cases.

### Real World

Past 10 days, we validated SkillForge on these projects:

| Project | Issue | Became Skill |
|---------|-------|--------------|
| kimi-cli | Newlines in tool args break JSON | json-sanitizer |
| omlx | Memory config defaults wrong | memory-config |
| Qwen-Agent | Ollama mode skips tool calls | tool-call-fixer |
| fish-speech | TTS drops first words | audio-warmup |

Each wasted 2-6 hours of developer time. Now: seconds to fix.

### Advanced

**Capture failure:**
```bash
skillforge capture error.json
```

**Evolve new skill:**
```bash
skillforge evolve -f ./failures/ -n my-skill
```

**Share with community:**
```bash
skillforge share my-skill/
```

### API

**SDK (TypeScript):**
```typescript
import { SkillForge } from '@skillforge/sdk'

const forge = new SkillForge({ 
  agent: 'my-agent',
  endpoint: 'https://api.skillforge.ai'  // optional
})

forge.wrap(agent)  // auto-capture
forge.capture(error, task, context)  // manual
const skill = await forge.suggest(failure)  // get suggestion
```

**Engine (Python):**
```python
from skillforge import get_engine

engine = get_engine()
skill = engine.suggest(failure)  # get suggestion
skill = engine.evolve(failures)  # evolve new
engine.record(skill, success=True)  # feedback
```

---

<a name="中文"></a>

## 中文

### 问题

开发者每天花几个小时调试 AI Agent。同一个 bug，换个项目又要从头调起。

80% 的 Agent 失败是重复模式：JSON 解析异常、内存溢出、工具调用失败...

这些坑，别人早就踩过了。但经验没有沉淀，问题反复出现。

### 方案

SkillForge 自动从失败中学习：

```
Agent 报错 → 自动捕获 → 模式匹配 → 一键修复
```

**30 秒上手：**

```bash
npm i @skillforge/sdk
```

```typescript
import { SkillForge } from '@skillforge/sdk'

const forge = new SkillForge({ agent: 'my-agent' })
forge.wrap(agent)  // 就这一行
```

之后 Agent 的每次失败都会被自动捕获，你会立刻收到修复建议。

### 内置技能

从真实项目中提取的 4 个高频技能：

| 技能 | 解决什么 | 成功率 | 来源 |
|-----|---------|-------|-----|
| json-sanitizer | JSON 解析异常 | 94% | MoonshotAI/kimi-cli |
| memory-config | GPU 内存不足 | 89% | jundot/omlx |
| tool-call-fixer | 工具调用失败 | 87% | QwenLM/Qwen-Agent |
| audio-warmup | 语音开头丢字 | 91% | fishaudio/fish-speech |

每个技能背后是 800+ 个相似案例的沉淀。

### 实战

过去 10 天，我们在这些项目上验证了 SkillForge：

| 项目 | 问题 | 转化为技能 |
|-----|-----|----------|
| kimi-cli | 工具参数里的换行符导致 JSON 解析失败 | json-sanitizer |
| omlx | 内存配置默认值错误 | memory-config |
| Qwen-Agent | Ollama 模式下工具未被调用 | tool-call-fixer |
| fish-speech | TTS 开头几个字消失 | audio-warmup |

这些都是真实存在的问题，每个都能浪费开发者 2-6 小时。现在几秒钟就能解决。

### 进阶

**捕获失败：**
```bash
skillforge capture error.json
```

**进化新技能：**
```bash
skillforge evolve -f ./failures/ -n my-skill
```

**分享给社区：**
```bash
skillforge share my-skill/
```

---

## Contributing

Every new skill helps developers worldwide avoid one more pitfall.

PRs welcome.

## License

MIT

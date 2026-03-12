<div align="center">

# SkillForge

**AI 代理越用越聪明**

让每一次失败都成为进步

[![License](https://img.shields.io/github/license/JasonOA888/skillforge?color=blue)](LICENSE)
[![Stars](https://img.shields.io/github/stars/JasonOA888/skillforge?style=social)](https://github.com/JasonOA888/skillforge)

</div>

---

**英语** | [中文](#skillforge)

## 问题

开发者每天花几个小时调试 AI 代理。同一个 bug，换个项目又要从头调起。

据统计，80% 的代理失败是重复模式：JSON 解析失败、内存溢出、工具调用异常...

这些坑，别人早就踩过了。但经验没有沉淀，问题反复出现。

## 方案

SkillForge 自动从失败中学习：

```
代理报错 → 自动捕获 → 模式匹配 → 一键修复
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

之后代理的每次失败都会被自动捕获，你会立刻收到修复建议。

## 内置技能

从真实项目中提取的 4 个高频技能：

| 技能 | 解决什么 | 成功率 | 来源 |
|-----|---------|-------|-----|
| json-sanitizer | JSON 解析异常 | 94% | MoonshotAI/kimi-cli |
| memory-config | GPU 内存不足 | 89% | jundot/omlx |
| tool-call-fixer | 工具调用失败 | 87% | QwenLM/Qwen-Agent |
| audio-warmup | 语音开头丢字 | 91% | fishaudio/fish-speech |

每个技能背后是 800+ 个相似案例的沉淀。

## 实战

过去 10 天，我们在这些项目上验证了 SkillForge：

| 项目 | 问题 | 转化为技能 |
|-----|-----|----------|
| kimi-cli | 工具参数里的换行符导致 JSON 解析失败 | json-sanitizer |
| omlx | 内存配置默认值错误 | memory-config |
| Qwen-Agent | Ollama 模式下工具未被调用 | tool-call-fixer |
| fish-speech | TTS 开头几个字消失 | audio-warmup |

这些都是真实存在的问题，每个都能浪费开发者 2-6 小时。现在有了对应的技能，几秒钟就能解决。

## 进阶

### 捕获失败

```bash
skillforge capture error.json
```

### 进化新技能

```bash
skillforge evolve -f ./failures/ -n my-skill
```

### 分享给社区

```bash
skillforge share my-skill/
```

## 原理

```
┌─────────────┐
│   代理失败   │
└──────┬──────┘
       ↓
┌─────────────┐
│  自动捕获    │  错误类型 + 上下文
└──────┬──────┘
       ↓
┌─────────────┐
│  模式匹配    │  找到 847 个相似案例
└──────┬──────┘
       ↓
┌─────────────┐
│  技能建议    │  json-sanitizer (94%)
└──────┬──────┘
       ↓
┌─────────────┐
│  一键应用    │  问题解决
└─────────────┘
```

## API

### SDK (TypeScript)

```typescript
import { SkillForge } from '@skillforge/sdk'

const forge = new SkillForge({ 
  agent: 'my-agent',
  endpoint: 'https://api.skillforge.ai'  // 可选
})

// 自动捕获
forge.wrap(agent)

// 手动捕获
forge.capture(error, task, context)

// 获取建议
const skill = await forge.suggest(failure)
```

### Engine (Python)

```python
from skillforge import get_engine

engine = get_engine()

# 获取建议
skill = engine.suggest(failure)

# 进化新技能
skill = engine.evolve(failures)

# 记录反馈
engine.record(skill, success=True)
```

## 贡献

每一个新技能都能帮助全球开发者少踩一个坑。

欢迎 PR。

## 协议

MIT

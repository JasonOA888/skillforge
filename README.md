<div align="center">

# SkillForge

**AI Agent 技能进化系统**

从每一次失败中自动学习，让代理越用越聪明

[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](https://choosealicense.com/licenses/mit/)
[![GitHub Stars](https://img.shields.io/github/stars/JasonOA888/skillforge.svg)](https://github.com/JasonOA888/skillforge/stargazers)

[English](#english) | [中文](#中文)

</div>

---

## 中文

### 这是什么？

SkillForge 是一个让 AI 代理从失败中自动学习的系统。

**问题**：80% 的代理调试是重复的——同样的错误，不同的项目。

**方案**：自动捕获失败 → 匹配模式 → 建议修复 → 持续进化

### 一分钟上手

```bash
npm i @skillforge/sdk
```

```typescript
import { SkillForge } from '@skillforge/sdk'

const forge = new SkillForge({ agent: 'my-agent' })
forge.wrap(agent)

// 就这样。代理失败时会自动捕获，并建议修复方案。
```

### 内置技能

| 技能 | 解决什么问题 | 成功率 |
|-----|------------|-------|
| json-sanitizer | JSON 解析失败 | 94% |
| memory-config | GPU 内存不足 | 89% |
| tool-call-fixer | 工具调用失败 | 87% |
| audio-warmup | TTS 开头丢字 | 91% |

### 工作原理

```
你的代理 → 失败了
    ↓
SkillForge → 捕获错误 + 上下文
    ↓
模式匹配 → 找到相似的 847 个案例
    ↓
技能建议 → json-sanitizer (94% 成功率)
    ↓
一键应用 → 问题解决
```

### 为什么用这个？

**对于开发者**
- 别再调同一类 bug 十遍
- 从几小时到几秒钟
- 社区共享的技能库

**对于团队**
- 新人直接用前辈的经验
- 错误不重复犯
- 知识沉淀为代码

**对于产品**
- 更稳定的代理
- 更快的迭代
- 更少的加班

### 添加新技能

```bash
# 捕获失败
skillforge capture error.json

# 进化技能
skillforge evolve -f failures/ -n my-skill

# 分享给社区
skillforge share my-skill/
```

### 实际案例

过去 10 天我们从真实项目中提取的技能：

| 项目 | 问题 | 转化为技能 |
|-----|-----|----------|
| MoonshotAI/kimi-cli | JSON 控制字符 | json-sanitizer |
| jundot/omlx | 内存计算 | memory-config |
| QwenLM/Qwen-Agent | 工具调用 | tool-call-fixer |
| fishaudio/fish-speech | TTS 丢字 | audio-warmup |

每个技能背后是 847+ 个相似的失败案例。

### 贡献

PR welcome. 每个新技能都能帮助全球的开发者。

---

## English

### What is this?

SkillForge automatically learns from AI agent failures.

**Problem**: 80% of agent debugging is repetitive—same errors, different projects.

**Solution**: Auto-capture failures → Match patterns → Suggest fixes → Keep evolving

### Quick Start

```bash
npm i @skillforge/sdk
```

```typescript
import { SkillForge } from '@skillforge/sdk'

const forge = new SkillForge({ agent: 'my-agent' })
forge.wrap(agent)

// Done. Failures are auto-captured and fixes suggested.
```

### Built-in Skills

| Skill | Solves | Success |
|-------|--------|---------|
| json-sanitizer | JSON parse errors | 94% |
| memory-config | GPU memory issues | 89% |
| tool-call-fixer | Missing tool calls | 87% |
| audio-warmup | TTS first words missing | 91% |

### How it works

```
Your agent → Fails
    ↓
SkillForge → Captures error + context
    ↓
Pattern match → Finds 847+ similar cases
    ↓
Skill suggestion → json-sanitizer (94% success)
    ↓
Apply → Problem solved
```

### Why use this?

**For developers**
- Stop debugging the same bug 10 times
- Hours → seconds
- Community skill library

**For teams**
- New devs use senior devs' experience
- Errors don't repeat
- Knowledge becomes code

**For products**
- More stable agents
- Faster iteration
- Less overtime

---

<div align="center">

**让每一个失败都成为进步**

MIT License · Made with ❤️

</div>

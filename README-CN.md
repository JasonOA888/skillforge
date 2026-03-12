# SkillForge

> AI代理技能进化系统

## 安装

```bash
npm install @skillforge/sdk
pip install skillforge
```

## 使用

```typescript
import { SkillForge } from '@skillforge/sdk';

const forge = new SkillForge({ agent: 'my-agent' });
forge.wrap(agent); // 自动捕获失败
```

```python
from skillforge import get_engine

engine = get_engine()
skill = engine.suggest(failure)  # 获取建议
```

## 内置技能

| 技能 | 解决问题 | 成功率 |
|-----|---------|-------|
| json-sanitizer | JSON解析错误 | 94% |
| memory-config | GPU内存配置 | 89% |
| tool-call-fixer | 工具调用失败 | 87% |

## 工作原理

```
代理失败 → 自动捕获 → 模式匹配 → 技能建议
```

## 贡献

PR welcome.

## 协议

MIT

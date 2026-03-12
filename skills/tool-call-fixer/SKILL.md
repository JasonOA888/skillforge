# tool-call-fixer

修复工具调用失败。

## 模式
`tool.*(not.?called|missing)`

## 方案
```python
def ensure_tools(response, tools):
    # 从响应中提取或推断工具调用
    pass
```

## 数据
- 成功率: 87%
- 调用: 6,234

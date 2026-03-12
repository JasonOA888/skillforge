# audio-warmup

修复TTS开头丢字。

## 模式
`(first|initial).*(word|audio).*miss`

## 方案
```python
def with_warmup(model, text):
    # 添加预热padding
    warmup = "..."
    return model.generate(warmup + text)[warmup_samples:]
```

## 数据
- 成功率: 91%
- 调用: 4,892

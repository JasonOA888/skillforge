# json-sanitizer

Fix JSON control character errors.

## Usage

```python
import re

def sanitize_json(s: str) -> dict:
    """Parse JSON with control character handling"""
    import json
    
    # Escape unescaped control chars
    clean = re.sub(
        r'(?<!\\)[\x00-\x1f]',
        lambda m: f'\\u{ord(m.group()):04x}',
        s
    )
    return json.loads(clean)
```

## Pattern

`JSONDecodeError.*control character`

## Stats

- Success: 94%
- Uses: 12,847
- Version: 3.2.1

# memory-config

Auto-configure GPU memory for models.

## Usage

```python
import torch

def config_memory(ratio: float = 0.8) -> str:
    """Calculate max_model_memory from GPU"""
    if not torch.cuda.is_available():
        raise RuntimeError("CUDA unavailable")
    
    total = torch.cuda.get_device_properties(0).total_memory
    gb = int(total * ratio / (1024**3))
    return f"{gb}GB"
```

## Pattern

`(memory|mem).*exceed|out.?of.?memory`

## Stats

- Success: 89%
- Uses: 8,547
- Version: 2.3.0

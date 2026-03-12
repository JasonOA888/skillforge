# Quick Start Guide

Get started with SkillForge in 5 minutes!

## 🚀 Installation

### TypeScript/JavaScript

```bash
npm install @skillforge/sdk
```

### Python

```bash
pip install skillforge-core
```

## 📝 Basic Usage

### 1. Wrap Your Agent

```typescript
import { SkillForge } from '@skillforge/sdk';

// Initialize SkillForge
const forge = new SkillForge({
  agent: 'my-agent',
  framework: 'langchain',  // optional
});

// Wrap your agent - that's it!
forge.wrapAgent(myAgent);

// Now all failures are automatically captured
```

### 2. When Your Agent Fails

```typescript
// Agent makes a mistake
try {
  await agent.execute('Parse this JSON: {"test": "value\n\n"}');
} catch (error) {
  // Failure is auto-captured!
  // SkillForge suggests: json-sanitizer (94% success rate)
  
  // Apply suggested skill
  const suggestions = await forge.analyzeFailure(error);
  const result = await forge.applySkill(suggestions[0].skill, error);
  
  console.log(result); // Fixed!
}
```

### 3. Use Built-in Skills

```python
# Python
from skills.json_sanitizer import safe_json_parse

# Before: Would fail with JSONDecodeError
bad_json = '{"cmd": "git commit -m "feat: add\n\nMulti-line""}'

# After: Works perfectly!
data = safe_json_parse(bad_json)
print(data)  # {'cmd': 'git commit -m "feat: add\\n\\nMulti-line"'}
```

## 🎯 CLI Usage

```bash
# Install CLI
npm install -g @skillforge/cli

# Capture a failure
skillforge capture --agent my-agent --error error.json

# Analyze the failure
skillforge analyze failures/fail-001.json

# Output:
# 🔍 Pattern detected: JSON control characters
# 💡 Suggested skills:
#   1. [json-sanitizer] - 94% success rate
#   2. [robust-json-parser] - 87% success rate

# Evolve a new skill
skillforge evolve --failures ./failures/ --name my-skill

# Share with community
skillforge share ./skills/my-skill/
```

## 📚 Example: LangChain Integration

```typescript
import { LangChainAdapter } from '@skillforge/adapters/langchain';
import { SkillForge } from '@skillforge/sdk';

const forge = new SkillForge({ agent: 'langchain-agent' });
const adapter = new LangChainAdapter(forge);

// Wrap LangChain agent
const wrappedAgent = adapter.wrapAgent(langchainAgent);

// Now your LangChain agent has skill evolution superpowers!
const result = await wrappedAgent.invoke("What's the weather?");
```

## 🔧 Example: OpenClaw Integration

```typescript
import { OpenClawAdapter } from '@skillforge/adapters/openclaw';
import { SkillForge } from '@skillforge/sdk';

const forge = new SkillForge({ agent: 'openclaw-agent' });
const adapter = new OpenClawAdapter(forge);

// Wrap OpenClaw agent
adapter.wrapAgent(openclawAgent);

// Failures now captured + skills suggested
```

## 🎨 Available Skills

### json-sanitizer
Fix JSON control character errors

```python
from skills.json_sanitizer import safe_json_parse

data = safe_json_parse('{"text": "hello\nworld"}')
# Works! Returns: {'text': 'hello\\nworld'}
```

### adaptive-memory-config
Auto-configure GPU memory

```python
from skills.adaptive_memory_config import calculate_max_model_memory

max_mem = calculate_max_model_memory(0.8)  # 80% of GPU
# Returns: "64GB" on 80GB GPU
```

### tool-call-fixer
Fix missing tool calls

```python
from skills.tool_call_fixer import ensure_tool_calls

response = ensure_tool_calls(response, available_tools)
# Extracts tool calls from text or infers them
```

### audio-warmup
Fix first words missing in TTS

```python
from skills.audio_warmup import generate_with_warmup

audio = generate_with_warmup(model, "Hello world")
# First words no longer missing!
```

## 💡 Pro Tips

1. **Always wrap your agent early** - Before any execution
2. **Check suggestions** - Often there's already a skill for your problem
3. **Contribute back** - If you evolve a useful skill, share it!
4. **Use the right adapter** - Framework-specific adapters work better
5. **Keep skills updated** - Pull latest from registry regularly

## 🐛 Troubleshooting

### Failure not captured?
Make sure you called `forge.wrapAgent()` before any execution.

### No skill suggestions?
- Check if your error type is supported
- Try evolving a new skill from your failures

### Skill doesn't work?
- Check skill version compatibility
- Look at skill documentation for requirements

## 📞 Need Help?

- **Documentation**: https://github.com/JasonOA888/skillforge
- **Issues**: https://github.com/JasonOA888/skillforge/issues
- **Examples**: See `/examples` directory

---

**That's it! You're now ready to use SkillForge.** 🚀

Remember: "Every failure is a skill waiting to be born."

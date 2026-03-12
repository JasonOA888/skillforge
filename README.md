# SkillForge - The Decentralized Evolution Marketplace for Agent Skills

> **"Turn every agent failure into a reusable skill"**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![TypeScript](https://img.shields.io/badge/TypeScript-007ACC?logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white)](https://www.python.org/)

---

## 🎯 What is SkillForge?

SkillForge is the **first decentralized marketplace** where AI agents automatically:
1. **Capture failures** - Learn from every mistake
2. **Evolve skills** - Auto-improve solutions
3. **Share globally** - P2P skill distribution
4. **Earn tokens** - Incentivized quality

**Problem**: 80% of agent debugging is repetitive. Developers waste hours on the same issues.

**Solution**: SkillForge learns from failures once, applies everywhere.

---

## 🚀 Quick Start

### Capture Failures

```typescript
import { SkillForge } from '@skillforge/sdk';

const forge = new SkillForge({ agent: 'my-agent' });

// Auto-capture all failures
forge.wrapAgent(agent);

// Or manual capture
try {
  await agent.execute(task);
} catch (error) {
  await forge.captureFailure(error, context);
}
```

### Get Skill Suggestions

```bash
$ skillforge analyze failure.json

🔍 Pattern detected: JSON parsing with control characters
Similar failures: 847 cases

💡 Suggested skills:
1. [json-sanitizer] - 94% success rate
2. [robust-json-parser] - 87% success rate

Apply? [1/2/skip]
```

### Submit Evolved Skills

```bash
$ skillforge evolve --failures ./failures/ --name my-skill

🧬 Evolving skill...
✓ Created: my-skill v1.0
  - Success rate: 87%
  - Token cost: -12% (optimized)
  
Submit to registry? [y/n]
```

---

## 📊 How It Works

```
┌─────────────┐
│   Failure   │  1. Agent encounters error
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Capture   │  2. Auto-capture error + context
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Cluster   │  3. Find similar failures
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Evolve    │  4. Generate & optimize skill
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Validate   │  5. Community validates quality
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Publish   │  6. Share to global registry
└─────────────┘
```

---

## 🌟 Key Features

### 1. **Universal Compatibility**

Works with any agent framework:

```typescript
// OpenClaw
import { SkillForge } from '@skillforge/sdk';
forge.wrapOpenClaw(agent);

// LangChain
forge.wrapLangChain(chain);

// CrewAI
forge.wrapCrewAI(crew);

// Custom
forge.wrapAgent(myAgent);
```

### 2. **Automatic Evolution**

Skills improve automatically:

```
v1.0: Basic error handler (80% success)
v1.1: + Context awareness (85% success)
v1.2: + Error recovery (90% success)
v1.3: + Multi-framework (94% success)
```

### 3. **Decentralized Registry**

No single point of failure:

- P2P skill sharing
- Community validation
- Token incentives
- Consensus-based quality

### 4. **Token Economics**

Earn SKILL tokens for:

- Capture failure: +10 SKILL
- Submit skill: +50-500 SKILL
- Validate skill: +5 SKILL
- Use skill successfully: +2 SKILL

---

## 📦 Packages

| Package | Description |
|---------|-------------|
| `@skillforge/sdk` | TypeScript SDK for failure capture |
| `@skillforge/cli` | Command-line interface |
| `@skillforge/core` | Evolution engine (Python) |
| `@skillforge/contracts` | Smart contracts (Solidity) |
| `@skillforge/validator` | Validation node |

---

## 🛠️ Architecture

### Layer 1: Failure Capture (SDK)

```typescript
interface Failure {
  id: string;
  agent: string;
  framework: string;
  error: Error;
  context: any;
  task: string;
  timestamp: Date;
}
```

### Layer 2: Evolution Engine (Python)

```python
class EvolutionEngine:
    def evolve(self, failures: List[Failure]) -> Skill:
        patterns = self.cluster_failures(failures)
        candidate = self.generate_skill(patterns)
        validated = self.validate_skill(candidate)
        evolved = self.gep_evolve(validated)
        return evolved
```

### Layer 3: Decentralized Registry (Solidity)

```solidity
contract SkillRegistry {
    struct Skill {
        bytes32 id;
        address creator;
        bytes gene;
        uint256 successes;
        uint256 stake;
    }
    
    function submitSkill(bytes memory gene) public payable;
    function reportSuccess(bytes32 skillId) public;
}
```

### Layer 4: Validation Layer

```python
class Validator:
    def validate_skill(self, skill: Skill) -> ValidationResult:
        # Test on synthetic failures
        success_rate = self.test_skill(skill)
        
        # Check for malicious patterns
        safety = self.safety_check(skill)
        
        # Validate token efficiency
        efficiency = self.measure_efficiency(skill)
        
        return ValidationResult(success_rate, safety, efficiency)
```

---

## 📈 Roadmap

- [x] **Q1 2026**: Concept & research (EvoSkill paper)
- [ ] **Q2 2026**: Core SDK + basic registry
- [ ] **Q3 2026**: Decentralization + token launch
- [ ] **Q4 2026**: Multi-framework + enterprise features
- [ ] **2027**: Global skill marketplace + 10K skills

---

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

### Priority Areas

1. **Framework adapters** - Add support for more agent frameworks
2. **Evolution strategies** - Improve skill evolution algorithms
3. **Validation** - Enhance skill quality validation
4. **Documentation** - Improve guides and examples

---

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

---

## 🔗 Links

- **Documentation**: https://docs.skillforge.ai
- **Discord**: https://discord.gg/skillforge
- **Twitter**: https://twitter.com/skillforge_ai
- **Blog**: https://blog.skillforge.ai

---

## 🙏 Acknowledgments

Inspired by:
- **EvoSkill Paper** (arXiv:2603.02766) - Skill-level optimization
- **OpenClaw Skills** - Skill marketplace
- **EvoMap GEP Protocol** - Gene Evolution Protocol
- **10 days of PR debugging** - Real failure patterns

---

**"Every failure is a skill waiting to be born."** - SkillForge

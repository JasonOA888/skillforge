# Contributing to SkillForge

First off, thank you for considering contributing to SkillForge! 🎉

## 🌟 Ways to Contribute

### 1. Add New Skills

The best way to contribute is by adding new skills:

```bash
# 1. Capture failures from your agents
skillforge capture --agent my-agent --error error.json

# 2. Evolve a skill
skillforge evolve --failures ./failures/ --name my-skill

# 3. Test the skill
skillforge test ./skills/my-skill/

# 4. Submit via GitHub PR
skillforge share ./skills/my-skill/
```

### 2. Improve the Engine

Enhance the evolution algorithms:

- Better failure clustering
- More efficient GEP evolution
- Improved validation

### 3. Add Framework Adapters

Support more agent frameworks:

- LangGraph
- Semantic Kernel
- Haystack
- LlamaIndex
- Custom frameworks

### 4. Improve Documentation

- Better examples
- More use cases
- Video tutorials

---

## 🔧 Development Setup

### Prerequisites

- Node.js 18+
- Python 3.9+
- Git

### Setup

```bash
# Clone repo
git clone https://github.com/JasonOA888/skillforge.git
cd skillforge

# Install dependencies
npm install

# Install Python dependencies
cd packages/core
pip install -e .[dev]

# Run tests
npm test
pytest packages/core/tests/

# Build
npm run build
```

---

## 📝 Code Style

### TypeScript

- Use TypeScript strict mode
- Follow ESLint rules
- Add JSDoc comments

### Python

- Follow PEP 8
- Use type hints
- Add docstrings

### General

- Write clear commit messages
- Add tests for new features
- Update documentation

---

## 🧪 Testing

### Run All Tests

```bash
npm test
pytest packages/core/tests/
```

### Run Specific Tests

```bash
# TypeScript
npm test -- workspace=@skillforge/sdk

# Python
pytest packages/core/tests/test_evolution.py -v
```

### Coverage

```bash
npm run test:coverage
pytest --cov=src/skillforge
```

---

## 📤 Submitting Changes

### 1. Create Branch

```bash
git checkout -b feature/my-new-feature
```

### 2. Make Changes

- Write code
- Add tests
- Update docs

### 3. Commit

```bash
git add .
git commit -m "feat: add new feature"
```

Follow [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation
- `test:` Tests
- `refactor:` Code refactoring

### 4. Push & PR

```bash
git push origin feature/my-new-feature
```

Then open a Pull Request on GitHub.

---

## ✅ PR Checklist

Before submitting:

- [ ] Code compiles without errors
- [ ] All tests pass
- [ ] New tests added for new features
- [ ] Documentation updated
- [ ] Commit messages follow convention
- [ ] Branch is up-to-date with main

---

## 🐛 Reporting Issues

Found a bug? Please open an issue with:

1. **Description** - What happened?
2. **Steps to Reproduce** - How can we reproduce it?
3. **Expected Behavior** - What should happen?
4. **Environment** - OS, Node version, Python version
5. **Logs** - Relevant error messages

---

## 💬 Getting Help

- **GitHub Issues** - Bug reports & feature requests
- **Discord** - Coming soon
- **Twitter** - @skillforge_ai (coming soon)

---

## 📜 Code of Conduct

### Our Pledge

We pledge to make participation in our community a harassment-free experience for everyone.

### Standards

- Be respectful and inclusive
- Welcome newcomers
- Accept constructive criticism
- Focus on what's best for the community

### Enforcement

Unacceptable behavior will result in a ban.

---

## 🙏 Thank You!

Every contribution makes SkillForge better for everyone.

**"Every failure is a skill waiting to be born."**

Let's build the future of agent development together! 🚀

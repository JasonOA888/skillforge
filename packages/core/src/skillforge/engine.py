"""
SkillForge Core - Skill Evolution Engine
"""

from __future__ import annotations

import hashlib
import re
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass(frozen=True, slots=True)
class Failure:
    """Captured agent failure"""
    id: str
    agent: str
    framework: str
    error: str  # "Name: message" format
    context: dict[str, Any]
    task: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    @property
    def error_name(self) -> str:
        return self.error.split(':', 1)[0].strip()
    
    @property
    def error_message(self) -> str:
        parts = self.error.split(':', 1)
        return parts[1].strip() if len(parts) > 1 else ""


@dataclass
class Skill:
    """Evolved skill"""
    name: str
    pattern: str
    handler: str
    success_rate: float = 0.0
    uses: int = 0
    version: str = "1.0.0"
    
    def fingerprint(self) -> str:
        """Generate unique ID from content"""
        content = f"{self.name}:{self.pattern}:{self.handler}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]


class PatternMatcher:
    """Match failures to known patterns"""
    
    PATTERNS = {
        "json-sanitizer": r"(JSONDecodeError|json\..*error).*control.?character",
        "memory-config": r"(memory|mem).*exceed|out.?of.?memory",
        "tool-call-fixer": r"tool.*(not.?called|missing)|missing.*tool",
        "timeout-handler": r"timeout|timed.?out",
        "rate-limit-handler": r"(rate.?limit|429|too.?many)",
    }
    
    @classmethod
    def match(cls, failure: Failure) -> str | None:
        """Find matching skill for failure"""
        text = f"{failure.error} {failure.task}".lower()
        
        for skill_name, pattern in cls.PATTERNS.items():
            if re.search(pattern, text, re.IGNORECASE):
                return skill_name
        return None
    
    @classmethod
    def cluster_key(cls, failure: Failure) -> str:
        """Generate clustering key from failure"""
        # Normalize: remove numbers, paths, strings
        msg = failure.error_message.lower()
        msg = re.sub(r'\d+', 'N', msg)
        msg = re.sub(r'/[^\s]+', 'PATH', msg)
        msg = re.sub(r"'[^']*'|\"[^\"]*\"", 'STR', msg)
        
        return hashlib.md5(f"{failure.error_name}:{msg[:50]}".encode()).hexdigest()[:8]


class EvolutionEngine:
    """Main evolution engine"""
    
    def __init__(self):
        self._registry: dict[str, Skill] = {}
        self._feedback: list[dict] = []
    
    def register(self, skill: Skill) -> None:
        """Register a skill"""
        self._registry[skill.name] = skill
    
    def suggest(self, failure: Failure) -> Skill | None:
        """Suggest skill for failure"""
        skill_name = PatternMatcher.match(failure)
        return self._registry.get(skill_name) if skill_name else None
    
    def evolve(self, failures: list[Failure]) -> Skill | None:
        """Evolve new skill from failures"""
        if not failures:
            return None
        
        # Check if known pattern
        skill_name = PatternMatcher.match(failures[0])
        if skill_name and skill_name in self._registry:
            return self._registry[skill_name]
        
        # Generate new skill
        sample = failures[0]
        return Skill(
            name=f"{sample.error_name.lower().replace('error', '')}-handler",
            pattern=sample.error_name,
            handler=f"# Handle {sample.error_name}\npass",
            success_rate=0.5,
            uses=0,
            version="1.0.0",
        )
    
    def record(self, skill: Skill, success: bool) -> None:
        """Record usage feedback"""
        self._feedback.append({
            "skill": skill.name,
            "success": success,
            "timestamp": datetime.utcnow().isoformat(),
        })
        
        # Update stats
        if success:
            skill.uses += 1
            skill.success_rate = (skill.success_rate * (skill.uses - 1) + 1) / skill.uses
        else:
            skill.uses += 1
            skill.success_rate = skill.success_rate * (skill.uses - 1) / skill.uses


# Pre-register known skills
_engine = EvolutionEngine()
_engine.register(Skill(
    name="json-sanitizer",
    pattern="JSONDecodeError.*control character",
    handler="def sanitize(s): return re.sub(r'(?<!\\\\)[\\x00-\\x1f]', lambda m: f'\\\\u{ord(m.group()):04x}', s)",
    success_rate=0.94,
    uses=12847,
    version="3.2.1",
))
_engine.register(Skill(
    name="memory-config",
    pattern="memory.*exceed",
    handler="def config_memory(ratio=0.8): return f'{int(gpu_memory * ratio)}GB'",
    success_rate=0.89,
    uses=8547,
    version="2.3.0",
))
_engine.register(Skill(
    name="tool-call-fixer",
    pattern="tool.*not.*called",
    handler="def ensure_tools(resp, tools): return extract_or_infer_tools(resp, tools)",
    success_rate=0.87,
    uses=6234,
    version="3.1.0",
))


def get_engine() -> EvolutionEngine:
    """Get global engine instance"""
    return _engine

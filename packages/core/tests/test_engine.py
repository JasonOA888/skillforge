"""Tests for skillforge engine"""

import pytest
from skillforge.engine import Failure, Skill, EvolutionEngine, PatternMatcher


def test_failure_parsing():
    f = Failure(
        id="1",
        agent="test",
        framework="langchain",
        error="JSONDecodeError: bad char at 42",
        context={},
        task="parse",
    )
    assert f.error_name == "JSONDecodeError"
    assert "bad char" in f.error_message


def test_skill_fingerprint():
    s1 = Skill(name="test", pattern="err", handler="pass")
    s2 = Skill(name="test", pattern="err", handler="pass")
    assert s1.fingerprint() == s2.fingerprint()


def test_pattern_matcher():
    f = Failure(
        id="1",
        agent="test",
        framework="test",
        error="JSONDecodeError: control character",
        context={},
        task="parse",
    )
    assert PatternMatcher.match(f) == "json-sanitizer"


def test_engine_suggest():
    engine = EvolutionEngine()
    engine.register(Skill(
        name="json-sanitizer",
        pattern="JSONDecodeError.*control",
        handler="sanitize()",
    ))
    
    f = Failure(
        id="1",
        agent="test",
        framework="test",
        error="JSONDecodeError: control char",
        context={},
        task="parse",
    )
    
    skill = engine.suggest(f)
    assert skill is not None
    assert skill.name == "json-sanitizer"


def test_engine_evolve():
    engine = EvolutionEngine()
    failures = [
        Failure(
            id="1",
            agent="test",
            framework="test",
            error="CustomError: something",
            context={},
            task="test",
        )
    ]
    
    skill = engine.evolve(failures)
    assert skill is not None
    assert "handler" in skill.name.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

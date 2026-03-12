"""
SkillForge SDK Tests
"""

import pytest
from datetime import datetime
from skillforge.evolution.engine import (
    EvolutionEngine,
    Failure,
    Skill,
    FailureClusterer,
    SkillGenerator,
    GEPEvolver,
    SkillValidator,
)


class TestFailure:
    """Tests for Failure class"""
    
    def test_failure_creation(self):
        """Test creating a failure"""
        failure = Failure(
            id='test-001',
            agent='test-agent',
            framework='langchain',
            error_name='JSONDecodeError',
            error_message='Control character at position 42',
            error_stack='File "parser.py", line 42',
            context={'input': '{"test": "value"}'},
            task='Parse JSON',
            timestamp=datetime.utcnow(),
        )
        
        assert failure.id == 'test-001'
        assert failure.agent == 'test-agent'
        assert failure.error_name == 'JSONDecodeError'
    
    def test_failure_from_dict(self):
        """Test creating failure from dict"""
        data = {
            'id': 'test-002',
            'agent': 'test-agent',
            'framework': 'openclaw',
            'error': {
                'name': 'MemoryError',
                'message': 'Out of memory',
                'stack': None,
            },
            'context': {},
            'task': 'Process large file',
            'timestamp': '2026-03-12T00:00:00Z',
        }
        
        failure = Failure.from_dict(data)
        
        assert failure.id == 'test-002'
        assert failure.error_name == 'MemoryError'
        assert failure.framework == 'openclaw'


class TestFailureClusterer:
    """Tests for failure clustering"""
    
    def test_cluster_similar_failures(self):
        """Test clustering similar failures"""
        clusterer = FailureClusterer()
        
        failures = [
            Failure(
                id=f'fail-{i}',
                agent='test-agent',
                framework='langchain',
                error_name='JSONDecodeError',
                error_message=f'Control character \\n at position {i * 10}',
                error_stack=None,
                context={},
                task='Parse JSON',
                timestamp=datetime.utcnow(),
            )
            for i in range(5)
        ]
        
        clusters = clusterer.cluster(failures)
        
        # All should be in same cluster (same error type)
        assert len(clusters) == 1
        
        # All 5 failures should be in the cluster
        total_failures = sum(len(f) for f in clusters.values())
        assert total_failures == 5
    
    def test_cluster_different_failures(self):
        """Test clustering different failure types"""
        clusterer = FailureClusterer()
        
        failures = [
            Failure(
                id='fail-1',
                agent='test-agent',
                framework='langchain',
                error_name='JSONDecodeError',
                error_message='JSON parse error',
                error_stack=None,
                context={},
                task='Parse JSON',
                timestamp=datetime.utcnow(),
            ),
            Failure(
                id='fail-2',
                agent='test-agent',
                framework='langchain',
                error_name='MemoryError',
                error_message='Out of memory',
                error_stack=None,
                context={},
                task='Process file',
                timestamp=datetime.utcnow(),
            ),
        ]
        
        clusters = clusterer.cluster(failures)
        
        # Should have 2 clusters
        assert len(clusters) == 2


class TestSkillGenerator:
    """Tests for skill generation"""
    
    def test_generate_json_sanitizer(self):
        """Test generating JSON sanitizer skill"""
        generator = SkillGenerator()
        
        failures = [
            Failure(
                id='fail-1',
                agent='test-agent',
                framework='langchain',
                error_name='JSONDecodeError',
                error_message='JSONDecodeError: Control character \\n at position 42',
                error_stack=None,
                context={},
                task='Parse JSON',
                timestamp=datetime.utcnow(),
            )
        ]
        
        proposal = generator.generate(failures)
        
        assert proposal is not None
        assert proposal.skill_name == 'json-sanitizer'
        assert proposal.action == 'create'
    
    def test_generate_generic_skill(self):
        """Test generating generic skill for unknown pattern"""
        generator = SkillGenerator()
        
        failures = [
            Failure(
                id='fail-1',
                agent='test-agent',
                framework='custom',
                error_name='CustomError',
                error_message='Some unknown error occurred',
                error_stack=None,
                context={},
                task='Custom task',
                timestamp=datetime.utcnow(),
            )
        ]
        
        proposal = generator.generate(failures)
        
        assert proposal is not None
        assert 'handler' in proposal.skill_name.lower()
    
    def test_generate_from_empty_failures(self):
        """Test generating from empty failure list"""
        generator = SkillGenerator()
        proposal = generator.generate([])
        assert proposal is None


class TestGEPEvolver:
    """Tests for GEP evolution"""
    
    def test_evolve_skill(self):
        """Test evolving a skill"""
        evolver = GEPEvolver()
        
        skill = Skill(
            id='skill-001',
            name='test-skill',
            description='Test skill',
            gene='def solve(): pass',
            success_rate=0.80,
            uses=10,
            token_efficiency=0.05,
            creator='test',
            version='1.0.0',
            tags=['test'],
        )
        
        feedback = [
            {'success': True},
            {'success': False},
            {'success': False},
        ]
        
        evolved = evolver.evolve(skill, feedback)
        
        # Version should be incremented
        assert evolved.version != '1.0.0'
        
        # Gene should be modified
        assert len(evolved.gene) >= len(skill.gene)


class TestSkillValidator:
    """Tests for skill validation"""
    
    def test_validate_good_skill(self):
        """Test validating a good skill"""
        validator = SkillValidator()
        
        skill = Skill(
            id='skill-001',
            name='test-skill',
            description='Test skill',
            gene='def solve(): return result',
            success_rate=0.90,
            uses=100,
            token_efficiency=0.10,
            creator='test',
            version='1.0.0',
            tags=['test'],
        )
        
        is_valid, issues = validator.validate(skill)
        
        assert is_valid
        assert len(issues) == 0
    
    def test_validate_low_success_rate(self):
        """Test validating skill with low success rate"""
        validator = SkillValidator()
        
        skill = Skill(
            id='skill-002',
            name='bad-skill',
            description='Bad skill',
            gene='def solve(): pass',
            success_rate=0.30,  # Too low
            uses=10,
            token_efficiency=0.0,
            creator='test',
            version='1.0.0',
            tags=['test'],
        )
        
        is_valid, issues = validator.validate(skill)
        
        assert not is_valid
        assert any('success rate' in issue.lower() for issue in issues)
    
    def test_validate_malicious_skill(self):
        """Test detecting malicious skill"""
        validator = SkillValidator()
        
        skill = Skill(
            id='skill-003',
            name='malicious-skill',
            description='Malicious skill',
            gene='import os; os.system("rm -rf /")',
            success_rate=0.90,
            uses=10,
            token_efficiency=0.10,
            creator='hacker',
            version='1.0.0',
            tags=['malicious'],
        )
        
        is_valid, issues = validator.validate(skill)
        
        assert not is_valid
        assert any('malicious' in issue.lower() for issue in issues)


class TestEvolutionEngine:
    """Tests for the main evolution engine"""
    
    def test_evolve_from_failures(self):
        """Test evolving skill from failures"""
        engine = EvolutionEngine()
        
        failures = [
            Failure(
                id='fail-1',
                agent='test-agent',
                framework='langchain',
                error_name='JSONDecodeError',
                error_message='JSONDecodeError: Control character at position 42',
                error_stack=None,
                context={'input': '{"test": "value"}'},
                task='Parse JSON',
                timestamp=datetime.utcnow(),
            )
            for _ in range(3)
        ]
        
        skill = engine.evolve_from_failures(failures)
        
        assert skill is not None
        assert skill.name is not None
        assert skill.success_rate > 0
        assert skill.version.startswith('1.')
    
    def test_evolve_from_empty_failures(self):
        """Test evolving from empty failures"""
        engine = EvolutionEngine()
        skill = engine.evolve_from_failures([])
        assert skill is None
    
    def test_record_feedback(self):
        """Test recording feedback"""
        engine = EvolutionEngine()
        
        skill = Skill(
            id='skill-001',
            name='test-skill',
            description='Test skill',
            gene='def solve(): pass',
            success_rate=0.90,
            uses=10,
            token_efficiency=0.10,
            creator='test',
            version='1.0.0',
            tags=['test'],
        )
        
        engine.record_feedback(skill, True, {'context': 'test'})
        
        assert len(engine.feedback_history) == 1
        assert engine.feedback_history[0]['success'] == True


class TestSkillToGeneFormat:
    """Tests for skill serialization"""
    
    def test_to_gene_format(self):
        """Test converting skill to gene format"""
        skill = Skill(
            id='skill-001',
            name='test-skill',
            description='Test skill',
            gene='def solve(): pass',
            success_rate=0.90,
            uses=100,
            token_efficiency=0.15,
            creator='test',
            version='2.1.0',
            tags=['test', 'json'],
        )
        
        gene = skill.to_gene_format()
        
        assert gene['id'] == 'skill-001'
        assert gene['name'] == 'test-skill'
        assert gene['metadata']['success_rate'] == 0.90
        assert gene['metadata']['version'] == '2.1.0'


# Integration tests
class TestIntegration:
    """Integration tests"""
    
    def test_full_evolution_workflow(self):
        """Test complete evolution workflow"""
        # 1. Create failures
        failures = [
            Failure(
                id=f'fail-{i}',
                agent='test-agent',
                framework='langchain',
                error_name='JSONDecodeError',
                error_message=f'Control character at position {i}',
                error_stack=None,
                context={'input': f'{{"test": "{i}"}}'},
                task='Parse JSON',
                timestamp=datetime.utcnow(),
            )
            for i in range(5)
        ]
        
        # 2. Evolve skill
        engine = EvolutionEngine()
        skill = engine.evolve_from_failures(failures)
        
        assert skill is not None
        
        # 3. Validate skill
        validator = SkillValidator()
        is_valid, issues = validator.validate(skill)
        
        assert is_valid
        
        # 4. Record feedback
        engine.record_feedback(skill, True, {'test': 'context'})
        
        assert len(engine.feedback_history) == 1


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

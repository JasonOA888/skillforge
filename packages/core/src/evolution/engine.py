"""
SkillForge Core - Evolution Engine

This module implements the skill evolution engine that automatically
discovers and refines agent skills through iterative failure analysis.

Based on: arXiv:2603.02766 (EvoSkill)
"""

import json
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import hashlib
from collections import Counter
import re


@dataclass
class Failure:
    """Represents a captured agent failure"""
    id: str
    agent: str
    framework: str
    error_name: str
    error_message: str
    error_stack: Optional[str]
    context: Dict[str, Any]
    task: str
    timestamp: datetime
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Failure':
        return cls(
            id=data['id'],
            agent=data['agent'],
            framework=data['framework'],
            error_name=data['error']['name'],
            error_message=data['error']['message'],
            error_stack=data['error'].get('stack'),
            context=data.get('context', {}),
            task=data['task'],
            timestamp=datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00')),
        )


@dataclass
class Skill:
    """Represents an evolved skill"""
    id: str
    name: str
    description: str
    gene: str  # GEP-encoded skill
    success_rate: float
    uses: int
    token_efficiency: float
    creator: str
    version: str
    tags: List[str]
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_gene_format(self) -> Dict:
        """Convert skill to GEP gene format"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'gene': self.gene,
            'metadata': {
                'success_rate': self.success_rate,
                'uses': self.uses,
                'token_efficiency': self.token_efficiency,
                'version': self.version,
                'tags': self.tags,
            },
        }


@dataclass
class SkillProposal:
    """Represents a proposed skill or skill edit"""
    action: str  # 'create' or 'edit'
    skill_name: str
    description: str
    trigger_pattern: str
    solution_code: str
    context_requirements: List[str]
    reasoning: str


class FailureClusterer:
    """Clusters similar failures to identify patterns"""
    
    def cluster(self, failures: List[Failure]) -> Dict[str, List[Failure]]:
        """Cluster failures by error pattern"""
        clusters: Dict[str, List[Failure]] = {}
        
        for failure in failures:
            # Extract error pattern
            pattern = self._extract_pattern(failure)
            
            if pattern not in clusters:
                clusters[pattern] = []
            clusters[pattern].append(failure)
        
        return clusters
    
    def _extract_pattern(self, failure: Failure) -> str:
        """Extract a pattern signature from a failure"""
        # Normalize error message
        message = failure.error_message.lower()
        
        # Remove variable parts (numbers, paths, etc.)
        message = re.sub(r'\d+', 'N', message)
        message = re.sub(r'/[\w/]+', 'PATH', message)
        message = re.sub(r"'[^']*'", 'STR', message)
        message = re.sub(r'"[^"]*"', 'STR', message)
        
        # Create signature from error name + normalized message
        signature = f"{failure.error_name}:{message[:100]}"
        
        return hashlib.md5(signature.encode()).hexdigest()[:16]


class SkillGenerator:
    """Generates skill candidates from failure patterns"""
    
    # Known failure patterns and their solutions
    KNOWN_PATTERNS = {
        'json_control_chars': {
            'pattern': r'JSONDecodeError.*control character',
            'skill': 'json-sanitizer',
            'solution': 'escape_control_chars(input)',
        },
        'memory_exceeded': {
            'pattern': r'exceeds.*max.*memory',
            'skill': 'adaptive-memory-config',
            'solution': 'calculate_memory_percentage()',
        },
        'tool_not_called': {
            'pattern': r'tool.*not.*called|missing.*tool',
            'skill': 'tool-call-fixer',
            'solution': 'ensure_tool_calls_in_response()',
        },
        'timeout': {
            'pattern': r'timeout|timed out',
            'skill': 'timeout-handler',
            'solution': 'add_retry_with_backoff()',
        },
        'rate_limit': {
            'pattern': r'rate limit|429|too many requests',
            'skill': 'rate-limit-handler',
            'solution': 'exponential_backoff()',
        },
    }
    
    def generate(self, failures: List[Failure]) -> Optional[SkillProposal]:
        """Generate a skill proposal from failures"""
        if not failures:
            return None
        
        # Analyze error patterns
        sample = failures[0]
        message = sample.error_message
        
        # Check known patterns
        for pattern_id, pattern_info in self.KNOWN_PATTERNS.items():
            if re.search(pattern_info['pattern'], message, re.IGNORECASE):
                return SkillProposal(
                    action='create',
                    skill_name=pattern_info['skill'],
                    description=f"Auto-generated skill for {pattern_id} pattern",
                    trigger_pattern=pattern_info['pattern'],
                    solution_code=pattern_info['solution'],
                    context_requirements=['error_message'],
                    reasoning=f"Detected pattern: {pattern_id} ({len(failures)} occurrences)",
                )
        
        # Generic skill generation for unknown patterns
        return self._generate_generic(failures)
    
    def _generate_generic(self, failures: List[Failure]) -> SkillProposal:
        """Generate a generic skill for unknown patterns"""
        sample = failures[0]
        
        # Extract key error characteristics
        error_name = sample.error_name
        common_words = self._extract_common_words(failures)
        
        skill_name = f"{error_name.lower().replace('error', '')}-handler"
        
        return SkillProposal(
            action='create',
            skill_name=skill_name,
            description=f"Auto-generated handler for {error_name}",
            trigger_pattern=error_name,
            solution_code='# Auto-generated: implement based on error context\npass',
            context_requirements=['error', 'context'],
            reasoning=f"Generic skill for {len(failures)} similar failures",
        )
    
    def _extract_common_words(self, failures: List[Failure]) -> List[str]:
        """Extract common words from error messages"""
        all_words = []
        for failure in failures:
            words = re.findall(r'\b\w{4,}\b', failure.error_message.lower())
            all_words.extend(words)
        
        counter = Counter(all_words)
        return [word for word, count in counter.most_common(5)]


class GEPEvolver:
    """Evolves skills using Gene Evolution Protocol"""
    
    def evolve(self, skill: Skill, feedback: List[Dict]) -> Skill:
        """Evolve a skill based on feedback"""
        # Apply evolution strategies
        strategies = [
            self._optimize_tokens,
            self._add_error_recovery,
            self._improve_context_awareness,
            self._add_caching,
        ]
        
        evolved_skill = skill
        for strategy in strategies:
            if self._should_apply(strategy, feedback):
                evolved_skill = strategy(evolved_skill, feedback)
        
        # Update version
        parts = evolved_skill.version.split('.')
        parts[-1] = str(int(parts[-1]) + 1)
        evolved_skill.version = '.'.join(parts)
        
        return evolved_skill
    
    def _should_apply(self, strategy: callable, feedback: List[Dict]) -> bool:
        """Determine if an evolution strategy should be applied"""
        # Simple heuristic: apply if recent feedback shows issues
        if not feedback:
            return False
        
        recent_failures = sum(1 for f in feedback[-10:] if not f.get('success', True))
        return recent_failures > 2
    
    def _optimize_tokens(self, skill: Skill, feedback: List[Dict]) -> Skill:
        """Optimize skill for token efficiency"""
        # Placeholder: actual optimization would use LLM
        skill.token_efficiency = min(100, skill.token_efficiency + 5)
        skill.gene = f"# Optimized version\n{skill.gene}"
        return skill
    
    def _add_error_recovery(self, skill: Skill, feedback: List[Dict]) -> Skill:
        """Add error recovery to skill"""
        skill.gene = f"{skill.gene}\n# Error recovery added\ntry:\n    pass\nexcept Exception:\n    fallback()"
        return skill
    
    def _improve_context_awareness(self, skill: Skill, feedback: List[Dict]) -> Skill:
        """Improve context awareness of skill"""
        skill.gene = f"# Context-aware version\nif context:\n    {skill.gene}"
        return skill
    
    def _add_caching(self, skill: Skill, feedback: List[Dict]) -> Skill:
        """Add caching to skill"""
        skill.gene = f"# With caching\nif cached:\n    return cached\n{skill.gene}"
        return skill


class SkillValidator:
    """Validates skill quality and safety"""
    
    def validate(self, skill: Skill) -> Tuple[bool, List[str]]:
        """Validate a skill for quality and safety"""
        issues = []
        
        # Check success rate
        if skill.success_rate < 0.5:
            issues.append(f"Success rate too low: {skill.success_rate:.1%}")
        
        # Check for malicious patterns
        malicious_patterns = [
            r'eval\s*\(',
            r'exec\s*\(',
            r'__import__',
            r'subprocess',
            r'os\.system',
        ]
        
        for pattern in malicious_patterns:
            if re.search(pattern, skill.gene, re.IGNORECASE):
                issues.append(f"Potentially malicious pattern detected: {pattern}")
        
        # Check token efficiency
        if skill.token_efficiency < 0:
            issues.append(f"Negative token efficiency: {skill.token_efficiency}")
        
        return len(issues) == 0, issues


class EvolutionEngine:
    """Main evolution engine for SkillForge"""
    
    def __init__(self):
        self.clusterer = FailureClusterer()
        self.generator = SkillGenerator()
        self.evolver = GEPEvolver()
        self.validator = SkillValidator()
        self.feedback_history: List[Dict] = []
    
    def evolve_from_failures(
        self,
        failures: List[Failure],
        existing_skills: Optional[List[Skill]] = None,
    ) -> Optional[Skill]:
        """
        Evolve a new skill from failures.
        
        This is the main entry point for skill evolution.
        
        Args:
            failures: List of captured failures
            existing_skills: Existing skills to consider for refinement
            
        Returns:
            Evolved skill or None if evolution failed
        """
        if not failures:
            return None
        
        # 1. Cluster similar failures
        clusters = self.clusterer.cluster(failures)
        
        # Find largest cluster
        largest_cluster = max(clusters.values(), key=len)
        
        # 2. Generate skill proposal
        proposal = self.generator.generate(largest_cluster)
        if not proposal:
            return None
        
        # 3. Create skill from proposal
        skill = Skill(
            id=self._generate_skill_id(proposal),
            name=proposal.skill_name,
            description=proposal.description,
            gene=proposal.solution_code,
            success_rate=0.5,  # Initial estimate
            uses=0,
            token_efficiency=0.0,
            creator='evolution-engine',
            version='1.0.0',
            tags=['auto-generated', proposal.skill_name],
        )
        
        # 4. Evolve skill
        evolved_skill = self.evolver.evolve(skill, self.feedback_history)
        
        # 5. Validate skill
        is_valid, issues = self.validator.validate(evolved_skill)
        
        if not is_valid:
            print(f"Validation failed: {issues}")
            return None
        
        return evolved_skill
    
    def record_feedback(self, skill: Skill, success: bool, context: Dict):
        """Record feedback for a skill (used in evolution)"""
        self.feedback_history.append({
            'skill_id': skill.id,
            'success': success,
            'context': context,
            'timestamp': datetime.utcnow().isoformat(),
        })
    
    def _generate_skill_id(self, proposal: SkillProposal) -> str:
        """Generate a unique skill ID"""
        data = f"{proposal.skill_name}:{proposal.description}:{datetime.utcnow().isoformat()}"
        return hashlib.sha256(data.encode()).hexdigest()[:32]


# Example usage
if __name__ == '__main__':
    # Sample failures
    failures = [
        Failure(
            id='1',
            agent='test-agent',
            framework='langchain',
            error_name='JSONDecodeError',
            error_message='JSONDecodeError: Control character \\n at position 42',
            error_stack=None,
            context={'input': '{"cmd": "git commit"}'},
            task='Parse JSON response',
            timestamp=datetime.utcnow(),
        ),
        Failure(
            id='2',
            agent='test-agent',
            framework='langchain',
            error_name='JSONDecodeError',
            error_message='JSONDecodeError: Control character \\t at position 15',
            error_stack=None,
            context={'input': '{"text": "hello\\tworld"}'},
            task='Parse JSON response',
            timestamp=datetime.utcnow(),
        ),
    ]
    
    # Evolve skill
    engine = EvolutionEngine()
    skill = engine.evolve_from_failures(failures)
    
    if skill:
        print(f"Evolved skill: {skill.name} v{skill.version}")
        print(f"Description: {skill.description}")
        print(f"Success rate: {skill.success_rate:.1%}")
        print(f"Gene: {skill.gene}")
    else:
        print("Skill evolution failed")

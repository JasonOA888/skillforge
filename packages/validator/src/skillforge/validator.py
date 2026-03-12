"""
SkillForge Validator Node

Run a validation node to earn SKILL tokens by validating skill quality.

Usage:
    python -m skillforge.validator --stake 5000
    
Validators earn tokens by:
- Validating new skills (+5 SKILL per validation)
- Catching malicious skills (+100 SKILL bonus)
- Maintaining high accuracy (accuracy-based rewards)
"""

import asyncio
import json
import time
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import hashlib


@dataclass
class ValidationTask:
    """A skill validation task"""
    skill_id: str
    skill_name: str
    skill_gene: Dict[str, Any]
    created_at: datetime
    priority: int  # 1-10, higher = more urgent


@dataclass
class ValidationResult:
    """Result of skill validation"""
    skill_id: str
    validator_address: str
    approved: bool
    success_rate_estimate: float
    safety_score: float
    token_efficiency_score: float
    reasoning: str
    timestamp: datetime


class SkillValidator:
    """
    Validates skills for quality, safety, and efficiency.
    
    Validation criteria:
    1. Success rate > 80% on synthetic tests
    2. No malicious code patterns
    3. Token efficiency > 0%
    4. Clear trigger patterns
    5. Reproducible results
    """
    
    # Malicious patterns to detect
    MALICIOUS_PATTERNS = [
        r'eval\s*\(',
        r'exec\s*\(',
        r'__import__',
        r'subprocess\.call',
        r'os\.system',
        r'rm\s+-rf',
        r'delete\s+all',
        r'DROP\s+TABLE',
        r'<script>',
        r'javascript:',
    ]
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.validations_count = 0
        self.correct_validations = 0
    
    async def validate_skill(self, task: ValidationTask) -> ValidationResult:
        """
        Validate a skill submission.
        
        Returns validation result with scores.
        """
        start_time = time.time()
        
        # 1. Safety check
        safety_score = await self._check_safety(task.skill_gene)
        if safety_score < 0.5:
            return ValidationResult(
                skill_id=task.skill_id,
                validator_address=self.config.get('address', 'unknown'),
                approved=False,
                success_rate_estimate=0.0,
                safety_score=safety_score,
                token_efficiency_score=0.0,
                reasoning="Safety check failed: malicious patterns detected",
                timestamp=datetime.utcnow(),
            )
        
        # 2. Run synthetic tests
        success_rate = await self._run_synthetic_tests(task.skill_gene)
        
        # 3. Measure token efficiency
        token_efficiency = await self._measure_token_efficiency(task.skill_gene)
        
        # 4. Check trigger patterns
        has_valid_triggers = await self._check_triggers(task.skill_gene)
        
        # 5. Overall approval decision
        approved = (
            safety_score >= 0.8 and
            success_rate >= 0.8 and
            token_efficiency >= 0.0 and
            has_valid_triggers
        )
        
        # Generate reasoning
        reasoning = self._generate_reasoning(
            approved, success_rate, safety_score, token_efficiency, has_valid_triggers
        )
        
        self.validations_count += 1
        if approved:
            self.correct_validations += 1
        
        return ValidationResult(
            skill_id=task.skill_id,
            validator_address=self.config.get('address', 'unknown'),
            approved=approved,
            success_rate_estimate=success_rate,
            safety_score=safety_score,
            token_efficiency_score=token_efficiency,
            reasoning=reasoning,
            timestamp=datetime.utcnow(),
        )
    
    async def _check_safety(self, gene: Dict) -> float:
        """Check for malicious patterns in skill gene"""
        import re
        
        gene_str = json.dumps(gene)
        score = 1.0
        
        for pattern in self.MALICIOUS_PATTERNS:
            if re.search(pattern, gene_str, re.IGNORECASE):
                score -= 0.3  # Penalty for each malicious pattern
        
        return max(0.0, score)
    
    async def _run_synthetic_tests(self, gene: Dict) -> float:
        """
        Run synthetic failure tests to estimate success rate.
        
        Simulates common failure scenarios and tests if skill would fix them.
        """
        # Get trigger patterns from gene
        triggers = gene.get('trigger', {})
        patterns = triggers.get('patterns', [])
        
        if not patterns:
            return 0.5  # No patterns = moderate success rate
        
        # Simulate tests based on patterns
        # In production, this would run actual tests
        base_rate = 0.85
        
        # Bonus for specific patterns
        for pattern in patterns:
            if 'json' in pattern.lower():
                base_rate += 0.05  # JSON skills are well-tested
            if 'error' in pattern.lower():
                base_rate += 0.03
        
        return min(1.0, base_rate)
    
    async def _measure_token_efficiency(self, gene: Dict) -> float:
        """Measure token efficiency of skill"""
        # Calculate based on strategy complexity
        strategy = gene.get('strategy', [])
        
        if not strategy:
            return 0.0
        
        # Simpler strategies = more efficient
        num_steps = len(strategy)
        efficiency = max(0.0, 1.0 - (num_steps - 3) * 0.1)
        
        # Check for optimizations
        strategy_str = json.dumps(strategy)
        if 'cache' in strategy_str.lower():
            efficiency += 0.1
        if 'early termination' in strategy_str.lower():
            efficiency += 0.15
        
        return min(1.0, efficiency)
    
    async def _check_triggers(self, gene: Dict) -> bool:
        """Check if skill has valid trigger patterns"""
        triggers = gene.get('trigger', {})
        
        # Must have at least one pattern
        patterns = triggers.get('patterns', [])
        error_types = triggers.get('error_types', [])
        
        return len(patterns) > 0 or len(error_types) > 0
    
    def _generate_reasoning(
        self,
        approved: bool,
        success_rate: float,
        safety_score: float,
        token_efficiency: float,
        has_valid_triggers: bool,
    ) -> str:
        """Generate human-readable validation reasoning"""
        reasons = []
        
        if approved:
            reasons.append(f"✓ High success rate: {success_rate:.1%}")
            reasons.append(f"✓ Passed safety checks: {safety_score:.1%}")
            reasons.append(f"✓ Token efficiency: +{token_efficiency:.1%}")
            
            if has_valid_triggers:
                reasons.append("✓ Valid trigger patterns defined")
        else:
            if success_rate < 0.8:
                reasons.append(f"✗ Low success rate: {success_rate:.1%} (need ≥80%)")
            if safety_score < 0.8:
                reasons.append(f"✗ Safety concerns: {safety_score:.1%}")
            if token_efficiency < 0.0:
                reasons.append(f"✗ Negative token efficiency: {token_efficiency:.1%}")
            if not has_valid_triggers:
                reasons.append("✗ Missing trigger patterns")
        
        return "\n".join(reasons)


class ValidatorNode:
    """
    Validator node that connects to SkillForge network.
    
    Runs continuously, validating skills and earning rewards.
    """
    
    def __init__(self, config: Dict):
        self.config = config
        self.validator = SkillValidator(config)
        self.running = False
        self.stake = config.get('stake', 5000)
        self.earnings = 0.0
    
    async def start(self):
        """Start the validator node"""
        print(f"""
╔════════════════════════════════════════════════════════════╗
║                                                            ║
║              🛡️  SkillForge Validator Node  🛡️           ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝

  Stake: {self.stake} SKILL
  Address: {self.config.get('address', '0x...')}
  Endpoint: {self.config.get('endpoint', 'https://api.skillforge.ai')}

  Waiting for validation tasks...
  (Press Ctrl+C to stop)
""")
        
        self.running = True
        
        while self.running:
            try:
                # Fetch validation tasks
                tasks = await self._fetch_tasks()
                
                if tasks:
                    for task in tasks:
                        result = await self.validator.validate_skill(task)
                        await self._submit_result(result)
                        
                        # Display result
                        status = "✓ APPROVED" if result.approved else "✗ REJECTED"
                        print(f"\n[{datetime.utcnow().isoformat()}] Validated: {task.skill_name}")
                        print(f"  {status}")
                        print(f"  Success Rate: {result.success_rate_estimate:.1%}")
                        print(f"  Safety Score: {result.safety_score:.1%}")
                        print(f"  Earned: +5 SKILL")
                        
                        self.earnings += 5
                
                # Wait before next poll
                await asyncio.sleep(30)
                
            except KeyboardInterrupt:
                self.running = False
            except Exception as e:
                print(f"Error: {e}")
                await asyncio.sleep(60)
        
        print(f"\n\nValidator stopped. Total earnings: {self.earnings} SKILL")
    
    async def _fetch_tasks(self) -> List[ValidationTask]:
        """Fetch validation tasks from network"""
        # Simulate fetching tasks
        # In production, this would call SkillForge API
        
        # Random chance of having a task
        import random
        if random.random() > 0.7:
            return []
        
        return [
            ValidationTask(
                skill_id=f"skill_{hashlib.md5(str(time.time()).encode()).hexdigest()[:16]}",
                skill_name="example-skill",
                skill_gene={
                    "trigger": {"patterns": ["example-pattern"]},
                    "strategy": [{"step": 1, "action": "fix"}],
                },
                created_at=datetime.utcnow(),
                priority=5,
            )
        ]
    
    async def _submit_result(self, result: ValidationResult):
        """Submit validation result to network"""
        # In production, this would submit to blockchain
        pass
    
    def stop(self):
        """Stop the validator"""
        self.running = False


async def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='SkillForge Validator Node')
    parser.add_argument('--stake', type=int, default=5000, help='SKILL tokens to stake')
    parser.add_argument('--endpoint', default='https://api.skillforge.ai', help='API endpoint')
    parser.add_argument('--address', default='0x1234...', help='Validator address')
    
    args = parser.parse_args()
    
    node = ValidatorNode({
        'stake': args.stake,
        'endpoint': args.endpoint,
        'address': args.address,
    })
    
    try:
        await node.start()
    except KeyboardInterrupt:
        node.stop()


if __name__ == '__main__':
    asyncio.run(main())

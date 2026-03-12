#!/usr/bin/env python3
"""
SkillForge Demo - See the evolution in action

This demo shows how SkillForge:
1. Captures a failure
2. Clusters it with similar failures
3. Evolves a skill
4. Suggests the skill to fix the problem

Run: python demo.py
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from packages.core.src.evolution.engine import (
    EvolutionEngine,
    Failure,
)
import json
from datetime import datetime


def print_header(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


def demo_failure_capture():
    """Demo: Capture agent failures"""
    print_header("Step 1: Capture Agent Failures")
    
    failures = [
        Failure(
            id='fail-001',
            agent='code-agent',
            framework='langchain',
            error_name='JSONDecodeError',
            error_message='JSONDecodeError: Control character \\n at position 42',
            error_stack='File "parser.py", line 42',
            context={'input': '{"cmd": "git commit -m "feat: add\\n\\nMulti-line""}'},
            task='Parse LLM JSON response',
            timestamp=datetime.utcnow(),
        ),
        Failure(
            id='fail-002',
            agent='code-agent',
            framework='langchain',
            error_name='JSONDecodeError',
            error_message='JSONDecodeError: Control character \\t at position 15',
            error_stack='File "parser.py", line 42',
            context={'input': '{"text": "hello\\tworld"}'},
            task='Parse LLM JSON response',
            timestamp=datetime.utcnow(),
        ),
        Failure(
            id='fail-003',
            agent='data-agent',
            framework='openclaw',
            error_name='JSONDecodeError',
            error_message='JSONDecodeError: Control character \\r at position 8',
            error_stack='File "toolset.py", line 128',
            context={'input': '{"value": "line1\\rline2"}'},
            task='Extract structured data',
            timestamp=datetime.utcnow(),
        ),
    ]
    
    print(f"Captured {len(failures)} failures:\n")
    for failure in failures:
        print(f"  ❌ [{failure.agent}] {failure.error_name}")
        print(f"     Task: {failure.task}")
        print(f"     Error: {failure.error_message[:60]}...")
        print()
    
    return failures


def demo_skill_evolution(failures):
    """Demo: Evolve skill from failures"""
    print_header("Step 2: Evolve Skill from Failures")
    
    print("Analyzing failures...\n")
    
    engine = EvolutionEngine()
    skill = engine.evolve_from_failures(failures)
    
    if skill:
        print("✅ Skill evolved successfully!\n")
        print(f"  Name: {skill.name}")
        print(f"  Version: {skill.version}")
        print(f"  Description: {skill.description}")
        print(f"  Success Rate: {skill.success_rate:.1%}")
        print(f"  Token Efficiency: {skill.token_efficiency:+.1%}")
        print(f"  Tags: {', '.join(skill.tags)}")
        print()
        print("  Gene (first 200 chars):")
        print(f"  {skill.gene[:200]}...")
        print()
    else:
        print("❌ Skill evolution failed")
    
    return skill


def demo_skill_registry(skill):
    """Demo: Submit skill to decentralized registry"""
    print_header("Step 3: Submit to Decentralized Registry")
    
    if not skill:
        print("No skill to submit")
        return
    
    print("Submitting skill to registry...\n")
    
    # Simulate registry submission
    gene_data = skill.to_gene_format()
    
    print(f"  Skill ID: {gene_data['id']}")
    print(f"  Creator: {skill.creator}")
    print(f"  Stake Required: 100 SKILL tokens")
    print()
    print("  ✅ Skill submitted successfully!")
    print("  📊 Validation in progress...")
    print("  ⏳ Waiting for community validation (3 validators required)")
    print()
    print("  Expected validation results:")
    print("  - Token efficiency: +12% ✓")
    print("  - Success rate: 94.2% ✓")
    print("  - Safety check: Passed ✓")
    print()
    print("  🎉 Skill approved and published to global registry!")
    print(f"  🔗 View at: https://skillforge.ai/skills/{gene_data['id'][:16]}")


def demo_skill_usage(skill):
    """Demo: Use skill to fix a new failure"""
    print_header("Step 4: Use Skill to Fix New Failure")
    
    print("New failure detected:\n")
    print("  Agent: data-processor")
    print("  Error: JSONDecodeError: Control character \\n at position 50")
    print("  Task: Parse config file")
    print()
    
    print("🔍 Analyzing failure...\n")
    print("  Pattern match: JSON control characters")
    print(f"  Similar failures: 847 cases")
    print(f"  Suggested skill: {skill.name if skill else 'json-sanitizer'}")
    print()
    
    print("💡 Skill suggestion:\n")
    print("  [json-sanitizer v3.2.1]")
    print("  - Success rate: 94.2%")
    print("  - Uses: 12,847")
    print("  - Token savings: +12%")
    print()
    
    print("Apply skill? [Y/n]: Y\n")
    print("  ✅ Skill applied successfully!")
    print("  📊 Result: JSON parsed correctly")
    print("  ⚡ Time saved: ~2 hours (vs manual debugging)")
    print("  💰 Earned: +2 SKILL tokens")
    print()
    print("  🎉 Problem solved in 2 seconds instead of 2 hours!")


def demo_market_stats():
    """Demo: Show market statistics"""
    print_header("Market Statistics")
    
    print("  📊 SkillForge Ecosystem\n")
    print("  Skills Published: 847")
    print("  Total Failures Captured: 23,456")
    print("  Success Rate (avg): 91.3%")
    print("  Time Saved: 45,678 hours")
    print("  SKILL Tokens Distributed: 2,345,678")
    print()
    print("  Top Skills:")
    print("  1. json-sanitizer (94.2% success, 12.8K uses)")
    print("  2. adaptive-memory-config (89.7% success, 8.5K uses)")
    print("  3. tool-call-fixer (87.3% success, 6.2K uses)")
    print("  4. timeout-handler (91.5% success, 5.1K uses)")
    print("  5. rate-limit-handler (88.9% success, 4.8K uses)")
    print()
    print("  📈 Growth: +347% this month")
    print("  🌐 Validators: 234 active")
    print("  💎 Total Staked: 1.2M SKILL")


def main():
    print("""
╔════════════════════════════════════════════════════════════╗
║                                                            ║
║              🚀 SkillForge Demo 🚀                        ║
║                                                            ║
║        Turn every agent failure into a reusable skill     ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝
    """)
    
    # Step 1: Capture failures
    failures = demo_failure_capture()
    
    # Step 2: Evolve skill
    skill = demo_skill_evolution(failures)
    
    # Step 3: Submit to registry
    demo_skill_registry(skill)
    
    # Step 4: Use skill
    demo_skill_usage(skill)
    
    # Show market stats
    demo_market_stats()
    
    print_header("Demo Complete!")
    print("  🎯 Next Steps:\n")
    print("  1. Install SDK: npm install @skillforge/sdk")
    print("  2. Wrap your agent: forge.wrapAgent(myAgent)")
    print("  3. Start capturing failures automatically")
    print("  4. Earn SKILL tokens for valuable contributions")
    print()
    print("  📚 Documentation: https://docs.skillforge.ai")
    print("  💬 Discord: https://discord.gg/skillforge")
    print("  🐙 GitHub: https://github.com/skillforge/skillforge")
    print()
    print("  \"Every failure is a skill waiting to be born.\" 🚀\n")


if __name__ == '__main__':
    main()

"""
json-sanitizer - Helper functions for JSON sanitization

This module provides helper functions used by the json-sanitizer skill.
"""

import re
import json
from functools import lru_cache
from typing import Any, Dict, Optional


# Control character escape mapping
ESCAPE_MAP = {
    '\n': '\\n',
    '\r': '\\r',
    '\t': '\\t',
    '\f': '\\f',
    '\b': '\\b',
    '\v': '\\v',
    '\0': '\\0',
}


def detect_control_characters(s: str) -> bool:
    """
    Check if string contains unescaped control characters.
    
    Args:
        s: String to check
        
    Returns:
        True if control characters detected
    """
    # Pattern matches unescaped control characters
    pattern = r'(?<!\\)[\x00-\x1f\x7f-\x9f]'
    return bool(re.search(pattern, s))


def escape_control_characters(s: str) -> str:
    """
    Escape control characters in a string.
    
    Args:
        s: Input string
        
    Returns:
        String with escaped control characters
    """
    def escape_match(match):
        char = match.group(0)
        return ESCAPE_MAP.get(char, f'\\u{ord(char):04x}')
    
    # Match unescaped control characters
    pattern = r'(?<!\\)[\x00-\x1f\x7f-\x9f]'
    return re.sub(pattern, escape_match, s)


@lru_cache(maxsize=1000)
def sanitize_json_cached(s: str) -> str:
    """
    Cached version of JSON sanitization.
    
    Args:
        s: JSON string to sanitize
        
    Returns:
        Sanitized JSON string
    """
    if not detect_control_characters(s):
        return s
    return escape_control_characters(s)


def parse_json_safely(
    json_string: str,
    *,
    use_cache: bool = True,
    fallback_parsers: bool = False,
) -> Dict[str, Any]:
    """
    Parse JSON with automatic control character handling.
    
    Args:
        json_string: Raw JSON string
        use_cache: Whether to use caching (default: True)
        fallback_parsers: Try alternative parsers on failure (default: False)
        
    Returns:
        Parsed JSON object
        
    Raises:
        JSONDecodeError: If JSON is invalid after sanitization
        
    Example:
        >>> bad_json = '{"text": "hello\\nworld"}'
        >>> data = parse_json_safely(bad_json)
        >>> print(data['text'])
        hello
        world
    """
    sanitize = sanitize_json_cached if use_cache else escape_control_characters
    
    try:
        return json.loads(json_string)
    except json.JSONDecodeError as e:
        if 'control character' in str(e).lower():
            try:
                sanitized = sanitize(json_string)
                return json.loads(sanitized)
            except json.JSONDecodeError:
                pass
        
        if fallback_parsers:
            # Try alternative parsers
            try:
                import orjson
                return orjson.loads(sanitize(json_string))
            except ImportError:
                pass
            
            try:
                import ujson
                return ujson.loads(sanitize(json_string))
            except ImportError:
                pass
        
        raise


def validate_json_structure(
    data: Dict[str, Any],
    required_keys: Optional[list] = None,
) -> bool:
    """
    Validate parsed JSON has expected structure.
    
    Args:
        data: Parsed JSON object
        required_keys: List of required keys (optional)
        
    Returns:
        True if structure is valid
    """
    if not isinstance(data, dict):
        return False
    
    if required_keys:
        return all(key in data for key in required_keys)
    
    return True


# Convenience function for agent use
def safe_json_parse(json_string: str, **kwargs) -> Dict[str, Any]:
    """
    Main entry point for agents.
    
    This is the function that gets called when the skill is triggered.
    
    Args:
        json_string: JSON string to parse
        **kwargs: Additional options passed to parse_json_safely
        
    Returns:
        Parsed JSON object
    """
    return parse_json_safely(json_string, **kwargs)


if __name__ == '__main__':
    # Test cases
    test_cases = [
        ('{"valid": "json"}', {'valid': 'json'}),
        ('{"text": "hello\\nworld"}', {'text': 'hello\nworld'}),
        ('{"cmd": "git commit -m \\"feat: add\\n\\nMulti-line\\""}', None),
    ]
    
    for json_str, expected in test_cases:
        try:
            result = safe_json_parse(json_str)
            print(f"✓ Parsed: {json_str[:50]}...")
            if expected:
                assert result == expected, f"Expected {expected}, got {result}"
        except Exception as e:
            print(f"✗ Failed: {json_str[:50]}... - {e}")

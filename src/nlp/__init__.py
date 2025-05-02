"""
G3r4ki Natural Language Processing

This package provides natural language processing capabilities for the G3r4ki system,
allowing for command understanding, intent recognition, and entity extraction.
"""

from .command_processor import CommandProcessor
from .reasoning_engine import ReasoningEngine
from .nlp_utils import (
    parse_command,
    determine_intent,
    extract_entities,
    extract_urls,
    extract_ips,
    extract_domain_names,
    extract_ports,
    extract_options,
    extract_key_phrases
)

__all__ = [
    'CommandProcessor',
    'ReasoningEngine',
    'parse_command',
    'determine_intent',
    'extract_entities',
    'extract_urls',
    'extract_ips',
    'extract_domain_names',
    'extract_ports',
    'extract_options',
    'extract_key_phrases'
]
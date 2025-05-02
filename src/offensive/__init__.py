"""
G3r4ki Offensive Framework

This module provides advanced penetration testing and red team operation capabilities
through a modular, extensible framework.
"""

from typing import Dict, List, Any, Optional

# Define mission profiles
MISSION_PROFILES = {
    'stealth': {
        'description': 'Prioritizes minimal footprint, evasion, and anti-forensics',
        'priority_modules': [
            'evasion_engine',
            'memory_resident',
            'anti_forensics',
            'silent_credentials',
            'low_bandwidth_c2',
            'minimal_persistence'
        ],
        'avoid_modules': [
            'loud_exploitation',
            'bulk_exfiltration',
            'excessive_scanning',
            'noisy_lateral_movement'
        ]
    },
    'loud': {
        'description': 'Maximizes speed and effectiveness without concern for detection',
        'priority_modules': [
            'mass_exploitation',
            'aggressive_scanning',
            'rapid_exfiltration',
            'maximum_impact',
            'fast_lateral_movement'
        ],
        'avoid_modules': [
            'time_delayed_actions',
            'complex_evasion',
            'stealth_techniques'
        ]
    },
    'persistence': {
        'description': 'Focuses on establishing long-term access',
        'priority_modules': [
            'multi_level_persistence',
            'boot_persistence',
            'service_persistence',
            'kernel_implants',
            'scheduled_tasks',
            'redundant_access'
        ],
        'avoid_modules': [
            'volatile_access',
            'memory_only_techniques',
            'network_dependent_access'
        ]
    },
    'data_extraction': {
        'description': 'Optimizes for data identification and exfiltration',
        'priority_modules': [
            'data_discovery',
            'database_access',
            'file_indexing',
            'staged_exfiltration',
            'data_compression',
            'encryption'
        ],
        'avoid_modules': [
            'system_modification',
            'lateral_movement',
            'complex_persistence'
        ]
    },
}

# Export module-related constants
__all__ = [
    'MISSION_PROFILES',
]
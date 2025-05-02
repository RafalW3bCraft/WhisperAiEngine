"""
G3r4ki Agent Skills

This module provides skills that agents can use to accomplish tasks.
Skills are the building blocks of agent capabilities, and can be composed
to form complex operations.
"""

from src.agents.skills.base import Skill, SkillRegistry, skill
from src.agents.skills.network import NetworkSkills
from src.agents.skills.recon import ReconSkills
from src.agents.skills.analysis import AnalysisSkills
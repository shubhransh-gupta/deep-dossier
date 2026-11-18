"""
Deep Dossier - Autonomous multi-step research agent using Google Gemini.
"""

__version__ = "0.1.0"
__author__ = "Shubhransh Gupta"

from .agent import DeepResearchAgent
from .config import ResearchConfig

__all__ = ["DeepResearchAgent", "ResearchConfig", "__version__"]

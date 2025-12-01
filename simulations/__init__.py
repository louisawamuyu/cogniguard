"""
CogniGuard Simulations Module
Contains simulations of real-world AI safety incidents
"""

from .sydney_simulation import SydneySimulation
from .samsung_simulation import SamsungSimulation
from .autogpt_simulation import AutoGPTSimulation

__all__ = ['SydneySimulation', 'SamsungSimulation', 'AutoGPTSimulation']
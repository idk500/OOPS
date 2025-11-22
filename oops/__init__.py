"""
OOPS - Open-source One-click Problem Solver
开源一键问题排查器

A lightweight diagnostic toolbox for Windows gamers and developers.
"""

__version__ = "0.1.0"
__author__ = "OOPS Team"
__email__ = "oops@example.com"

from oops.core.diagnostics import DiagnosticSuite
from oops.core.config import ConfigManager
from oops.core.report import ReportGenerator

__all__ = [
    "DiagnosticSuite",
    "ConfigManager", 
    "ReportGenerator",
]
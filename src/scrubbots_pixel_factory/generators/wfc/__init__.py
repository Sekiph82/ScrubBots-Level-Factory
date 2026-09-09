"""Project-owned deterministic overlapping-pattern WFC generator."""

from .generator import WFCGenerator
from .model import Exemplar, ExemplarRegistry, Pattern, PatternTable, WFCConfig, WFCCandidate, WFCContractError
from .patterns import extract_pattern_table, transformed_patterns
from .solver import SolveOutcome, WFCContradiction, solve_pattern_table

__all__ = [
    "Exemplar", "ExemplarRegistry", "Pattern", "PatternTable", "WFCConfig", "WFCCandidate",
    "WFCContractError", "WFCGenerator", "extract_pattern_table", "transformed_patterns",
    "SolveOutcome", "WFCContradiction", "solve_pattern_table",
]

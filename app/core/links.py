"""
URL constants for PapaCambridge.
"""
from enum import Enum


class RemoteLinks(Enum):
    """Remote links for PapaCambridge past papers."""
    AICE = 'https://pastpapers.papacambridge.com/papers/caie/as-and-a-level'
    IGCSE = 'https://pastpapers.papacambridge.com/papers/caie/igcse'
    O = 'https://pastpapers.papacambridge.com/papers/caie/o-level'
    PAST_PAPERS = 'https://pastpapers.papacambridge.com/'
    AICE_PATTERN = 'as-and-a-level'
    O_PATTERN = 'o-level'
    IGCSE_PATTERN = 'igcse'

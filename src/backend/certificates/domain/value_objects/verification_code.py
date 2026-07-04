"""
Verification code value object
"""

import random
import string
from datetime import datetime


class VerificationCode:
    """
    Certificate verification code.

    Format: LF-{YEAR}-{RANDOM_6_CHARS}
    Example: LF-2026-8AF3D2
    """

    def __init__(self, code: str):
        """Initialize with existing code."""
        if not self._is_valid_format(code):
            raise ValueError(f"Invalid verification code format: {code}")
        self.code = code

    @classmethod
    def generate(cls, year: int = None) -> 'VerificationCode':
        """Generate a new verification code."""
        if year is None:
            year = datetime.now().year

        
        random_part = ''.join(
            random.choices(string.ascii_uppercase + string.digits, k=6)
        )

        code = f"LF-{year}-{random_part}"
        return cls(code)

    @staticmethod
    def _is_valid_format(code: str) -> bool:
        """Validate code format."""
        if not code or not isinstance(code, str):
            return False

        parts = code.split('-')
        if len(parts) != 3:
            return False

        prefix, year, random_part = parts

        
        if prefix != 'LF':
            return False

        
        if not year.isdigit() or len(year) != 4:
            return False

        
        if len(random_part) != 6 or not random_part.isalnum():
            return False

        return True

    def __str__(self) -> str:
        return self.code

    def __repr__(self) -> str:
        return f"VerificationCode('{self.code}')"

    def __eq__(self, other) -> bool:
        if not isinstance(other, VerificationCode):
            return False
        return self.code == other.code

    def __hash__(self) -> int:
        return hash(self.code)

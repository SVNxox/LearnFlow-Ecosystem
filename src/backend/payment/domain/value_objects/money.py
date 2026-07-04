"""
Money value object.
"""

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class Money:
    """
    Money value object.

    Immutable representation of monetary amount with currency.
    """

    amount: Decimal
    currency: str  

    def __post_init__(self):
        """Validate money value."""
        if self.amount < 0:
            raise ValueError("Amount cannot be negative")
        if len(self.currency) != 3:
            raise ValueError("Currency must be ISO 4217 code (3 letters)")
        if not self.currency.isupper():
            raise ValueError("Currency must be uppercase")

    def __str__(self) -> str:
        return f"{self.amount} {self.currency}"

    def to_cents(self) -> int:
        """
        Convert to cents (for Stripe API).

        Used when integrating with payment providers that expect integer cents.
        """
        return int(self.amount * 100)

    @classmethod
    def from_cents(cls, cents: int, currency: str) -> 'Money':
        """Create Money from cents."""
        return cls(amount=Decimal(cents) / 100, currency=currency)

    def __add__(self, other: 'Money') -> 'Money':
        """Add two money values (same currency only)."""
        if self.currency != other.currency:
            raise ValueError(f"Cannot add {self.currency} and {other.currency}")
        return Money(amount=self.amount + other.amount, currency=self.currency)

    def __sub__(self, other: 'Money') -> 'Money':
        """Subtract two money values (same currency only)."""
        if self.currency != other.currency:
            raise ValueError(f"Cannot subtract {self.currency} and {other.currency}")
        return Money(amount=self.amount - other.amount, currency=self.currency)

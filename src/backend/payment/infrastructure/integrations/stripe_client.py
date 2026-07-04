"""
Stripe Client — Integration stub for Stripe API.

TODO: Implement when Stripe integration is ready.
Requires: stripe Python library, webhook signature verification.
"""

from decimal import Decimal
from typing import Dict, Optional


class StripeClient:
    """
    Wrapper for Stripe API.

    Current status: STUB
    Real implementation requires:
    - stripe library installed
    - STRIPE_SECRET_KEY in settings
    - Webhook endpoint configured
    - Signature verification
    """

    def __init__(self):
        """Initialize Stripe client."""
        
        pass

    def create_payment_intent(
        self,
        amount: int,
        currency: str,
        metadata: Dict
    ) -> Dict:
        """
        Create payment intent.

        Args:
            amount: Amount in cents (e.g., 5000 for $50.00)
            currency: ISO 4217 currency code
            metadata: Custom metadata

        Returns:
            Dict with 'id', 'client_secret', 'status'

        TODO: Implement
        """
        
        return {
            'id': 'pi_stub_123456789',
            'client_secret': 'pi_stub_123456789_secret_stub',
            'status': 'requires_payment_method',
            'amount': amount,
            'currency': currency,
            'metadata': metadata,
        }

    def create_refund(
        self,
        payment_intent_id: str,
        amount: int,
        reason: Optional[str] = None
    ) -> Dict:
        """
        Create refund.

        Args:
            payment_intent_id: Stripe payment intent ID
            amount: Amount to refund in cents
            reason: Refund reason

        Returns:
            Dict with 'id', 'status', 'amount'

        TODO: Implement
        """
        
        return {
            'id': 're_stub_123456789',
            'status': 'succeeded',
            'amount': amount,
            'payment_intent': payment_intent_id,
            'reason': reason,
        }

    def verify_webhook_signature(
        self,
        payload: bytes,
        signature: str,
        secret: str
    ) -> bool:
        """
        Verify webhook signature.

        Critical for security — prevents webhook spoofing.

        Args:
            payload: Raw request body
            signature: Stripe-Signature header value
            secret: Webhook signing secret

        Returns:
            True if signature valid

        TODO: Implement using stripe.Webhook.construct_event()
        """
        
        
        return True

from django.urls import path

from src.backend.payment.presentation.rest.v1.payments.stripe_checkout import StripeCheckoutView
from src.backend.payment.presentation.rest.v1.webhooks.stripe_checkout import StripeCheckoutWebhookView
from src.backend.payment.presentation.rest.v1.payments.create import CreatePaymentView
from src.backend.payment.presentation.rest.v1.payments.list import PaymentListView
from src.backend.payment.presentation.rest.v1.payments.detail import PaymentDetailView
from src.backend.payment.presentation.rest.v1.payments.admin_list import AdminPaymentsListView
from src.backend.payment.presentation.rest.v1.payments.admin_detail import AdminPaymentDetailView
from src.backend.payment.presentation.rest.v1.payments.simulate import SimulatePaymentSuccessView
from src.backend.payment.presentation.rest.v1.payments.telegram_invoice import TelegramInvoiceView  
from src.backend.payment.presentation.rest.v1.refunds.create import CreateRefundView
from src.backend.payment.presentation.rest.v1.refunds.detail import RefundDetailView
from src.backend.payment.presentation.rest.v1.webhooks.stripe import StripeWebhookView
from src.backend.payment.presentation.rest.v1.webhooks.payme import PaymeWebhookView
from src.backend.payment.presentation.rest.v1.webhooks.telegram import TelegramWebhookView  

app_name = 'payment'

urlpatterns = [
    
    path('admin/payments/', AdminPaymentsListView.as_view(), name='admin-payment-list'),
    path('admin/payments/<str:payment_id>/', AdminPaymentDetailView.as_view(), name='admin-payment-detail'),

    
    path('payments/create/', CreatePaymentView.as_view(), name='payment-create'),
    path('payments/', PaymentListView.as_view(), name='payment-list'),
    path('payments/<str:payment_id>/', PaymentDetailView.as_view(), name='payment-detail'),

    
    path('payments/<str:payment_id>/telegram-invoice/', TelegramInvoiceView.as_view(), name='telegram-invoice'),
    

    
    path('payments/<str:payment_id>/simulate-success/', SimulatePaymentSuccessView.as_view(),
         name='payment-simulate-success'),

    
    path('payments/<str:payment_id>/refund/', CreateRefundView.as_view(), name='refund-create'),
    path('refunds/<str:refund_id>/', RefundDetailView.as_view(), name='refund-detail'),

    
    path('webhooks/stripe/', StripeWebhookView.as_view(), name='webhook-stripe'),
    path('webhooks/payme/', PaymeWebhookView.as_view(), name='webhook-payme'),
    path('webhooks/telegram/', TelegramWebhookView.as_view(), name='webhook-telegram'),  

    path('stripe/checkout/<str:payment_id>/', StripeCheckoutView.as_view(), name='stripe-checkout'),

    
    path('webhooks/stripe-checkout/', StripeCheckoutWebhookView.as_view(), name='stripe-checkout-webhook'),
]
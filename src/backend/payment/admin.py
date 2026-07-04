"""
Django Admin configuration for Payment Domain
"""

from django.contrib import admin
from django.utils.html import format_html

from src.backend.payment.domain.models.payment import Payment
from src.backend.payment.domain.models.transaction import PaymentTransaction
from src.backend.payment.domain.models.refund import Refund


class PaymentTransactionInline(admin.TabularInline):
    """Inline for PaymentTransaction."""
    model = PaymentTransaction
    extra = 0
    readonly_fields = ['transaction_type', 'amount', 'transaction_id', 'provider_response', 'created_at']
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


class RefundInline(admin.TabularInline):
    """Inline for Refund."""
    model = Refund
    extra = 0
    readonly_fields = ['amount', 'reason', 'status', 'succeeded_at', 'failed_at']
    fields = ['amount', 'reason', 'status', 'succeeded_at', 'failed_at']
    can_delete = False


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    """Admin for Payment."""

    list_display = [
        'id_short',
        'user_email',
        'amount_display',
        'status_badge',
        'provider',
        'created_at',
        'succeeded_at',
    ]

    list_filter = [
        'status',
        'provider',
        'currency',
        'created_at',
        'succeeded_at',
    ]

    search_fields = [
        'id',
        'user_id',
        'enrollment_id',
        'provider_payment_id',
        'idempotency_key',
    ]

    readonly_fields = [
        'id',
        'user_id',
        'enrollment_id',
        'amount',
        'currency',
        'status',
        'provider',
        'provider_payment_id',
        'idempotency_key',
        'payment_method',
        'card_last4',
        'card_brand',
        'failure_code',
        'failure_message',
        'metadata',
        'created_at',
        'updated_at',
        'succeeded_at',
        'failed_at',
        'refunded_at',
    ]

    fieldsets = (
        ('Identification', {
            'fields': ('id', 'user_id', 'enrollment_id', 'idempotency_key')
        }),
        ('Payment Details', {
            'fields': ('amount', 'currency', 'status', 'provider', 'provider_payment_id')
        }),
        ('Payment Method', {
            'fields': ('payment_method', 'card_last4', 'card_brand')
        }),
        ('Failure Info', {
            'fields': ('failure_code', 'failure_message'),
            'classes': ('collapse',),
        }),
        ('Metadata', {
            'fields': ('metadata',),
            'classes': ('collapse',),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'succeeded_at', 'failed_at', 'refunded_at')
        }),
    )

    inlines = [PaymentTransactionInline, RefundInline]

    def id_short(self, obj):
        return str(obj.id)[:8]
    id_short.short_description = 'ID'

    def user_email(self, obj):
        return str(obj.user_id)[:8]
    user_email.short_description = 'User'

    def amount_display(self, obj):
        return f"{obj.amount} {obj.currency}"
    amount_display.short_description = 'Amount'

    def status_badge(self, obj):
        colors = {
            'pending': 'orange',
            'processing': 'blue',
            'succeeded': 'green',
            'failed': 'red',
            'refunded': 'gray',
            'canceled': 'gray',
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.status.upper()
        )
    status_badge.short_description = 'Status'


@admin.register(PaymentTransaction)
class PaymentTransactionAdmin(admin.ModelAdmin):
    """Admin for PaymentTransaction."""

    list_display = [
        'id_short',
        'payment_link',
        'transaction_type',
        'amount',
        'created_at',
    ]

    list_filter = [
        'transaction_type',
        'created_at',
    ]

    search_fields = [
        'payment_id',
        'transaction_id',
    ]

    readonly_fields = [
        'id',
        'payment_id',
        'transaction_type',
        'amount',
        'transaction_id',
        'provider_response',
        'created_at',
    ]

    fieldsets = (
        ('Identification', {
            'fields': ('id', 'payment_id', 'transaction_id')
        }),
        ('Transaction', {
            'fields': ('transaction_type', 'amount')
        }),
        ('Provider Response', {
            'fields': ('provider_response',),
            'classes': ('collapse',),
        }),
        ('Timestamps', {
            'fields': ('created_at',)
        }),
    )

    def id_short(self, obj):
        return str(obj.id)[:8]
    id_short.short_description = 'ID'

    def payment_link(self, obj):
        return format_html(
            '<a href="/admin/payment/payment/{}/change/">{}</a>',
            obj.payment_id,
            str(obj.payment_id)[:8]
        )
    payment_link.short_description = 'Payment'


@admin.register(Refund)
class RefundAdmin(admin.ModelAdmin):
    """Admin for Refund."""

    list_display = [
        'id_short',
        'payment_link',
        'amount',
        'status_badge',
        'reason',
        'created_at',
        'succeeded_at',
    ]

    list_filter = [
        'status',
        'reason',
        'created_at',
        'succeeded_at',
    ]

    search_fields = [
        'payment_id',
        'provider_refund_id',
    ]

    readonly_fields = [
        'id',
        'payment_id',
        'amount',
        'reason',
        'reason_details',
        'status',
        'provider_refund_id',
        'initiated_by_id',
        'created_at',
        'succeeded_at',
        'failed_at',
    ]

    fieldsets = (
        ('Identification', {
            'fields': ('id', 'payment_id', 'provider_refund_id')
        }),
        ('Refund Details', {
            'fields': ('amount', 'reason', 'reason_details', 'status')
        }),
        ('Processing', {
            'fields': ('initiated_by_id',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'succeeded_at', 'failed_at')
        }),
    )

    def id_short(self, obj):
        return str(obj.id)[:8]
    id_short.short_description = 'ID'

    def payment_link(self, obj):
        return format_html(
            '<a href="/admin/payment/payment/{}/change/">{}</a>',
            obj.payment_id,
            str(obj.payment_id)[:8]
        )
    payment_link.short_description = 'Payment'

    def status_badge(self, obj):
        colors = {
            'pending': 'orange',
            'processing': 'blue',
            'succeeded': 'green',
            'failed': 'red',
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.status.upper()
        )
    status_badge.short_description = 'Status'

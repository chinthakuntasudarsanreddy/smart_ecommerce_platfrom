from django.contrib import admin

from .models import Order, OrderItem
from .forms import OrderForm, OrderItemForm


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):

    form = OrderForm

    list_display = (
        "id",
        "user_id",
        "total",
        "payment_status",
        "order_status",
        "created_at",
    )

    list_filter = (
        "payment_status",
        "order_status",
    )

    search_fields = (
        "id",
        "user_id",
    )

    readonly_fields = (
        "id",
        "created_at",
    )

    ordering = (
        "-created_at",
    )


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):

    form = OrderItemForm

    list_display = (
        "id",
        "order_id",
        "product_id",
        "quantity",
        "price",
    )

    search_fields = (
        "id",
        "order_id",
        "product_id",
    )

    readonly_fields = (
        "id",
    )
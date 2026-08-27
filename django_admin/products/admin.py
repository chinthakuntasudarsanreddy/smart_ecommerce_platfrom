from django.contrib import admin

from .models import Product
from .forms import ProductForm


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):

    form = ProductForm

    list_display = (
        "id",
        "name",
        "category",
        "price",
        "stock",
        "popularity",
        "created_at",
    )

    search_fields = (
        "name",
        "category",
        "description",
    )

    list_filter = (
        "category",
    )

    ordering = (
        "-created_at",
    )

    readonly_fields = (
        "id",
        "created_at",
        "updated_at",
    )

    list_per_page = 20
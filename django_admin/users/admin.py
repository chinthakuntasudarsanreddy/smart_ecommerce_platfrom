from django.contrib import admin

from .models import User
from .forms import UserForm


@admin.register(User)
class UserAdmin(admin.ModelAdmin):

    form = UserForm

    list_display = (
        "id",
        "email",
        "role",
        "created_at",
    )

    search_fields = (
        "email",
    )

    list_filter = (
        "role",
    )

    readonly_fields = (
        "id",
        "created_at",
    )

    ordering = (
        "-created_at",
    )

    list_per_page = 20

    def has_add_permission(self, request):
        return True

    def has_change_permission(self, request, obj=None):
        return True

    def has_delete_permission(self, request, obj=None):
        return True
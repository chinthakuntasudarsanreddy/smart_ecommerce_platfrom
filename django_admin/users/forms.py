from django import forms
from django.utils import timezone

from .models import User


class UserForm(forms.ModelForm):

    class Meta:
        model = User
        fields = "__all__"

    def save(self, commit=True):

        user = super().save(commit=False)

        if hasattr(user, "created_at") and not user.created_at:
            user.created_at = timezone.now()

        if commit:
            user.save()

        return user
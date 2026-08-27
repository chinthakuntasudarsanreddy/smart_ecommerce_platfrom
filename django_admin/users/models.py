from django.db import models


class User(models.Model):

    ROLE_CHOICES = [
        ("admin", "Admin"),
        ("staff", "Staff"),
        ("customer", "Customer"),
    ]

    id = models.BigAutoField(
        primary_key=True
    )

    name = models.CharField(
        max_length=120
    )

    email = models.EmailField(
        max_length=255,
        unique=True
    )

    password = models.CharField(
        max_length=255,
        null=True,
        blank=True
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default="customer"
    )

    created_at = models.DateTimeField()

    auth0_sub = models.CharField(
        max_length=255,
        unique=True,
        null=True,
        blank=True
    )

    class Meta:
        db_table = "users"
        managed = False
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} ({self.email})"
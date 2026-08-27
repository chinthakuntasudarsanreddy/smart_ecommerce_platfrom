from django.db import models


class Order(models.Model):

    PAYMENT_STATUS_CHOICES = [
        ("pending", "Pending"),
        ("paid", "Paid"),
        ("failed", "Failed"),
        ("refunded", "Refunded"),
    ]

    ORDER_STATUS_CHOICES = [
        ("pending", "Pending"),
        ("paid", "Paid"),
        ("shipped", "Shipped"),
        ("delivered", "Delivered"),
        ("cancelled", "Cancelled"),
    ]

    id = models.IntegerField(
        primary_key=True
    )

    user_id = models.IntegerField(
        null=False,
        blank=False
    )

    total = models.FloatField(
        null=False,
        blank=False
    )

    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default="pending"
    )

    order_status = models.CharField(
        max_length=20,
        choices=ORDER_STATUS_CHOICES,
        default="pending"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        managed = False
        db_table = "orders"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Order #{self.id}"


class OrderItem(models.Model):

    id = models.IntegerField(
        primary_key=True
    )

    order_id = models.IntegerField(
        null=False,
        blank=False
    )

    product_id = models.IntegerField(
        null=False,
        blank=False
    )

    quantity = models.IntegerField(
        null=False,
        blank=False
    )

    price = models.FloatField(
        null=False,
        blank=False
    )

    class Meta:
        managed = False
        db_table = "order_items"

    def __str__(self):
        return f"Order Item #{self.id}"
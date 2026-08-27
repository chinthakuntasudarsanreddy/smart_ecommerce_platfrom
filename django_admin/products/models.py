from django.db import models


class Product(models.Model):

    id = models.AutoField(
        primary_key=True
    )

    name = models.CharField(
        max_length=255
    )

    description = models.TextField(
        blank=True,
        null=True
    )

    category = models.CharField(
        max_length=100
    )

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    stock = models.IntegerField(
        default=0
    )

    popularity = models.IntegerField(
        default=0
    )

    image_url = models.URLField(
        max_length=500,
        blank=True,
        null=True
    )

    created_at = models.DateTimeField()

    updated_at = models.DateTimeField()

    class Meta:

        managed = False

        db_table = "products"

        ordering = [
            "-created_at"
        ]

    def __str__(self):

        return self.name
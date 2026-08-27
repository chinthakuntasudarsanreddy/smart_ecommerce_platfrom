import os

from django import forms
from django.conf import settings

from .models import Product


class ProductForm(forms.ModelForm):

    image = forms.ImageField(
        required=False,
        label="Product Image"
    )

    class Meta:

        model = Product

        fields = [
            "name",
            "description",
            "category",
            "price",
            "stock",
            "popularity",
            "image",
        ]

    def save(self, commit=True):

        product = super().save(commit=False)

        image = self.cleaned_data.get("image")

        if image:

            upload_dir = os.path.join(
                settings.MEDIA_ROOT,
                "products"
            )

            os.makedirs(
                upload_dir,
                exist_ok=True
            )

            filename = image.name

            file_path = os.path.join(
                upload_dir,
                filename
            )

            with open(
                file_path,
                "wb+"
            ) as destination:

                for chunk in image.chunks():
                    destination.write(chunk)

            product.image_url = (
                "products/" + filename
            )

        if commit:
            product.save()

        return product
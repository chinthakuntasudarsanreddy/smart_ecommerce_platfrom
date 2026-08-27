from django import forms

from .models import Order, OrderItem


class OrderForm(forms.ModelForm):

    class Meta:
        model = Order
        fields = (
            "user_id",
            "total",
            "payment_status",
            "order_status",
        )


class OrderItemForm(forms.ModelForm):

    order_id = forms.IntegerField(
        min_value=1,
        label="Order ID"
    )

    product_id = forms.IntegerField(
        min_value=1,
        label="Product ID"
    )

    class Meta:
        model = OrderItem

        fields = (
            "order_id",
            "product_id",
            "quantity",
            "price",
        )

    def clean_order_id(self):
        order_id = self.cleaned_data["order_id"]

        if not Order.objects.filter(id=order_id).exists():
            raise forms.ValidationError(
                f"Order #{order_id} does not exist."
            )

        return order_id
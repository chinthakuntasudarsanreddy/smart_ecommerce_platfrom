from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import (
    get_object_or_404,
    redirect,
    render,
)

from .models import Order
from .forms import OrderStatusForm


@staff_member_required
def order_list(request):

    orders = Order.objects.all()

    search = request.GET.get("search", "").strip()

    status = request.GET.get("status", "").strip()

    payment_status = request.GET.get(
        "payment_status",
        ""
    ).strip()


    # Search by Order ID or User ID
    if search:

        if search.isdigit():

            orders = orders.filter(
                user_id=int(search)
            ) | orders.filter(
                id=int(search)
            )


    if status:

        orders = orders.filter(
            order_status=status
        )


    if payment_status:

        orders = orders.filter(
            payment_status=payment_status
        )


    context = {

        "orders": orders,

        "search": search,

        "status": status,

        "payment_status": payment_status,

    }


    return render(
        request,
        "orders/order_list.html",
        context
    )


@staff_member_required
def order_detail(request, order_id):

    order = get_object_or_404(
        Order,
        id=order_id
    )

    context = {
        "order": order,
    }

    return render(
        request,
        "orders/order_detail.html",
        context
    )


@staff_member_required
def update_order(request, order_id):

    order = get_object_or_404(
        Order,
        id=order_id
    )


    if request.method == "POST":

        form = OrderStatusForm(
            request.POST,
            instance=order
        )


        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Order updated successfully."
            )

            return redirect(
                "order_detail",
                order_id=order.id
            )


    else:

        form = OrderStatusForm(
            instance=order
        )


    return render(
        request,
        "orders/update_order.html",
        {
            "order": order,
            "form": form,
        }
    )
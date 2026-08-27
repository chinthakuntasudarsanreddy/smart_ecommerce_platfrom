from django.urls import path

from . import views
from . import reports


urlpatterns = [

    path(
        "",
        views.dashboard,
        name="dashboard",
    ),

    path(
        "reports/orders/csv/",
        reports.orders_csv,
        name="orders_csv",
    ),

    path(
        "reports/orders/pdf/",
        reports.orders_pdf,
        name="orders_pdf",
    ),

    path(
        "reports/sales/csv/",
        reports.sales_csv,
        name="sales_csv",
    ),

    path(
        "reports/sales/pdf/",
        reports.sales_pdf,
        name="sales_pdf",
    ),

    path(
        "reports/users/csv/",
        reports.users_csv,
        name="users_csv",
    ),

    path(
        "reports/users/pdf/",
        reports.users_pdf,
        name="users_pdf",
    ),
]
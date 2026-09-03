
from django.urls import path

from . import views
from . import reports


urlpatterns = [

    # =========================================
    # DASHBOARD
    # =========================================

    path(
        "",
        views.dashboard,
        name="dashboard",
    ),


    # =========================================
    # RETURN REQUESTS
    # =========================================

    path(
        "returns/",
        views.return_requests,
        name="return_requests",
    ),

    path(
        "returns/<int:return_id>/approve/",
        views.approve_return_request,
        name="approve_return_request",
    ),

    path(
        "returns/<int:return_id>/reject/",
        views.reject_return_request,
        name="reject_return_request",
    ),


    # =========================================
    # REPORTS
    # =========================================

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

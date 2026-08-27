import csv

from django.contrib.admin.views.decorators import staff_member_required
from django.db import connection
from django.http import HttpResponse


# =========================================
# ORDERS CSV
# =========================================

@staff_member_required
def orders_csv(request):

    response = HttpResponse(
        content_type="text/csv"
    )

    response["Content-Disposition"] = (
        'attachment; filename="orders.csv"'
    )

    writer = csv.writer(response)

    writer.writerow([
        "Order ID",
        "User ID",
        "Total",
        "Payment Status",
        "Order Status",
        "Created At",
    ])

    with connection.cursor() as cursor:

        cursor.execute("""
            SELECT
                id,
                user_id,
                total,
                payment_status,
                order_status,
                created_at
            FROM orders
            ORDER BY created_at DESC
        """)

        rows = cursor.fetchall()

    for row in rows:

        writer.writerow(row)

    return response


# =========================================
# SALES CSV
# =========================================

@staff_member_required
def sales_csv(request):

    response = HttpResponse(
        content_type="text/csv"
    )

    response["Content-Disposition"] = (
        'attachment; filename="sales.csv"'
    )

    writer = csv.writer(response)

    writer.writerow([
        "Order ID",
        "User ID",
        "Amount",
        "Payment Status",
        "Order Date",
    ])

    with connection.cursor() as cursor:

        cursor.execute("""
            SELECT
                id,
                user_id,
                total,
                payment_status,
                created_at
            FROM orders
            WHERE payment_status = 'paid'
            ORDER BY created_at DESC
        """)

        rows = cursor.fetchall()

    for row in rows:

        writer.writerow(row)

    return response


# =========================================
# USERS CSV
# =========================================

@staff_member_required
def users_csv(request):

    response = HttpResponse(
        content_type="text/csv"
    )

    response["Content-Disposition"] = (
        'attachment; filename="users.csv"'
    )

    writer = csv.writer(response)

    writer.writerow([
        "User ID",
        "Name",
        "Email",
        "Role",
        "Created At",
    ])

    with connection.cursor() as cursor:

        cursor.execute("""
            SELECT
                id,
                name,
                email,
                role,
                created_at
            FROM users
            ORDER BY created_at DESC
        """)

        rows = cursor.fetchall()

    for row in rows:

        writer.writerow(row)

    return response
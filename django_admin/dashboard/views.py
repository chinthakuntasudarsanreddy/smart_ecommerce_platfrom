
from django.contrib.admin.views.decorators import staff_member_required
from django.conf import settings
from django.db import connection
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST

import requests


# ============================================================
# DASHBOARD
# ============================================================

@staff_member_required
def dashboard(request):

    # =========================================
    # TOTAL ORDERS
    # =========================================

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT COUNT(*)
            FROM orders
        """)
        total_orders = cursor.fetchone()[0] or 0

    # =========================================
    # PAID ORDERS
    # =========================================

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT COUNT(*)
            FROM orders
            WHERE payment_status = 'paid'
        """)
        paid_orders = cursor.fetchone()[0] or 0

    # =========================================
    # PENDING ORDERS
    # =========================================

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT COUNT(*)
            FROM orders
            WHERE payment_status = 'pending'
        """)
        pending_orders = cursor.fetchone()[0] or 0

    # =========================================
    # CANCELLED ORDERS
    # =========================================

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT COUNT(*)
            FROM orders
            WHERE order_status = 'cancelled'
        """)
        cancelled_orders = cursor.fetchone()[0] or 0

    # =========================================
    # TOTAL SALES
    # =========================================

    total_sales = paid_orders

    # =========================================
    # TOTAL REVENUE
    # =========================================

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT COALESCE(SUM(total), 0)
            FROM orders
            WHERE payment_status = 'paid'
        """)
        total_revenue = cursor.fetchone()[0] or 0

    # =========================================
    # REVENUE TREND
    # =========================================

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT
                DATE(created_at),
                COALESCE(SUM(total), 0)
            FROM orders
            WHERE payment_status = 'paid'
            GROUP BY DATE(created_at)
            ORDER BY DATE(created_at)
        """)
        revenue_rows = cursor.fetchall()

    revenue_labels = [
        str(row[0])
        for row in revenue_rows
    ]

    revenue_values = [
        float(row[1])
        for row in revenue_rows
    ]

    # =========================================
    # RECENT ORDERS
    # =========================================

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
            LIMIT 10
        """)
        recent_order_rows = cursor.fetchall()

    recent_orders = [
        {
            "id": row[0],
            "user_id": row[1],
            "total": float(row[2]),
            "payment_status": row[3],
            "order_status": row[4],
            "created_at": row[5],
        }
        for row in recent_order_rows
    ]

    # =========================================
    # LOW STOCK PRODUCTS
    # =========================================

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT
                id,
                name,
                stock
            FROM products
            WHERE stock <= 10
            ORDER BY stock ASC
            LIMIT 10
        """)
        low_stock_rows = cursor.fetchall()

    low_stock_products = [
        {
            "id": row[0],
            "name": row[1],
            "stock": row[2],
        }
        for row in low_stock_rows
    ]

    # =========================================
    # TOP PRODUCTS
    # =========================================

    top_products = []

    try:

        with connection.cursor() as cursor:
            cursor.execute("""
                SHOW COLUMNS FROM order_items
            """)

            columns = {
                row[0]
                for row in cursor.fetchall()
            }

        product_column = None

        for column in [
            "product_id",
            "productId",
            "product"
        ]:
            if column in columns:
                product_column = column
                break

        quantity_column = None

        for column in [
            "quantity",
            "qty"
        ]:
            if column in columns:
                quantity_column = column
                break

        if product_column and quantity_column:

            with connection.cursor() as cursor:

                cursor.execute(f"""
                    SELECT
                        p.name,
                        SUM(oi.`{quantity_column}`) AS total_quantity
                    FROM order_items oi
                    INNER JOIN products p
                        ON p.id = oi.`{product_column}`
                    GROUP BY p.id, p.name
                    ORDER BY total_quantity DESC
                    LIMIT 10
                """)

                top_rows = cursor.fetchall()

            top_products = [
                {
                    "name": row[0],
                    "quantity": int(row[1]),
                }
                for row in top_rows
            ]

    except Exception:
        top_products = []

    # =========================================
    # CONTEXT
    # =========================================

    context = {
        "total_orders": total_orders,
        "paid_orders": paid_orders,
        "pending_orders": pending_orders,
        "cancelled_orders": cancelled_orders,
        "total_sales": total_sales,
        "total_revenue": float(total_revenue),
        "revenue_labels": revenue_labels,
        "revenue_values": revenue_values,
        "recent_orders": recent_orders,
        "low_stock_products": low_stock_products,
        "top_products": top_products,
    }

    # =========================================
    # RENDER
    # =========================================

    return render(
        request,
        "dashboard/dashboard.html",
        context
    )


# ============================================================
# RETURN REQUESTS
# ============================================================

@staff_member_required
def return_requests(request):

    with connection.cursor() as cursor:

        cursor.execute("""
            SELECT
                rr.id,
                rr.order_id,
                rr.user_id,
                rr.reason,
                rr.comment,
                rr.status,
                rr.created_at,
                o.total,
                o.order_status
            FROM return_requests rr
            INNER JOIN orders o
                ON o.id = rr.order_id
            ORDER BY rr.created_at DESC
        """)

        rows = cursor.fetchall()

    return_requests_data = [
        {
            "id": row[0],
            "order_id": row[1],
            "user_id": row[2],
            "reason": row[3],
            "comment": row[4],
            "status": row[5],
            "created_at": row[6],
            "amount": float(row[7]),
            "order_status": row[8],
        }
        for row in rows
    ]

    return render(
        request,
        "dashboard/return_requests.html",
        {
            "return_requests": return_requests_data
        }
    )


# ============================================================
# APPROVE RETURN REQUEST
# ============================================================

@staff_member_required
@require_POST
def approve_return_request(request, return_id):

    api_key = settings.INTERNAL_ADMIN_API_KEY

    if not api_key:
        return JsonResponse(
            {
                "success": False,
                "message": "Internal Admin API key is not configured",
            },
            status=500,
        )

    fastapi_url = (
        f"{settings.FASTAPI_BASE_URL}"
        f"/admin/returns/{return_id}/approve"
    )

    try:

        response = requests.post(
            fastapi_url,
            headers={
                "X-Internal-Admin-Key": api_key,
            },
            timeout=15,
        )

        try:
            data = response.json()

        except ValueError:
            data = {
                "success": response.ok,
                "message": response.text,
            }

        return JsonResponse(
            data,
            status=response.status_code,
        )

    except requests.RequestException as exc:

        return JsonResponse(
            {
                "success": False,
                "message": f"Unable to connect to FastAPI: {str(exc)}",
            },
            status=502,
        )


# ============================================================
# REJECT RETURN REQUEST
# ============================================================

@staff_member_required
@require_POST
def reject_return_request(request, return_id):

    api_key = settings.INTERNAL_ADMIN_API_KEY

    if not api_key:
        return JsonResponse(
            {
                "success": False,
                "message": "Internal Admin API key is not configured",
            },
            status=500,
        )

    fastapi_url = (
        f"{settings.FASTAPI_BASE_URL}"
        f"/admin/returns/{return_id}/reject"
    )

    try:

        response = requests.post(
            fastapi_url,
            headers={
                "X-Internal-Admin-Key": api_key,
            },
            timeout=15,
        )

        try:
            data = response.json()

        except ValueError:
            data = {
                "success": response.ok,
                "message": response.text,
            }

        return JsonResponse(
            data,
            status=response.status_code,
        )

    except requests.RequestException as exc:

        return JsonResponse(
            {
                "success": False,
                "message": f"Unable to connect to FastAPI: {str(exc)}",
            },
            status=502,
        )

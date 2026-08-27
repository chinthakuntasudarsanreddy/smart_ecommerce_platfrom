from django.contrib.admin.views.decorators import staff_member_required
from django.db import connection
from django.shortcuts import render


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
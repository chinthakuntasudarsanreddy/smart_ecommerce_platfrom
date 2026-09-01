from datetime import datetime, timedelta


RETURN_WINDOW_DAYS = 7


def is_return_allowed(order) -> bool:
    if order.status != "Delivered":
        return False

    if order.delivered_at is None:
        return False

    return datetime.utcnow() <= (
        order.delivered_at + timedelta(days=RETURN_WINDOW_DAYS)
    )
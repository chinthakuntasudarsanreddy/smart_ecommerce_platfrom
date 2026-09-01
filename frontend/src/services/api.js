
const API_URL = "http://127.0.0.1:8000";

// ============================================================
// PRODUCTS
// ============================================================

export async function getProducts() {
  const response = await fetch(`${API_URL}/products/`);

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.detail || `HTTP ${response.status}`);
  }

  return data;
}


// ============================================================
// ORDERS
// ============================================================

export async function getOrders() {
  const token = localStorage.getItem("access_token");

  console.log("Token:", token);

  if (!token) {
    throw new Error("Please login first");
  }

  const response = await fetch(`${API_URL}/orders/`, {
    method: "GET",
    headers: {
      Authorization: `Bearer ${token}`,
      Accept: "application/json",
    },
  });

  const data = await response.json();

  console.log("Orders response:", data);

  if (!response.ok) {
    throw new Error(data.detail || `HTTP ${response.status}`);
  }

  return data;
}


// ============================================================
// REQUEST RETURN
// ============================================================

export async function requestReturn(orderId, reason, comment) {
  const token = localStorage.getItem("access_token");

  if (!token) {
    throw new Error("Please login first");
  }

  const response = await fetch(
    `${API_URL}/orders/${orderId}/return`,
    {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
        Accept: "application/json",
      },
      body: JSON.stringify({
        reason: reason,
        comment: comment?.trim() || null,
      }),
    }
  );

  const data = await response.json();

  console.log("Return response:", data);

  if (!response.ok) {
    throw new Error(data.detail || `HTTP ${response.status}`);
  }

  return data;
}

const API_URL = "http://127.0.0.1:8000";

export async function getOrders() {
  try {
    const token = localStorage.getItem("access_token");

    const response = await fetch(`${API_URL}/orders`, {
      method: "GET",
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
    });

    console.log("Orders response:", response);

    if (!response.ok) {
      const errorData = await response.json().catch(() => null);

      throw new Error(
        errorData?.detail || `HTTP error: ${response.status}`
      );
    }

    const data = await response.json();

    console.log("Orders:", data);

    return data;
  } catch (error) {
    console.error("Orders backend error:", error);
    throw error;
  }
}
export async function requestReturn(orderId, reason, comment) {
  try {
    const token = localStorage.getItem("access_token");

    const response = await fetch(
      `${API_URL}/orders/${orderId}/return`,
      {
        method: "POST",

        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },

        body: JSON.stringify({
          reason: reason,
          comment: comment?.trim() || null,
        }),
      }
    );

    console.log("Return response:", response);

    if (!response.ok) {
      const errorData = await response.json().catch(() => null);

      throw new Error(
        errorData?.detail ||
        `HTTP error: ${response.status}`
      );
    }

    const data = await response.json();

    console.log("Return request:", data);

    return data;
  } catch (error) {
    console.error("Return request error:", error);
    throw error;
  }
}
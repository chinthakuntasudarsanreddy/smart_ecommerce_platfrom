const API_URL = "http://127.0.0.1:8000";

export async function getProducts() {
  try {
    const response = await fetch(`${API_URL}/products`);

    console.log("Backend response:", response);

    if (!response.ok) {
      throw new Error(`HTTP error: ${response.status}`);
    }

    const data = await response.json();

    console.log("Products:", data);

    return data;
  } catch (error) {
    console.error("Backend connection error:", error);
    throw error;
  }
}
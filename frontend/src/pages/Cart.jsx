
import { useEffect, useState } from "react";
import { useAuth0 } from "@auth0/auth0-react";

const API_URL =
  import.meta.env.VITE_API_URL ||
  "http://127.0.0.1:8000";

function Cart() {
  const [cart, setCart] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const {
    getAccessTokenSilently,
    isAuthenticated,
    isLoading: authLoading,
    loginWithRedirect,
  } = useAuth0();

  const loadCart = async () => {
    try {
      setLoading(true);
      setError("");

      const token = await getAccessTokenSilently();

      const response = await fetch(
        `${API_URL}/cart/`,
        {
          method: "GET",
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          },
        }
      );

      const data = await response
        .json()
        .catch(() => ({}));

      console.log(
        "GET /cart/:",
        response.status,
        data
      );

      if (response.status === 401) {
        throw new Error(
          "Your session is not authorized. Please log in again."
        );
      }

      if (!response.ok) {
        throw new Error(
          data.detail ||
            "Failed to load cart"
        );
      }

      setCart(data);
    } catch (err) {
      console.error("Cart error:", err);
      setError(
        err.message ||
          "Failed to load cart"
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (authLoading) {
      return;
    }

    if (!isAuthenticated) {
      setLoading(false);
      return;
    }

    loadCart();
  }, [authLoading, isAuthenticated]);

  const updateQuantity = async (
    productId,
    quantity
  ) => {
    const newQuantity = Number(quantity);

    if (newQuantity <= 0) {
      await removeItem(productId);
      return;
    }

    try {
      setError("");

      const token =
        await getAccessTokenSilently();

      const response = await fetch(
        `${API_URL}/cart/update`,
        {
          method: "PUT",
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            product_id: productId,
            quantity: newQuantity,
          }),
        }
      );

      const data = await response
        .json()
        .catch(() => ({}));

      console.log(
        "PUT /cart/update:",
        response.status,
        data
      );

      if (response.status === 401) {
        throw new Error(
          "Your session is not authorized. Please log in again."
        );
      }

      if (!response.ok) {
        throw new Error(
          data.detail ||
            "Failed to update quantity"
        );
      }

      setCart(data);
    } catch (err) {
      console.error(
        "Update cart error:",
        err
      );

      setError(
        err.message ||
          "Failed to update quantity"
      );
    }
  };

  const removeItem = async (productId) => {
    try {
      setError("");

      const token =
        await getAccessTokenSilently();

      const response = await fetch(
        `${API_URL}/cart/remove`,
        {
          method: "DELETE",
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            product_id: productId,
          }),
        }
      );

      const data = await response
        .json()
        .catch(() => ({}));

      console.log(
        "DELETE /cart/remove:",
        response.status,
        data
      );

      if (response.status === 401) {
        throw new Error(
          "Your session is not authorized. Please log in again."
        );
      }

      if (!response.ok) {
        throw new Error(
          data.detail ||
            "Failed to remove item"
        );
      }

      setCart(data);
    } catch (err) {
      console.error(
        "Remove cart item error:",
        err
      );

      setError(
        err.message ||
          "Failed to remove item"
      );
    }
  };

  if (authLoading) {
    return <h2>Checking authentication...</h2>;
  }

  if (!isAuthenticated) {
    return (
      <div>
        <h2>
          Please log in to view your cart.
        </h2>

        <button
          onClick={() =>
            loginWithRedirect()
          }
        >
          Login
        </button>
      </div>
    );
  }

  if (loading) {
    return <h2>Loading cart...</h2>;
  }

  if (error) {
    return (
      <div>
        <h2>Cart Error</h2>

        <p>{error}</p>

        <button onClick={loadCart}>
          Retry
        </button>
      </div>
    );
  }

  if (!cart) {
    return <h2>Cart is unavailable.</h2>;
  }

  if (
    !cart.items ||
    cart.items.length === 0
  ) {
    return (
      <div className="page">
        <h1>Shopping Cart 🛒</h1>

        <p>Your cart is empty.</p>

        <button
          onClick={() =>
            (window.location.href =
              "/products")
          }
        >
          Continue Shopping
        </button>
      </div>
    );
  }

  return (
    <div className="page">
      <h1>Shopping Cart 🛒</h1>

      {cart.items.map((item) => (
        <div
          key={item.product_id}
          className="cart-item"
        >
          <h3>{item.product_name}</h3>

          <p>
            Price: ₹{item.price}
          </p>

          <div>
            <button
              onClick={() =>
                updateQuantity(
                  item.product_id,
                  item.quantity - 1
                )
              }
            >
              −
            </button>

            <span
              style={{
                margin: "0 15px",
                fontWeight: "bold",
              }}
            >
              {item.quantity}
            </span>

            <button
              onClick={() =>
                updateQuantity(
                  item.product_id,
                  item.quantity + 1
                )
              }
            >
              +
            </button>
          </div>

          <p>
            Item Total: ₹
            {item.item_total}
          </p>

          <button
            onClick={() =>
              removeItem(item.product_id)
            }
          >
            🗑️ Remove
          </button>

          <hr />
        </div>
      ))}

      <div className="cart-summary">
        <h3>
          Cart Total: ₹
          {cart.cart_total}
        </h3>

        <h3>
          Tax (18%): ₹
          {cart.tax}
        </h3>

        <h2>
          Grand Total: ₹
          {cart.grand_total}
        </h2>

        <button
          onClick={() =>
            (window.location.href =
              "/payment")
          }
        >
          💳 Proceed to Payment
        </button>
      </div>
    </div>
  );
}

export default Cart;
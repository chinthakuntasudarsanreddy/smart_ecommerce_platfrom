import React, { useState } from "react";

const Cart = ({ cartItems = [] }) => {
  const [loading, setLoading] = useState(false);

  const handleCheckout = async () => {
    if (cartItems.length === 0) {
      alert("Your cart is empty");
      return;
    }

    try {
      setLoading(true);

      const response = await fetch(
        "http://127.0.0.1:8000/payment/create-checkout-session",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            items: cartItems.map((item) => ({
              product_id: item.id,
              name: item.name,
              price: item.price,
              quantity: item.quantity,
            })),
          }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        console.error("Backend error:", data);
        alert(data.detail || "Unable to start checkout");
        return;
      }

      if (data.checkout_url) {
        window.location.href = data.checkout_url;
      } else {
        alert("Checkout URL was not returned by the server");
      }
    } catch (error) {
      console.error("Checkout error:", error);
      alert("Unable to connect to payment server");
    } finally {
      setLoading(false);
    }
  };

  const totalAmount = cartItems.reduce(
    (total, item) => total + Number(item.price) * Number(item.quantity),
    0
  );

  return (
    <div>
      <h1>Shopping Cart</h1>

      {cartItems.length === 0 ? (
        <p>Your cart is empty.</p>
      ) : (
        <>
          {cartItems.map((item) => (
            <div key={item.id}>
              <h3>{item.name}</h3>
              <p>Price: ₹{item.price}</p>
              <p>Quantity: {item.quantity}</p>
              <p>
                Subtotal: ₹
                {Number(item.price) * Number(item.quantity)}
              </p>
            </div>
          ))}

          <hr />

          <h2>Total: ₹{totalAmount}</h2>

          <button onClick={handleCheckout} disabled={loading}>
            {loading ? "Processing..." : "Checkout & Pay"}
          </button>
        </>
      )}
    </div>
  );
};

export default Cart;
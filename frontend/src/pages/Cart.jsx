import { useEffect, useState } from "react";
import api from "../services/api";

function Cart() {
  const [cart, setCart] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchCart();
  }, []);

  const fetchCart = async () => {
    try {
      const response = await api.get("/cart");
      setCart(response.data);
    } catch (error) {
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <h2>Loading cart...</h2>;
  }

  if (!cart) {
    return <h2>Your cart is empty</h2>;
  }

  return (
    <div>
      <h1>Shopping Cart</h1>

      {cart.items?.map((item) => (
        <div key={item.id}>
          <h3>{item.product.name}</h3>

          <p>
            Price: ₹{item.product.price}
          </p>

          <p>
            Quantity: {item.quantity}
          </p>

          <p>
            Item Total: ₹{item.item_total}
          </p>
        </div>
      ))}

      <hr />

      <h2>
        Cart Total: ₹{cart.cart_total}
      </h2>

      <h2>
        Grand Total: ₹{cart.grand_total}
      </h2>
    </div>
  );
}

export default Cart;
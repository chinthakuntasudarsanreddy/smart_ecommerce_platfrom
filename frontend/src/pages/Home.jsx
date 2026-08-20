import { useEffect, useState } from "react";

function Cart() {
    const [cart, setCart] = useState(null);

    const userId = 2;

    const loadCart = async () => {
        try {
            const response = await fetch(
                `http://127.0.0.1:8000/cart/?user_id=${userId}`
            );

            if (!response.ok) {
                throw new Error("Failed to load cart");
            }

            const data = await response.json();
            setCart(data);
        } catch (error) {
            console.error(error);
        }
    };

    useEffect(() => {
        loadCart();
    }, []);

    const removeItem = async (productId) => {
        try {
            const response = await fetch(
                `http://127.0.0.1:8000/cart/remove?user_id=${userId}`,
                {
                    method: "DELETE",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({
                        product_id: productId
                    })
                }
            );

            if (!response.ok) {
                throw new Error("Failed to remove item");
            }

            const data = await response.json();
            setCart(data);
        } catch (error) {
            console.error(error);
        }
    };

    if (!cart) {
        return <h2>Loading cart...</h2>;
    }

    return (
        <div>
            <h1>Shopping Cart 🛒</h1>

            {cart.items.length === 0 ? (
                <p>Your cart is empty.</p>
            ) : (
                <>
                    {cart.items.map((item) => (
                        <div key={item.product_id}>
                            <h3>{item.product_name}</h3>

                            <p>
                                Price: ₹{item.price}
                            </p>

                            <p>
                                Quantity: {item.quantity}
                            </p>

                            <p>
                                Item Total: ₹{item.item_total}
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

                    <h3>
                        Cart Total: ₹{cart.cart_total}
                    </h3>

                    <h3>
                        Tax (18%): ₹{cart.tax}
                    </h3>

                    <h2>
                        Grand Total: ₹{cart.grand_total}
                    </h2>

                    <button
                        onClick={() =>
                            window.location.href = "/payment"
                        }
                    >
                        💳 Proceed to Payment
                    </button>
                </>
            )}
        </div>
    );
}

export default Cart;
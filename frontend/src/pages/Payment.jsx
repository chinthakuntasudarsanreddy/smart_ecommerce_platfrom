
import { useEffect, useState } from "react";
import { useAuth0 } from "@auth0/auth0-react";

const API_URL = "http://127.0.0.1:8000";

function Payment() {
    const {
        getAccessTokenSilently,
        isAuthenticated,
        user,
    } = useAuth0();

    const [cart, setCart] = useState(null);
    const [loadingCart, setLoadingCart] = useState(true);
    const [loadingPayment, setLoadingPayment] = useState(false);
    const [error, setError] = useState("");

    // =========================================================
    // LOAD CART
    // =========================================================

    useEffect(() => {
        const loadCart = async () => {
            try {
                setError("");

                if (!isAuthenticated) {
                    setError("Please login before making a payment.");
                    setLoadingCart(false);
                    return;
                }

                const token = await getAccessTokenSilently();

                const response = await fetch(
                    `${API_URL}/cart/`,
                    {
                        method: "GET",
                        headers: {
                            Authorization: `Bearer ${token}`,
                        },
                    }
                );

                const data = await response.json();

                console.log("Payment Cart:", data);

                if (!response.ok) {
                    throw new Error(
                        data.detail || "Failed to load cart"
                    );
                }

                setCart(data);

            } catch (error) {
                console.error("Cart loading error:", error);
                setError(error.message || "Failed to load cart.");
            } finally {
                setLoadingCart(false);
            }
        };

        loadCart();
    }, [isAuthenticated, getAccessTokenSilently]);

    // =========================================================
    // CREATE STRIPE CHECKOUT
    // =========================================================

    const handlePayment = async () => {
        try {
            setError("");

            if (!isAuthenticated) {
                setError("Please login before making a payment.");
                return;
            }

            if (!cart || !cart.items || cart.items.length === 0) {
                setError("Your cart is empty.");
                return;
            }

            setLoadingPayment(true);

            const token = await getAccessTokenSilently();

            // -------------------------------------------------
            // Get current user from backend
            // -------------------------------------------------

            const userResponse = await fetch(
                `${API_URL}/users/me`,
                {
                    method: "GET",
                    headers: {
                        Authorization: `Bearer ${token}`,
                    },
                }
            );

            const userData = await userResponse.json();

            console.log("Current backend user:", userData);

            if (!userResponse.ok) {
                throw new Error(
                    userData.detail || "Failed to get current user"
                );
            }

            // -------------------------------------------------
            // Build items required by CheckoutRequest
            // -------------------------------------------------

            const items = cart.items.map((item) => ({
                product_id: Number(item.product_id),
                name: item.product_name,
                price: Number(item.price),
                quantity: Number(item.quantity),
            }));

            const checkoutData = {
                user_id: Number(userData.id),
                items: items,
            };

            console.log(
                "Checkout request:",
                checkoutData
            );

            // -------------------------------------------------
            // Create Stripe Checkout Session
            // -------------------------------------------------

            const response = await fetch(
                `${API_URL}/payment/create-checkout-session`,
                {
                    method: "POST",
                    headers: {
                        Authorization: `Bearer ${token}`,
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify(checkoutData),
                }
            );

            const data = await response.json();

            console.log(
                "Payment API response:",
                data
            );

            if (!response.ok) {
                if (Array.isArray(data.detail)) {
                    const messages = data.detail
                        .map((error) => error.msg)
                        .join(", ");

                    throw new Error(messages);
                }

                throw new Error(
                    data.detail ||
                    "Failed to create payment session"
                );
            }

            // -------------------------------------------------
            // Redirect to Stripe
            // -------------------------------------------------

            if (data.checkout_url) {
                window.location.href =
                    data.checkout_url;
                return;
            }

            throw new Error(
                "Stripe checkout URL was not returned."
            );

        } catch (error) {
            console.error(
                "Payment error:",
                error
            );

            setError(
                error.message ||
                "Payment failed."
            );
        } finally {
            setLoadingPayment(false);
        }
    };

    // =========================================================
    // LOADING
    // =========================================================

    if (loadingCart) {
        return (
            <div className="page">
                <h1>Payment</h1>
                <p>Loading cart...</p>
            </div>
        );
    }

    // =========================================================
    // PAGE
    // =========================================================

    return (
        <div className="page">
            <h1>Payment</h1>

            <h2>Order Summary</h2>

            {cart?.items?.length > 0 ? (
                <div>
                    {cart.items.map((item) => (
                        <div
                            key={item.product_id}
                            style={{
                                marginBottom: "10px",
                            }}
                        >
                            <strong>
                                {item.product_name}
                            </strong>

                            <p>
                                ₹{item.price} ×{" "}
                                {item.quantity}
                                {" = "}
                                ₹{item.item_total}
                            </p>
                        </div>
                    ))}

                    <hr />

                    <p>
                        Cart Total: ₹
                        {cart.cart_total}
                    </p>

                    <p>
                        Tax: ₹
                        {cart.tax}
                    </p>

                    <h3>
                        Grand Total: ₹
                        {cart.grand_total}
                    </h3>
                </div>
            ) : (
                <p>Your cart is empty.</p>
            )}

            <h2>Payment Method</h2>

            <p>
                You will be redirected to Stripe
                Checkout to complete your payment.
            </p>

            {error && (
                <p
                    style={{
                        color: "red",
                        fontWeight: "bold",
                    }}
                >
                    {error}
                </p>
            )}

            <button
                onClick={handlePayment}
                disabled={
                    loadingPayment ||
                    !cart?.items?.length
                }
            >
                {loadingPayment
                    ? "Creating Checkout..."
                    : "💳 Pay Now"}
            </button>
        </div>
    );
}

export default Payment;


import React, { useEffect, useState } from "react";
import { Routes, Route } from "react-router-dom";
import { useAuth0 } from "@auth0/auth0-react";

import Navbar from "./components/Navbar";

import Home from "./pages/Home";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Products from "./pages/Products";
import Cart from "./pages/Cart";
import Profile from "./pages/Profile";
import Payment from "./pages/Payment";
import PaymentSuccess from "./pages/PaymentSuccess";
import Notifications from "./pages/Notifications";
import Orders from "./pages/Orders";
import AdminReturns from "./pages/AdminReturns";
import {
  connectNotificationSocket,
  disconnectNotificationSocket,
} from "./services/notificationSocket";

const API_URL =
  import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

function App() {
  const {
    isAuthenticated,
    isLoading,
    getAccessTokenSilently,
  } = useAuth0();

  const [cartItems, setCartItems] = useState([]);
  const [currentUserId, setCurrentUserId] = useState(null);

  // ============================================================
  // AUTH DEBUG
  // ============================================================

  useEffect(() => {
    console.log(
      "AUTH0 isAuthenticated =",
      isAuthenticated,
      "| isLoading =",
      isLoading
    );
  }, [isAuthenticated, isLoading]);

  // ============================================================
  // LOAD CURRENT USER
  // ============================================================

  useEffect(() => {
    const loadCurrentUser = async () => {
      if (isLoading) {
        return;
      }

      if (!isAuthenticated) {
        console.log("User is not authenticated.");

        setCurrentUserId(null);
        localStorage.removeItem("user_id");

        return;
      }

      try {
        console.log(
          "Authenticated. Getting Auth0 access token..."
        );

        const token = await getAccessTokenSilently();

        console.log("Auth0 access token received.");

        const response = await fetch(
          `${API_URL}/users/me`,
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

        if (!response.ok) {
          console.error(
            "Failed to load current user:",
            response.status,
            data
          );

          setCurrentUserId(null);
          return;
        }

        console.log(
          "FastAPI current user:",
          data
        );

        if (data?.id) {
          localStorage.setItem(
            "user_id",
            String(data.id)
          );

          setCurrentUserId(data.id);

          console.log(
            "Database user ID:",
            data.id
          );
        } else {
          console.error(
            "FastAPI did not return a user ID."
          );

          setCurrentUserId(null);
        }
      } catch (error) {
        console.error(
          "Failed to get FastAPI user:",
          error
        );

        setCurrentUserId(null);
      }
    };

    loadCurrentUser();
  }, [
    isAuthenticated,
    isLoading,
    getAccessTokenSilently,
  ]);

  // ============================================================
  // NOTIFICATION WEBSOCKET
  // ============================================================

  useEffect(() => {
    if (
      isLoading ||
      !isAuthenticated ||
      !currentUserId
    ) {
      return;
    }

    console.log(
      "Connecting notification WebSocket for user:",
      currentUserId
    );

    connectNotificationSocket(
      currentUserId,
      (notification) => {
        console.log(
          "New notification received:",
          notification
        );

        if (
          "Notification" in window &&
          Notification.permission === "granted"
        ) {
          new Notification(
            notification.type || "Notification",
            {
              body:
                notification.message || "",
            }
          );
        }
      }
    );

    return () => {
      console.log(
        "Disconnecting notification WebSocket."
      );

      disconnectNotificationSocket();
    };
  }, [
    isLoading,
    isAuthenticated,
    currentUserId,
  ]);

  // ============================================================
  // ADD TO CART - DATABASE
  // ============================================================

  const addToCart = async (product) => {
    try {
      if (!isAuthenticated) {
        alert(
          "Please log in to add products to your cart."
        );
        return;
      }

      console.log(
        "Adding product to cart:",
        product
      );

      const token =
        await getAccessTokenSilently();

      const response = await fetch(
        `${API_URL}/cart/add`,
        {
          method: "POST",
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            product_id: product.id,
            quantity: 1,
          }),
        }
      );

      const data = await response
        .json()
        .catch(() => ({}));

      console.log(
        "POST /cart/add:",
        response.status,
        data
      );

      if (response.status === 401) {
        alert(
          "Your session is not authorized. Please log in again."
        );
        return;
      }

      if (!response.ok) {
        alert(
          data.detail ||
            "Failed to add product to cart."
        );
        return;
      }

      // Keep frontend state synchronized
      if (data.items) {
        setCartItems(data.items);
      }

      alert(
        `${product.name} added to cart`
      );
    } catch (error) {
      console.error(
        "Add to cart error:",
        error
      );

      alert(
        error.message ||
          "Failed to add product to cart."
      );
    }
  };

  // ============================================================
  // REMOVE FROM LOCAL STATE
  // ============================================================

  const removeFromCart = (productId) => {
    setCartItems((currentItems) =>
      currentItems.filter(
        (item) =>
          item.product_id !== productId &&
          item.id !== productId
      )
    );
  };

  // ============================================================
  // UPDATE LOCAL STATE
  // ============================================================

  const updateCartQuantity = (
    productId,
    quantity
  ) => {
    const newQuantity = Number(quantity);

    if (newQuantity <= 0) {
      removeFromCart(productId);
      return;
    }

    setCartItems((currentItems) =>
      currentItems.map((item) =>
        item.product_id === productId ||
        item.id === productId
          ? {
              ...item,
              quantity: newQuantity,
            }
          : item
      )
    );
  };

  // ============================================================
  // CLEAR CART
  // ============================================================

  const clearCart = () => {
    setCartItems([]);
  };

  // ============================================================
  // ROUTES
  // ============================================================

  return (
    <>
      <Navbar />

      <Routes>
        <Route
          path="/"
          element={<Home />}
        />

        <Route
          path="/login"
          element={<Login />}
        />

        <Route
          path="/register"
          element={<Register />}
        />

        <Route
          path="/products"
          element={
            <Products
              addToCart={addToCart}
            />
          }
        />

        <Route
          path="/cart"
          element={<Cart />}
        />

        <Route
          path="/profile"
          element={<Profile />}
        />

        <Route
          path="/payment"
          element={<Payment />}
        />

        <Route
          path="/payment-success"
          element={
            <PaymentSuccess
              clearCart={clearCart}
            />
          }
        />

        <Route
          path="/notifications"
          element={
            <Notifications
              userId={currentUserId}
            />
          }
        />

        <Route
          path="/orders"
          element={<Orders />}
        />
        <Route
  path="/admin/returns"
  element={<AdminReturns />}
/>
      </Routes>
    </>
  );
}

export default App;

import { useEffect } from "react";
import {
  Routes,
  Route
} from "react-router-dom";

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
import {
  connectNotificationSocket,
  disconnectNotificationSocket
} from "./services/notificationSocket";
import Orders from "./pages/Orders";

function App() {

  useEffect(() => {

    // Temporary testing user ID
    const userId = 1;

    const socket = connectNotificationSocket(
      userId,
      (notification) => {

        console.log(
          "New notification received:",
          notification
        );

        // Browser notification
        if (
          "Notification" in window &&
          Notification.permission === "granted"
        ) {
          new Notification(
            notification.type,
            {
              body: notification.message
            }
          );
        }
      }
    );

    return () => {
      disconnectNotificationSocket();
    };

  }, []);


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
          element={<Products />}
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
          element={<PaymentSuccess />}
        />

        <Route
          path="/notifications"
          element={<Notifications userId={1} />}
        />
        <Route
    path="/orders"
    element={<Orders />}
/>

      </Routes>
    </>
  );
}

export default App;
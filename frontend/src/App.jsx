import { Routes, Route } from "react-router-dom";

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
function App() {
  return (
    <>
      <Navbar />

      <Routes>
        <Route path="/" element={<Home />} />

        <Route path="/login" element={<Login />} />

        <Route path="/register" element={<Register />} />

        <Route path="/products" element={<Products />} />

        <Route path="/cart" element={<Cart />} />

        <Route path="/profile" element={<Profile />} />

        <Route path="/payment" element={<Payment />} />

        <Route
          path="/payment-success"
          element={<PaymentSuccess />}
        />
        <Route
  path="/notifications"
  element={<Notifications userId={1} />}
/>
      </Routes>
    </>
  );
}

export default App;
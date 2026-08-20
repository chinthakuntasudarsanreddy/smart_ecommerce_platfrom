import React from "react";
import { Link } from "react-router-dom";

const PaymentSuccess = () => {
  return (
    <div>
      <h1>Payment Successful!</h1>

      <p>
        Thank you for your purchase.
        Your order has been placed successfully.
      </p>

      <Link to="/">
        Continue Shopping
      </Link>
    </div>
  );
};

export default PaymentSuccess;
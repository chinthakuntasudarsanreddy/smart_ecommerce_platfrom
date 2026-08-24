import { useEffect, useState } from "react";

function PaymentSuccess() {

  const [status, setStatus] = useState(
    "checking"
  );

  const [message, setMessage] = useState("");

  useEffect(() => {

    const params =
      new URLSearchParams(
        window.location.search
      );

    const sessionId =
      params.get("session_id");


    if (!sessionId) {

      setStatus("failed");

      setMessage(
        "Payment session was not found."
      );

      return;
    }


    const verifyPayment = async () => {

      try {

        const response = await fetch(

          `http://127.0.0.1:8000/` +
          `payment/verify-session/` +
          sessionId

        );


        const data =
          await response.json();


        if (!response.ok) {

          setStatus("failed");

          setMessage(
            data.detail ||
            "Payment verification failed."
          );

          return;
        }


        if (data.success) {

          setStatus("success");

          setMessage(
            data.message
          );

        } else {

          setStatus("failed");

          setMessage(
            data.message ||
            "Payment failed."
          );

        }

      } catch (error) {

        console.error(
          "Payment verification error:",
          error
        );

        setStatus("failed");

        setMessage(
          "Unable to verify payment."
        );

      }

    };


    verifyPayment();

  }, []);


  if (status === "checking") {

    return (

      <div>

        <h1>
          Checking Payment...
        </h1>

        <p>
          Please wait while we verify your payment.
        </p>

      </div>

    );

  }


  if (status === "success") {

    return (

      <div>

        <h1>
          🎉 Payment Successful
        </h1>

        <h2>
          📦 Order Confirmed
        </h2>

        <p>
          {message}
        </p>

        <p>
          Thank you for shopping with us!
        </p>

      </div>

    );

  }


  return (

    <div>

      <h1>
        ❌ Payment Failed
      </h1>

      <p>
        {message}
      </p>

    </div>

  );

}


export default PaymentSuccess;
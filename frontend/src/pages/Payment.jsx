function Payment() {

    const handlePayment = () => {
        alert("Payment processing started...");
    };

    return (
        <div>
            <h1>Payment</h1>

            <h2>Choose Payment Method</h2>

            <label>
                <input
                    type="radio"
                    name="payment"
                    defaultChecked
                />
                UPI
            </label>

            <br />

            <label>
                <input
                    type="radio"
                    name="payment"
                />
                Credit / Debit Card
            </label>

            <br />

            <label>
                <input
                    type="radio"
                    name="payment"
                />
                Cash on Delivery
            </label>

            <br />
            <br />

            <button onClick={handlePayment}>
                💳 Pay Now
            </button>
        </div>
    );
}

export default Payment;
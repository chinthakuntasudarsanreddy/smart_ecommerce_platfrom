import React, { useEffect, useState } from "react";
import axios from "axios";
import { useAuth0 } from "@auth0/auth0-react";

const API_URL = "http://127.0.0.1:8000";

const Order = () => {
  const {
    isAuthenticated,
    isLoading: authLoading,
    getAccessTokenSilently,
    loginWithRedirect,
  } = useAuth0();

  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  // Return request
  const [selectedOrder, setSelectedOrder] = useState(null);
  const [reason, setReason] = useState("");
  const [comment, setComment] = useState("");
  const [returnLoading, setReturnLoading] = useState(false);

  // ============================================================
  // GET AUTH0 ACCESS TOKEN
  // ============================================================

  const getToken = async () => {
    if (!isAuthenticated) {
      throw new Error("Please login first.");
    }

    try {
      const token = await getAccessTokenSilently();
      return token;
    } catch (err) {
      console.error("Auth0 token error:", err);
      throw new Error("Unable to get Auth0 access token.");
    }
  };

  // ============================================================
  // FETCH ORDERS
  // ============================================================

  const fetchOrders = async () => {
    try {
      setLoading(true);
      setError("");

      if (!isAuthenticated) {
        setError("Please login first.");
        return;
      }

      const token = await getToken();

      const response = await axios.get(
        `${API_URL}/orders/`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      console.log("Orders API response:", response.data);

      if (Array.isArray(response.data)) {
        setOrders(response.data);
      } else if (Array.isArray(response.data.orders)) {
        setOrders(response.data.orders);
      } else {
        setOrders([]);
      }
    } catch (err) {
      console.error("Fetch orders error:", err);

      if (err.response?.status === 401) {
        setError(
          "Authentication failed. Please login again."
        );
      } else {
        setError(
          err.response?.data?.detail ||
            err.response?.data?.message ||
            err.message ||
            "Unable to load orders."
        );
      }
    } finally {
      setLoading(false);
    }
  };

  // ============================================================
  // LOAD ORDERS
  // ============================================================

  useEffect(() => {
    if (!authLoading) {
      if (isAuthenticated) {
        fetchOrders();
      } else {
        setLoading(false);
        setError("Please login first.");
      }
    }
  }, [authLoading, isAuthenticated]);

  // ============================================================
  // OPEN RETURN FORM
  // ============================================================

  const openReturnForm = (order) => {
    setSelectedOrder(order);
    setReason("");
    setComment("");
  };

  // ============================================================
  // CLOSE RETURN FORM
  // ============================================================

  const closeReturnForm = () => {
    if (returnLoading) {
      return;
    }

    setSelectedOrder(null);
    setReason("");
    setComment("");
  };

  // ============================================================
  // SUBMIT RETURN REQUEST
  // ============================================================

  const handleReturnRequest = async () => {
    if (!selectedOrder) {
      alert("Order not selected.");
      return;
    }

    if (!reason) {
      alert("Please select a return reason.");
      return;
    }

    try {
      setReturnLoading(true);

      const token = await getToken();

      console.log(
        "Submitting return for order:",
        selectedOrder.id
      );

      const response = await axios.post(
        `${API_URL}/orders/${selectedOrder.id}/return`,
        {
          reason: reason,
          comment: comment.trim() || null,
        },
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      console.log(
        "Return request response:",
        response.data
      );

      alert(
        "Return request submitted successfully!"
      );

      closeReturnForm();

      // Reload orders so the latest backend status appears
      await fetchOrders();
    } catch (err) {
      console.error(
        "Return request error:",
        err
      );

      const message =
        err.response?.data?.detail ||
        err.response?.data?.message ||
        err.message ||
        "Failed to submit return request.";

      alert(message);
    } finally {
      setReturnLoading(false);
    }
  };

  // ============================================================
  // STATUS TEXT
  // ============================================================

  const getStatusText = (status) => {
    const normalizedStatus = String(
      status || ""
    ).toLowerCase();

    switch (normalizedStatus) {
      case "pending":
        return "Pending";

      case "paid":
        return "Paid";

      case "shipped":
        return "Shipped";

      case "delivered":
        return "Delivered";

      case "return_requested":
        return "Return Requested";

      case "returned":
        return "Returned";

      case "rejected":
        return "Rejected";

      case "refunded":
        return "Refunded";

      case "cancelled":
        return "Cancelled";

      default:
        return status || "Unknown";
    }
  };

  // ============================================================
  // STATUS COLOR
  // ============================================================

  const getStatusColor = (status) => {
    const normalizedStatus = String(
      status || ""
    ).toLowerCase();

    switch (normalizedStatus) {
      case "pending":
        return "#6c757d";

      case "paid":
        return "#0d6efd";

      case "shipped":
        return "#6f42c1";

      case "delivered":
        return "#198754";

      case "return_requested":
        return "#fd7e14";

      case "returned":
        return "#20c997";

      case "rejected":
        return "#dc3545";

      case "refunded":
        return "#198754";

      case "cancelled":
        return "#dc3545";

      default:
        return "#6c757d";
    }
  };

  // ============================================================
  // AUTH0 LOADING
  // ============================================================

  if (authLoading) {
    return (
      <div
        style={{
          maxWidth: "1000px",
          margin: "30px auto",
          padding: "20px",
        }}
      >
        <h1>My Orders</h1>
        <p>Checking login...</p>
      </div>
    );
  }

  // ============================================================
  // NOT AUTHENTICATED
  // ============================================================

  if (!isAuthenticated) {
    return (
      <div
        style={{
          maxWidth: "1000px",
          margin: "30px auto",
          padding: "20px",
          textAlign: "center",
        }}
      >
        <h1>My Orders</h1>

        <p>Please login to view your orders.</p>

        <button
          onClick={() => loginWithRedirect()}
          style={{
            padding: "12px 20px",
            border: "none",
            borderRadius: "6px",
            background: "#0d6efd",
            color: "#fff",
            cursor: "pointer",
            fontWeight: "bold",
          }}
        >
          Login
        </button>
      </div>
    );
  }

  // ============================================================
  // LOADING
  // ============================================================

  if (loading) {
    return (
      <div
        style={{
          maxWidth: "1000px",
          margin: "30px auto",
          padding: "20px",
        }}
      >
        <h1>My Orders</h1>
        <p>Loading orders...</p>
      </div>
    );
  }

  // ============================================================
  // ERROR
  // ============================================================

  if (error) {
    return (
      <div
        style={{
          maxWidth: "1000px",
          margin: "30px auto",
          padding: "20px",
        }}
      >
        <h1>My Orders</h1>

        <div
          style={{
            padding: "20px",
            background: "#f8d7da",
            border: "1px solid #f5c2c7",
            borderRadius: "8px",
            color: "#842029",
          }}
        >
          <h3>Unable to load orders</h3>

          <p>{error}</p>

          <button
            onClick={fetchOrders}
            style={{
              padding: "10px 18px",
              border: "none",
              borderRadius: "6px",
              cursor: "pointer",
            }}
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  // ============================================================
  // MAIN UI
  // ============================================================

  return (
    <div
      style={{
        maxWidth: "1000px",
        margin: "30px auto",
        padding: "20px",
      }}
    >
      {/* HEADER */}

      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          marginBottom: "25px",
        }}
      >
        <h1>My Orders</h1>

        <button
          onClick={fetchOrders}
          style={{
            padding: "10px 18px",
            border: "none",
            borderRadius: "6px",
            cursor: "pointer",
          }}
        >
          Refresh
        </button>
      </div>

      {/* NO ORDERS */}

      {orders.length === 0 ? (
        <div
          style={{
            padding: "40px",
            textAlign: "center",
            border: "1px solid #ddd",
            borderRadius: "10px",
          }}
        >
          <h2>No Orders Found</h2>

          <p>
            You haven't placed any orders yet.
          </p>
        </div>
      ) : (
        <div>
          {orders.map((order) => {
            // ==================================================
            // BACKEND ORDER STATUS
            // ==================================================

            const orderStatus = String(
              order.order_status || ""
            ).toLowerCase();

            const paymentStatus = String(
              order.payment_status || ""
            ).toLowerCase();

            // ==================================================
            // STATUS FLAGS
            // ==================================================

            const isDelivered =
              orderStatus === "delivered";

            const isReturnRequested =
              orderStatus === "return_requested";

            const isReturned =
              orderStatus === "returned";

            const isRejected =
              orderStatus === "rejected";

            const isRefunded =
              orderStatus === "refunded" ||
              paymentStatus === "refunded";

            // ==================================================
            // RETURN ALREADY STARTED
            // ==================================================

            const returnAlreadyStarted =
              isReturnRequested ||
              isReturned ||
              isRejected ||
              isRefunded;

            return (
              <div
                key={order.id}
                style={{
                  border: "1px solid #ddd",
                  borderRadius: "12px",
                  padding: "20px",
                  marginBottom: "20px",
                  background: "#fff",
                  boxShadow:
                    "0 2px 8px rgba(0,0,0,0.08)",
                }}
              >
                {/* ============================================
                    ORDER HEADER
                ============================================ */}

                <div
                  style={{
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                    flexWrap: "wrap",
                    gap: "10px",
                  }}
                >
                  <div>
                    <h2>
                      Order #{order.id}
                    </h2>

                    {order.created_at && (
                      <p>
                        Ordered:{" "}
                        {new Date(
                          order.created_at
                        ).toLocaleDateString()}
                      </p>
                    )}
                  </div>

                  <span
                    style={{
                      padding: "8px 14px",
                      borderRadius: "20px",
                      color: "#fff",
                      background:
                        getStatusColor(
                          orderStatus
                        ),
                      fontWeight: "bold",
                    }}
                  >
                    {getStatusText(
                      orderStatus
                    )}
                  </span>
                </div>

                {/* ============================================
                    ORDER DETAILS
                ============================================ */}

                <div
                  style={{
                    marginTop: "15px",
                  }}
                >
                  <p>
                    <strong>Total:</strong> ₹
                    {Number(
                      order.total || 0
                    ).toFixed(2)}
                  </p>

                  <p>
                    <strong>
                      Payment Status:
                    </strong>{" "}
                    {getStatusText(
                      paymentStatus
                    )}
                  </p>

                  <p>
                    <strong>
                      Order Status:
                    </strong>{" "}
                    {getStatusText(
                      orderStatus
                    )}
                  </p>
                </div>

                {/* ============================================
                    RETURN REQUESTED
                ============================================ */}

                {isReturnRequested && (
                  <div
                    style={{
                      marginTop: "15px",
                      padding: "15px",
                      borderRadius: "8px",
                      background: "#fff3cd",
                      border:
                        "1px solid #ffecb5",
                      color: "#664d03",
                    }}
                  >
                    <strong>
                      Return Request Submitted
                    </strong>

                    <p>
                      Your return request is
                      waiting for admin approval.
                    </p>
                  </div>
                )}

                {/* ============================================
                    RETURNED
                ============================================ */}

                {isReturned && !isRefunded && (
                  <div
                    style={{
                      marginTop: "15px",
                      padding: "15px",
                      borderRadius: "8px",
                      background: "#d1e7dd",
                      border:
                        "1px solid #badbcc",
                      color: "#0f5132",
                    }}
                  >
                    <strong>
                      Return Completed
                    </strong>

                    <p>
                      Your return has been
                      approved and the product
                      has been marked as returned.
                    </p>
                  </div>
                )}

                {/* ============================================
                    REJECTED
                ============================================ */}

                {isRejected && (
                  <div
                    style={{
                      marginTop: "15px",
                      padding: "15px",
                      borderRadius: "8px",
                      background: "#f8d7da",
                      border:
                        "1px solid #f5c2c7",
                      color: "#842029",
                    }}
                  >
                    <strong>
                      Return Rejected
                    </strong>

                    <p>
                      Your return request was
                      rejected by the admin.
                    </p>

                    {order.rejection_reason && (
                      <p>
                        <strong>
                          Reason:
                        </strong>{" "}
                        {order.rejection_reason}
                      </p>
                    )}
                  </div>
                )}

                {/* ============================================
                    REFUNDED
                ============================================ */}

                {isRefunded && (
                  <div
                    style={{
                      marginTop: "15px",
                      padding: "15px",
                      borderRadius: "8px",
                      background: "#d1e7dd",
                      border:
                        "1px solid #badbcc",
                      color: "#0f5132",
                    }}
                  >
                    <strong>
                      Refund Completed
                    </strong>

                    <p>
                      Your refund has been
                      successfully processed.
                    </p>
                  </div>
                )}

                {/* ============================================
                    ACTION BUTTONS
                ============================================ */}

                <div
                  style={{
                    marginTop: "20px",
                  }}
                >
                  {/* REQUEST RETURN */}

                  {isDelivered &&
                    !returnAlreadyStarted && (
                      <button
                        onClick={() =>
                          openReturnForm(order)
                        }
                        style={{
                          padding:
                            "11px 20px",
                          background:
                            "#dc3545",
                          color: "#fff",
                          border: "none",
                          borderRadius: "6px",
                          cursor: "pointer",
                          fontWeight: "bold",
                        }}
                      >
                        Request Return
                      </button>
                    )}

                  {/* RETURN REQUESTED */}

                  {isReturnRequested && (
                    <button
                      disabled
                      style={{
                        padding:
                          "11px 20px",
                        background:
                          "#fd7e14",
                        color: "#fff",
                        border: "none",
                        borderRadius: "6px",
                      }}
                    >
                      Return Requested
                    </button>
                  )}

                  {/* RETURNED */}

                  {isReturned &&
                    !isRefunded && (
                      <button
                        disabled
                        style={{
                          padding:
                            "11px 20px",
                          background:
                            "#20c997",
                          color: "#fff",
                          border: "none",
                          borderRadius: "6px",
                        }}
                      >
                        Returned
                      </button>
                    )}

                  {/* REJECTED */}

                  {isRejected && (
                    <button
                      disabled
                      style={{
                        padding:
                          "11px 20px",
                        background:
                          "#dc3545",
                        color: "#fff",
                        border: "none",
                        borderRadius: "6px",
                      }}
                    >
                      Return Rejected
                    </button>
                  )}

                  {/* REFUNDED */}

                  {isRefunded && (
                    <button
                      disabled
                      style={{
                        padding:
                          "11px 20px",
                        background:
                          "#198754",
                        color: "#fff",
                        border: "none",
                        borderRadius: "6px",
                      }}
                    >
                      Refunded
                    </button>
                  )}
                </div>

                {/* ============================================
                    RETURN FORM
                ============================================ */}

                {selectedOrder?.id ===
                  order.id && (
                  <div
                    style={{
                      marginTop: "25px",
                      padding: "20px",
                      border:
                        "1px solid #ccc",
                      borderRadius: "10px",
                      background:
                        "#f8f9fa",
                    }}
                  >
                    <h3>
                      Request Return
                    </h3>

                    <p>
                      <strong>Order:</strong>{" "}
                      #{order.id}
                    </p>

                    {/* RETURN REASON */}

                    <div
                      style={{
                        marginBottom: "15px",
                      }}
                    >
                      <label>
                        <strong>
                          Return Reason
                        </strong>
                      </label>

                      <select
                        value={reason}
                        onChange={(e) =>
                          setReason(
                            e.target.value
                          )
                        }
                        disabled={
                          returnLoading
                        }
                        style={{
                          display: "block",
                          width: "100%",
                          padding: "10px",
                          marginTop: "6px",
                          border:
                            "1px solid #ccc",
                          borderRadius:
                            "6px",
                        }}
                      >
                        <option value="">
                          Select a reason
                        </option>

                        <option value="Damaged product">
                          Damaged product
                        </option>

                        <option value="Wrong product">
                          Wrong product
                        </option>

                        <option value="Product not as described">
                          Product not as
                          described
                        </option>

                        <option value="Missing item">
                          Missing item
                        </option>

                        <option value="Size issue">
                          Size issue
                        </option>

                        <option value="Quality issue">
                          Quality issue
                        </option>

                        <option value="Changed my mind">
                          Changed my mind
                        </option>

                        <option value="Other">
                          Other
                        </option>
                      </select>
                    </div>

                    {/* COMMENT */}

                    <div
                      style={{
                        marginBottom: "15px",
                      }}
                    >
                      <label>
                        <strong>
                          Comment
                        </strong>{" "}
                        (Optional)
                      </label>

                      <textarea
                        value={comment}
                        onChange={(e) =>
                          setComment(
                            e.target.value
                          )
                        }
                        disabled={
                          returnLoading
                        }
                        placeholder="Explain why you want to return this product..."
                        rows="5"
                        style={{
                          display: "block",
                          width: "100%",
                          padding: "10px",
                          marginTop: "6px",
                          border:
                            "1px solid #ccc",
                          borderRadius:
                            "6px",
                          resize: "vertical",
                        }}
                      />
                    </div>

                    {/* FORM BUTTONS */}

                    <div>
                      <button
                        onClick={
                          handleReturnRequest
                        }
                        disabled={
                          returnLoading ||
                          !reason
                        }
                        style={{
                          padding:
                            "11px 20px",
                          marginRight:
                            "10px",
                          background:
                            returnLoading ||
                            !reason
                              ? "#999"
                              : "#198754",
                          color: "#fff",
                          border: "none",
                          borderRadius:
                            "6px",
                          cursor:
                            returnLoading ||
                            !reason
                              ? "not-allowed"
                              : "pointer",
                        }}
                      >
                        {returnLoading
                          ? "Submitting..."
                          : "Submit Return Request"}
                      </button>

                      <button
                        onClick={
                          closeReturnForm
                        }
                        disabled={
                          returnLoading
                        }
                        style={{
                          padding:
                            "11px 20px",
                          background:
                            "#fff",
                          border:
                            "1px solid #ccc",
                          borderRadius:
                            "6px",
                          cursor:
                            "pointer",
                        }}
                      >
                        Cancel
                      </button>
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};

export default Order;
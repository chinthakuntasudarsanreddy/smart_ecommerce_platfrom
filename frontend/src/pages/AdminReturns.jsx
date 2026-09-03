import React, { useEffect, useState } from "react";
import axios from "axios";
import { useAuth0 } from "@auth0/auth0-react";

const API_URL = "http://127.0.0.1:8000";

const AdminReturns = () => {
  const {
    isAuthenticated,
    isLoading: authLoading,
    getAccessTokenSilently,
    loginWithRedirect,
  } = useAuth0();

  const [returns, setReturns] = useState([]);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(null);
  const [error, setError] = useState("");

  // Reject modal/form
  const [selectedReturn, setSelectedReturn] = useState(null);
  const [rejectionReason, setRejectionReason] = useState("");

  // ============================================================
  // GET TOKEN
  // ============================================================

  const getToken = async () => {
    if (!isAuthenticated) {
      throw new Error("Please login first.");
    }

    try {
      return await getAccessTokenSilently();
    } catch (err) {
      console.error("Auth0 token error:", err);
      throw new Error("Unable to get Auth0 access token.");
    }
  };

  // ============================================================
  // FETCH RETURNS
  // ============================================================

  const fetchReturns = async () => {
    try {
      setLoading(true);
      setError("");

      const token = await getToken();

      const response = await axios.get(
        `${API_URL}/admin/returns`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      console.log("Admin returns response:", response.data);

      if (Array.isArray(response.data)) {
        setReturns(response.data);
      } else if (Array.isArray(response.data.returns)) {
        setReturns(response.data.returns);
      } else {
        setReturns([]);
      }
    } catch (err) {
      console.error("Fetch returns error:", err);

      setError(
        err.response?.data?.detail ||
          err.response?.data?.message ||
          err.message ||
          "Unable to load return requests."
      );
    } finally {
      setLoading(false);
    }
  };

  // ============================================================
  // LOAD
  // ============================================================

  useEffect(() => {
    if (!authLoading && isAuthenticated) {
      fetchReturns();
    } else if (!authLoading && !isAuthenticated) {
      setLoading(false);
    }
  }, [authLoading, isAuthenticated]);

  // ============================================================
  // APPROVE RETURN
  // ============================================================

  const approveReturn = async (returnId) => {
    const confirmed = window.confirm(
      "Are you sure you want to approve this return?"
    );

    if (!confirmed) {
      return;
    }

    try {
      setActionLoading(returnId);

      const token = await getToken();

      await axios.post(
        `${API_URL}/admin/returns/${returnId}/approve`,
        {},
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      alert("Return approved successfully.");

      await fetchReturns();
    } catch (err) {
      console.error("Approve return error:", err);

      alert(
        err.response?.data?.detail ||
          err.response?.data?.message ||
          "Failed to approve return."
      );
    } finally {
      setActionLoading(null);
    }
  };

  // ============================================================
  // OPEN REJECT FORM
  // ============================================================

  const openRejectForm = (returnRequest) => {
    setSelectedReturn(returnRequest);
    setRejectionReason("");
  };

  // ============================================================
  // CLOSE REJECT FORM
  // ============================================================

  const closeRejectForm = () => {
    if (actionLoading) {
      return;
    }

    setSelectedReturn(null);
    setRejectionReason("");
  };

  // ============================================================
  // REJECT RETURN
  // ============================================================

  const rejectReturn = async () => {
    if (!selectedReturn) {
      return;
    }

    if (!rejectionReason.trim()) {
      alert("Please enter a rejection reason.");
      return;
    }

    try {
      setActionLoading(selectedReturn.id);

      const token = await getToken();

      await axios.post(
        `${API_URL}/admin/returns/${selectedReturn.id}/reject`,
        {
          rejection_reason: rejectionReason.trim(),
        },
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      alert("Return rejected successfully.");

      closeRejectForm();

      await fetchReturns();
    } catch (err) {
      console.error("Reject return error:", err);

      alert(
        err.response?.data?.detail ||
          err.response?.data?.message ||
          "Failed to reject return."
      );
    } finally {
      setActionLoading(null);
    }
  };

  // ============================================================
  // REFUND
  // ============================================================

  const processRefund = async (returnId) => {
    const confirmed = window.confirm(
      "Are you sure you want to process the refund?"
    );

    if (!confirmed) {
      return;
    }

    try {
      setActionLoading(returnId);

      const token = await getToken();

      /*
       * Your backend should expose:
       *
       * POST /admin/returns/{id}/refund
       *
       * The backend handles Stripe securely.
       */

      await axios.post(
        `${API_URL}/admin/returns/${returnId}/refund`,
        {},
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      alert("Refund processed successfully.");

      await fetchReturns();
    } catch (err) {
      console.error("Refund error:", err);

      alert(
        err.response?.data?.detail ||
          err.response?.data?.message ||
          "Failed to process refund."
      );
    } finally {
      setActionLoading(null);
    }
  };

  // ============================================================
  // STATUS TEXT
  // ============================================================

  const getStatusText = (status) => {
    const value = String(status || "").toLowerCase();

    switch (value) {
      case "requested":
        return "Requested";

      case "approved":
        return "Approved";

      case "rejected":
        return "Rejected";

      case "returned":
        return "Returned";

      case "refunded":
        return "Refunded";

      default:
        return status || "Unknown";
    }
  };

  // ============================================================
  // STATUS COLOR
  // ============================================================

  const getStatusColor = (status) => {
    const value = String(status || "").toLowerCase();

    switch (value) {
      case "requested":
        return "#fd7e14";

      case "approved":
        return "#20c997";

      case "returned":
        return "#0d6efd";

      case "refunded":
        return "#198754";

      case "rejected":
        return "#dc3545";

      default:
        return "#6c757d";
    }
  };

  // ============================================================
  // LOADING
  // ============================================================

  if (authLoading || loading) {
    return (
      <div
        style={{
          maxWidth: "1200px",
          margin: "30px auto",
          padding: "20px",
        }}
      >
        <h1>Return Management</h1>
        <p>Loading return requests...</p>
      </div>
    );
  }

  // ============================================================
  // LOGIN
  // ============================================================

  if (!isAuthenticated) {
    return (
      <div
        style={{
          maxWidth: "1000px",
          margin: "50px auto",
          padding: "30px",
          textAlign: "center",
        }}
      >
        <h1>Admin Return Management</h1>

        <p>Please login to access return management.</p>

        <button
          onClick={() => loginWithRedirect()}
          style={{
            padding: "12px 25px",
            background: "#0d6efd",
            color: "#fff",
            border: "none",
            borderRadius: "6px",
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
  // ERROR
  // ============================================================

  if (error) {
    return (
      <div
        style={{
          maxWidth: "1200px",
          margin: "30px auto",
          padding: "20px",
        }}
      >
        <h1>Return Management</h1>

        <div
          style={{
            padding: "20px",
            background: "#f8d7da",
            color: "#842029",
            borderRadius: "8px",
            border: "1px solid #f5c2c7",
          }}
        >
          <h3>Unable to load returns</h3>

          <p>{error}</p>

          <button
            onClick={fetchReturns}
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
        maxWidth: "1200px",
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
          flexWrap: "wrap",
          gap: "10px",
        }}
      >
        <div>
          <h1>Return Management</h1>

          <p>
            Manage customer return requests and refunds.
          </p>
        </div>

        <button
          onClick={fetchReturns}
          style={{
            padding: "10px 18px",
            border: "none",
            borderRadius: "6px",
            cursor: "pointer",
            background: "#6c757d",
            color: "#fff",
          }}
        >
          Refresh
        </button>
      </div>

      {/* NO RETURNS */}

      {returns.length === 0 ? (
        <div
          style={{
            padding: "50px",
            textAlign: "center",
            border: "1px solid #ddd",
            borderRadius: "10px",
            background: "#fff",
          }}
        >
          <h2>No Return Requests</h2>

          <p>
            There are currently no return requests.
          </p>
        </div>
      ) : (
        <div>
          {returns.map((item) => {
            const status = String(
              item.status || ""
            ).toLowerCase();

            const isRequested =
              status === "requested";

            const isApproved =
              status === "approved";

            const isReturned =
              status === "returned";

            const isRejected =
              status === "rejected";

            const isRefunded =
              status === "refunded";

            const busy =
              actionLoading === item.id;

            return (
              <div
                key={item.id}
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
                {/* TOP */}

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
                      Return #{item.id}
                    </h2>

                    <p>
                      <strong>
                        Order:
                      </strong>{" "}
                      #{item.order_id}
                    </p>
                  </div>

                  <span
                    style={{
                      padding: "8px 15px",
                      borderRadius: "20px",
                      background:
                        getStatusColor(status),
                      color: "#fff",
                      fontWeight: "bold",
                    }}
                  >
                    {getStatusText(status)}
                  </span>
                </div>

                {/* DETAILS */}

                <div
                  style={{
                    marginTop: "15px",
                    padding: "15px",
                    background: "#f8f9fa",
                    borderRadius: "8px",
                  }}
                >
                  <p>
                    <strong>
                      Customer ID:
                    </strong>{" "}
                    {item.user_id ?? "N/A"}
                  </p>

                  <p>
                    <strong>
                      Reason:
                    </strong>{" "}
                    {item.reason || "N/A"}
                  </p>

                  {item.comment && (
                    <p>
                      <strong>
                        Comment:
                      </strong>{" "}
                      {item.comment}
                    </p>
                  )}

                  <p>
                    <strong>
                      Refund Amount:
                    </strong>{" "}
                    ₹
                    {Number(
                      item.refund_amount || 0
                    ).toFixed(2)}
                  </p>

                  {item.created_at && (
                    <p>
                      <strong>
                        Requested:
                      </strong>{" "}
                      {new Date(
                        item.created_at
                      ).toLocaleString()}
                    </p>
                  )}

                  {item.rejection_reason && (
                    <p
                      style={{
                        color: "#842029",
                      }}
                    >
                      <strong>
                        Rejection Reason:
                      </strong>{" "}
                      {item.rejection_reason}
                    </p>
                  )}

                  {item.stripe_refund_id && (
                    <p>
                      <strong>
                        Stripe Refund:
                      </strong>{" "}
                      {item.stripe_refund_id}
                    </p>
                  )}
                </div>

                {/* ACTIONS */}

                <div
                  style={{
                    display: "flex",
                    gap: "10px",
                    marginTop: "20px",
                    flexWrap: "wrap",
                  }}
                >
                  {/* APPROVE */}

                  {isRequested && (
                    <button
                      onClick={() =>
                        approveReturn(item.id)
                      }
                      disabled={busy}
                      style={{
                        padding: "11px 20px",
                        background: "#198754",
                        color: "#fff",
                        border: "none",
                        borderRadius: "6px",
                        cursor: busy
                          ? "not-allowed"
                          : "pointer",
                        fontWeight: "bold",
                      }}
                    >
                      {busy
                        ? "Processing..."
                        : "Approve Return"}
                    </button>
                  )}

                  {/* REJECT */}

                  {isRequested && (
                    <button
                      onClick={() =>
                        openRejectForm(item)
                      }
                      disabled={busy}
                      style={{
                        padding: "11px 20px",
                        background: "#dc3545",
                        color: "#fff",
                        border: "none",
                        borderRadius: "6px",
                        cursor: busy
                          ? "not-allowed"
                          : "pointer",
                        fontWeight: "bold",
                      }}
                    >
                      Reject Return
                    </button>
                  )}

                  {/* REFUND */}

                  {isApproved && (
                    <button
                      onClick={() =>
                        processRefund(item.id)
                      }
                      disabled={busy}
                      style={{
                        padding: "11px 20px",
                        background: "#0d6efd",
                        color: "#fff",
                        border: "none",
                        borderRadius: "6px",
                        cursor: busy
                          ? "not-allowed"
                          : "pointer",
                        fontWeight: "bold",
                      }}
                    >
                      {busy
                        ? "Processing..."
                        : "Process Refund"}
                    </button>
                  )}

                  {/* APPROVED STATUS */}

                  {isApproved && (
                    <span
                      style={{
                        padding: "11px 15px",
                        background: "#d1e7dd",
                        color: "#0f5132",
                        borderRadius: "6px",
                      }}
                    >
                      Return Approved
                    </span>
                  )}

                  {/* RETURNED */}

                  {isReturned && (
                    <span
                      style={{
                        padding: "11px 15px",
                        background: "#cfe2ff",
                        color: "#084298",
                        borderRadius: "6px",
                      }}
                    >
                      Returned
                    </span>
                  )}

                  {/* REJECTED */}

                  {isRejected && (
                    <span
                      style={{
                        padding: "11px 15px",
                        background: "#f8d7da",
                        color: "#842029",
                        borderRadius: "6px",
                      }}
                    >
                      Rejected
                    </span>
                  )}

                  {/* REFUNDED */}

                  {isRefunded && (
                    <span
                      style={{
                        padding: "11px 15px",
                        background: "#d1e7dd",
                        color: "#0f5132",
                        borderRadius: "6px",
                      }}
                    >
                      Refund Completed
                    </span>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* ========================================================
          REJECT FORM
      ======================================================== */}

      {selectedReturn && (
        <div
          style={{
            position: "fixed",
            inset: 0,
            background: "rgba(0,0,0,0.5)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            padding: "20px",
            zIndex: 1000,
          }}
        >
          <div
            style={{
              width: "100%",
              maxWidth: "500px",
              background: "#fff",
              borderRadius: "10px",
              padding: "25px",
              boxShadow:
                "0 5px 20px rgba(0,0,0,0.2)",
            }}
          >
            <h2>
              Reject Return #{selectedReturn.id}
            </h2>

            <p>
              Order #{selectedReturn.order_id}
            </p>

            <label>
              <strong>
                Rejection Reason
              </strong>
            </label>

            <textarea
              value={rejectionReason}
              onChange={(e) =>
                setRejectionReason(
                  e.target.value
                )
              }
              placeholder="Enter reason for rejecting this return..."
              rows="5"
              disabled={actionLoading !== null}
              style={{
                display: "block",
                width: "100%",
                marginTop: "8px",
                marginBottom: "20px",
                padding: "10px",
                border: "1px solid #ccc",
                borderRadius: "6px",
                resize: "vertical",
              }}
            />

            <div
              style={{
                display: "flex",
                gap: "10px",
              }}
            >
              <button
                onClick={rejectReturn}
                disabled={
                  actionLoading !== null ||
                  !rejectionReason.trim()
                }
                style={{
                  padding: "11px 20px",
                  background:
                    actionLoading !== null ||
                    !rejectionReason.trim()
                      ? "#999"
                      : "#dc3545",
                  color: "#fff",
                  border: "none",
                  borderRadius: "6px",
                  cursor:
                    actionLoading !== null ||
                    !rejectionReason.trim()
                      ? "not-allowed"
                      : "pointer",
                  fontWeight: "bold",
                }}
              >
                Reject Return
              </button>

              <button
                onClick={closeRejectForm}
                disabled={
                  actionLoading !== null
                }
                style={{
                  padding: "11px 20px",
                  background: "#fff",
                  border: "1px solid #ccc",
                  borderRadius: "6px",
                  cursor: "pointer",
                }}
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AdminReturns;
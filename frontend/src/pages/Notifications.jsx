import { useEffect, useState } from "react";
import { useAuth0 } from "@auth0/auth0-react";

function Notifications() {
  const { isAuthenticated, user } = useAuth0();

  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const API_URL =
    import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

  // ------------------------------------------------
  // Get backend user ID
  // ------------------------------------------------

  const getBackendUser = async () => {
    const response = await fetch(
      `${API_URL}/users/by-email?email=${encodeURIComponent(
        user.email
      )}`
    );

    if (!response.ok) {
      throw new Error("Unable to find backend user");
    }

    return await response.json();
  };

  // ------------------------------------------------
  // Get notifications
  // ------------------------------------------------

  const fetchNotifications = async () => {
    try {
      setLoading(true);
      setError("");

      if (!isAuthenticated || !user?.email) {
        setNotifications([]);
        return;
      }

      const backendUser = await getBackendUser();

      const response = await fetch(
        `${API_URL}/notifications?user_id=${backendUser.id}`
      );

      if (!response.ok) {
        throw new Error("Unable to load notifications");
      }

      const data = await response.json();

      setNotifications(data);
    } catch (err) {
      console.error(err);
      setError("Unable to connect to backend");
    } finally {
      setLoading(false);
    }
  };

  // ------------------------------------------------
  // Mark notification as read
  // ------------------------------------------------

  const markAsRead = async (notificationId) => {
    try {
      const response = await fetch(
        `${API_URL}/notifications/read`,
        {
          method: "POST",

          headers: {
            "Content-Type": "application/json",
          },

          body: JSON.stringify({
            notification_id: notificationId,
          }),
        }
      );

      if (!response.ok) {
        throw new Error(
          "Failed to mark notification as read"
        );
      }

      setNotifications((previous) =>
        previous.map((notification) =>
          notification.id === notificationId
            ? {
                ...notification,
                read_status: true,
              }
            : notification
        )
      );
    } catch (err) {
      console.error(err);
    }
  };

  // ------------------------------------------------
  // Load notifications
  // ------------------------------------------------

  useEffect(() => {
    fetchNotifications();
  }, [isAuthenticated, user]);

  // ------------------------------------------------
  // Not logged in
  // ------------------------------------------------

  if (!isAuthenticated) {
    return (
      <div
        style={{
          maxWidth: "800px",
          margin: "40px auto",
          padding: "20px",
        }}
      >
        <h2>🔔 Notifications</h2>

        <p>
          Please login to view your notifications.
        </p>
      </div>
    );
  }

  // ------------------------------------------------
  // Loading
  // ------------------------------------------------

  if (loading) {
    return (
      <div
        style={{
          maxWidth: "800px",
          margin: "40px auto",
          padding: "20px",
        }}
      >
        <h2>🔔 Notifications</h2>

        <p>Loading notifications...</p>
      </div>
    );
  }

  // ------------------------------------------------
  // Error
  // ------------------------------------------------

  if (error) {
    return (
      <div
        style={{
          maxWidth: "800px",
          margin: "40px auto",
          padding: "20px",
        }}
      >
        <h2>🔔 Notifications</h2>

        <p>{error}</p>

        <button onClick={fetchNotifications}>
          Try Again
        </button>
      </div>
    );
  }

  // ------------------------------------------------
  // Notifications UI
  // ------------------------------------------------

  return (
    <div
      style={{
        maxWidth: "800px",
        margin: "40px auto",
        padding: "20px",
      }}
    >
      <h2>🔔 Notifications</h2>

      {notifications.length === 0 ? (
        <p>No notifications yet.</p>
      ) : (
        notifications.map((notification) => (
          <div
            key={notification.id}
            style={{
              border: "1px solid #ddd",
              borderRadius: "8px",
              padding: "15px",
              marginBottom: "10px",
              backgroundColor:
                notification.read_status
                  ? "#ffffff"
                  : "#f0f8ff",
            }}
          >
            <h3>
              {notification.type ===
                "order_confirmed" &&
                "✅ Order Confirmed"}

              {notification.type ===
                "payment_success" &&
                "💳 Payment Successful"}

              {notification.type ===
                "payment_failed" &&
                "❌ Payment Failed"}

              {notification.type ===
                "order_shipped" &&
                "🚚 Order Shipped"}

              {notification.type ===
                "order_delivered" &&
                "📦 Order Delivered"}
            </h3>

            <p>{notification.message}</p>

            {notification.order_id && (
              <p>
                <strong>Order ID:</strong>{" "}
                {notification.order_id}
              </p>
            )}

            <small>
              {notification.timestamp}
            </small>

            {!notification.read_status && (
              <div>
                <button
                  onClick={() =>
                    markAsRead(notification.id)
                  }
                  style={{
                    marginTop: "10px",
                    padding: "8px 12px",
                    cursor: "pointer",
                  }}
                >
                  Mark as read
                </button>
              </div>
            )}
          </div>
        ))
      )}
    </div>
  );
}

export default Notifications;

import React, { useEffect, useState } from "react";
import { useAuth0 } from "@auth0/auth0-react";

const API_URL = "http://127.0.0.1:8000";

export default function Notifications() {
  const { getAccessTokenSilently, isAuthenticated } = useAuth0();

  const [userId, setUserId] = useState(null);
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  // ============================================================
  // GET DATABASE USER
  // ============================================================

  const loadCurrentUser = async () => {
    try {
      const token = await getAccessTokenSilently();

      const response = await fetch(`${API_URL}/users/me`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error("Failed to get current user");
      }

      const user = await response.json();

      console.log("DATABASE USER:", user);

      setUserId(user.id);

      return user.id;
    } catch (err) {
      console.error("User loading error:", err);
      setError("Unable to load user");
      return null;
    }
  };

  // ============================================================
  // LOAD NOTIFICATIONS
  // ============================================================

  const loadNotifications = async (dbUserId) => {
    try {
      const token = await getAccessTokenSilently();

      const response = await fetch(
        `${API_URL}/notifications/?user_id=${dbUserId}`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      if (!response.ok) {
        throw new Error("Failed to load notifications");
      }

      const data = await response.json();

      console.log("NOTIFICATIONS:", data);

      setNotifications(data);
    } catch (err) {
      console.error("Notification loading error:", err);
      setError("Unable to load notifications");
    } finally {
      setLoading(false);
    }
  };

  // ============================================================
  // INITIAL LOAD
  // ============================================================

  useEffect(() => {
    if (!isAuthenticated) {
      setLoading(false);
      return;
    }

    const initialize = async () => {
      const dbUserId = await loadCurrentUser();

      if (dbUserId) {
        await loadNotifications(dbUserId);
      }
    };

    initialize();
  }, [isAuthenticated]);

  // ============================================================
  // REAL-TIME NOTIFICATION
  // App.jsx WebSocket dispatches this event
  // ============================================================

  useEffect(() => {
    const handleNotification = (event) => {
      console.log("REAL-TIME NOTIFICATION:", event.detail);

      setNotifications((previous) => [
        event.detail,
        ...previous,
      ]);
    };

    window.addEventListener(
      "notification-received",
      handleNotification
    );

    return () => {
      window.removeEventListener(
        "notification-received",
        handleNotification
      );
    };
  }, []);

  // ============================================================
  // MARK ONE AS READ
  // ============================================================

  const markAsRead = async (notificationId) => {
    if (!userId) return;

    try {
      const token = await getAccessTokenSilently();

      const response = await fetch(
        `${API_URL}/notifications/read?user_id=${userId}`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({
            notification_id: notificationId,
          }),
        }
      );

      if (!response.ok) {
        throw new Error("Failed to mark notification as read");
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
      console.error("Mark read error:", err);
    }
  };

  // ============================================================
  // MARK ALL AS READ
  // ============================================================

  const markAllAsRead = async () => {
    if (!userId) return;

    try {
      const token = await getAccessTokenSilently();

      const response = await fetch(
        `${API_URL}/notifications/read-all?user_id=${userId}`,
        {
          method: "POST",
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      if (!response.ok) {
        throw new Error("Failed to mark all as read");
      }

      setNotifications((previous) =>
        previous.map((notification) => ({
          ...notification,
          read_status: true,
        }))
      );
    } catch (err) {
      console.error("Mark all read error:", err);
    }
  };

  // ============================================================
  // LOADING
  // ============================================================

  if (loading) {
    return (
      <div style={{ padding: "30px" }}>
        <h2>Notifications</h2>
        <p>Loading notifications...</p>
      </div>
    );
  }

  // ============================================================
  // NOT AUTHENTICATED
  // ============================================================

  if (!isAuthenticated) {
    return (
      <div style={{ padding: "30px" }}>
        <h2>Notifications</h2>
        <p>Please login to view notifications.</p>
      </div>
    );
  }

  // ============================================================
  // UI
  // ============================================================

  return (
    <div
      style={{
        maxWidth: "800px",
        margin: "30px auto",
        padding: "20px",
      }}
    >
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          marginBottom: "20px",
        }}
      >
        <h2>Notifications</h2>

        {notifications.some(
          (notification) => !notification.read_status
        ) && (
          <button onClick={markAllAsRead}>
            Mark all as read
          </button>
        )}
      </div>

      {error && (
        <p style={{ color: "red" }}>
          {error}
        </p>
      )}

      {notifications.length === 0 ? (
        <div
          style={{
            padding: "30px",
            textAlign: "center",
            border: "1px solid #ddd",
            borderRadius: "8px",
          }}
        >
          <p>No notifications yet.</p>
        </div>
      ) : (
        notifications.map((notification) => (
          <div
            key={notification.id}
            onClick={() => {
              if (!notification.read_status) {
                markAsRead(notification.id);
              }
            }}
            style={{
              padding: "16px",
              marginBottom: "10px",
              border: "1px solid #ddd",
              borderRadius: "8px",
              cursor: notification.read_status
                ? "default"
                : "pointer",
              backgroundColor: notification.read_status
                ? "#ffffff"
                : "#f0f7ff",
            }}
          >
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
              }}
            >
              <strong>
                {notification.type}
              </strong>

              {!notification.read_status && (
                <span
                  style={{
                    fontSize: "12px",
                    fontWeight: "bold",
                  }}
                >
                  NEW
                </span>
              )}
            </div>

            <p>{notification.message}</p>

            {notification.order_id && (
              <small>
                Order ID: {notification.order_id}
              </small>
            )}

            <br />

            <small>
              {notification.timestamp
                ? new Date(
                    notification.timestamp
                  ).toLocaleString()
                : ""}
            </small>
          </div>
        ))
      )}
    </div>
  );
}

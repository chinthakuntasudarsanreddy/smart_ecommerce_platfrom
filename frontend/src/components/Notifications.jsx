
import React, { useEffect, useState } from "react";

const API_URL = "http://127.0.0.1:8000";

const Notifications = ({ userId }) => {
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(true);

  // Load notifications from API
  useEffect(() => {
    if (!userId) return;

    const fetchNotifications = async () => {
      try {
        setLoading(true);

        const response = await fetch(
          `${API_URL}/notifications/?user_id=${userId}`
        );

        if (!response.ok) {
          throw new Error("Failed to fetch notifications");
        }

        const data = await response.json();
        setNotifications(data);
      } catch (error) {
        console.error("Failed to load notifications:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchNotifications();
  }, [userId]);

  // Receive real-time notifications from App.jsx
  useEffect(() => {
    const handleNotification = (event) => {
      const notification = event.detail;

      if (!notification) return;

      setNotifications((previous) => {
        // Prevent duplicate notification
        if (
          notification.id &&
          previous.some(
            (item) => item.id === notification.id
          )
        ) {
          return previous;
        }

        return [notification, ...previous];
      });
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

  // Mark one notification as read
  const markAsRead = async (notificationId) => {
    try {
      const response = await fetch(
        `${API_URL}/notifications/read?user_id=${userId}`,
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
    } catch (error) {
      console.error(
        "Failed to mark notification as read:",
        error
      );
    }
  };

  // Mark all notifications as read
  const markAllAsRead = async () => {
    try {
      const response = await fetch(
        `${API_URL}/notifications/read-all?user_id=${userId}`,
        {
          method: "POST",
        }
      );

      if (!response.ok) {
        throw new Error(
          "Failed to mark all notifications as read"
        );
      }

      setNotifications((previous) =>
        previous.map((notification) => ({
          ...notification,
          read_status: true,
        }))
      );
    } catch (error) {
      console.error(
        "Failed to mark all notifications as read:",
        error
      );
    }
  };

  if (loading) {
    return (
      <div style={styles.container}>
        <h2>Notifications</h2>
        <p>Loading notifications...</p>
      </div>
    );
  }

  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <h2>Notifications</h2>

        {notifications.length > 0 && (
          <button
            onClick={markAllAsRead}
            style={styles.markAllButton}
          >
            Mark All as Read
          </button>
        )}
      </div>

      {notifications.length === 0 ? (
        <div style={styles.empty}>
          <div style={styles.emptyIcon}>🔔</div>
          <h3>No notifications</h3>
          <p>You don't have any notifications yet.</p>
        </div>
      ) : (
        <div style={styles.list}>
          {notifications.map((notification) => (
            <div
              key={notification.id}
              style={{
                ...styles.notification,
                ...(notification.read_status
                  ? styles.read
                  : styles.unread),
              }}
              onClick={() =>
                !notification.read_status &&
                markAsRead(notification.id)
              }
            >
              <div style={styles.icon}>
                🔔
              </div>

              <div style={styles.content}>
                <div style={styles.topRow}>
                  <strong>
                    {notification.type || "Notification"}
                  </strong>

                  {!notification.read_status && (
                    <span style={styles.newBadge}>
                      NEW
                    </span>
                  )}
                </div>

                <p style={styles.message}>
                  {notification.message}
                </p>

                <small style={styles.time}>
                  {notification.timestamp
                    ? new Date(
                        notification.timestamp
                      ).toLocaleString()
                    : ""}
                </small>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

const styles = {
  container: {
    maxWidth: "900px",
    margin: "40px auto",
    padding: "20px",
  },

  header: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: "25px",
  },

  markAllButton: {
    padding: "10px 16px",
    border: "none",
    borderRadius: "6px",
    cursor: "pointer",
    background: "#333",
    color: "#fff",
  },

  list: {
    display: "flex",
    flexDirection: "column",
    gap: "12px",
  },

  notification: {
    display: "flex",
    gap: "15px",
    padding: "18px",
    borderRadius: "10px",
    cursor: "pointer",
    border: "1px solid #ddd",
  },

  unread: {
    background: "#f5f9ff",
  },

  read: {
    background: "#fff",
  },

  icon: {
    fontSize: "25px",
  },

  content: {
    flex: 1,
  },

  topRow: {
    display: "flex",
    alignItems: "center",
    gap: "10px",
  },

  newBadge: {
    fontSize: "10px",
    padding: "3px 7px",
    borderRadius: "10px",
    background: "#007bff",
    color: "#fff",
  },

  message: {
    margin: "8px 0",
  },

  time: {
    color: "#777",
  },

  empty: {
    textAlign: "center",
    padding: "60px 20px",
  },

  emptyIcon: {
    fontSize: "50px",
    marginBottom: "10px",
  },
};

export default Notifications;

import { useEffect, useState } from "react";

function Notifications({ userId }) {
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const API_URL = "http://127.0.0.1:8000";

  // ---------------------------------------------
  // Get notifications from backend
  // ---------------------------------------------

  const fetchNotifications = async () => {
    try {
      setLoading(true);
      setError("");

      const response = await fetch(
        `${API_URL}/notifications/?user_id=${userId}`
      );

      if (!response.ok) {
        throw new Error("Failed to fetch notifications");
      }

      const data = await response.json();

      setNotifications(data);

    } catch (err) {
      console.error(err);
      setError("Unable to load notifications");
    } finally {
      setLoading(false);
    }
  };


  // ---------------------------------------------
  // Initial notifications
  // ---------------------------------------------

  useEffect(() => {
    if (userId) {
      fetchNotifications();
    }
  }, [userId]);


  // ---------------------------------------------
  // WebSocket real-time notification
  // ---------------------------------------------

  useEffect(() => {
    if (!userId) {
      return;
    }

    const socket = new WebSocket(
      `ws://127.0.0.1:8000/ws/notifications/${userId}`
    );

    socket.onopen = () => {
      console.log("Notification WebSocket connected");
    };

    socket.onmessage = (event) => {
      try {
        const notification = JSON.parse(event.data);

        console.log(
          "New notification:",
          notification
        );

        setNotifications((previous) => [
          notification,
          ...previous
        ]);

      } catch (error) {
        console.error(
          "Invalid notification:",
          error
        );
      }
    };

    socket.onerror = (error) => {
      console.error(
        "Notification WebSocket error:",
        error
      );
    };

    socket.onclose = () => {
      console.log(
        "Notification WebSocket disconnected"
      );
    };

    return () => {
      socket.close();
    };

  }, [userId]);


  // ---------------------------------------------
  // Mark notification as read
  // ---------------------------------------------

  const markAsRead = async (notificationId) => {
    try {
      const response = await fetch(
        `${API_URL}/notifications/read?user_id=${userId}`,
        {
          method: "POST",

          headers: {
            "Content-Type": "application/json"
          },

          body: JSON.stringify({
            notification_id: notificationId
          })
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
                read_status: true
              }
            : notification
        )
      );

    } catch (error) {
      console.error(error);
    }
  };


  // ---------------------------------------------
  // Mark all as read
  // ---------------------------------------------

  const markAllAsRead = async () => {
    try {
      const response = await fetch(
        `${API_URL}/notifications/read-all?user_id=${userId}`,
        {
          method: "POST"
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
          read_status: true
        }))
      );

    } catch (error) {
      console.error(error);
    }
  };


  // ---------------------------------------------
  // Loading
  // ---------------------------------------------

  if (loading) {
    return (
      <div style={styles.container}>
        <h2>Notifications</h2>

        <p>Loading notifications...</p>
      </div>
    );
  }


  // ---------------------------------------------
  // Page
  // ---------------------------------------------

  return (
    <div style={styles.container}>

      <div style={styles.header}>

        <h2>
          Notifications
        </h2>

        {notifications.length > 0 && (
          <button
            onClick={markAllAsRead}
            style={styles.markAllButton}
          >
            Mark All as Read
          </button>
        )}

      </div>


      {error && (
        <div style={styles.error}>
          {error}
        </div>
      )}


      {notifications.length === 0 ? (

        <div style={styles.empty}>
          <h3>
            No notifications
          </h3>

          <p>
            You're all caught up.
          </p>
        </div>

      ) : (

        <div>

          {notifications.map(
            (notification) => (

              <div
                key={notification.id}
                style={{
                  ...styles.notification,

                  backgroundColor:
                    notification.read_status
                      ? "#ffffff"
                      : "#eef6ff"
                }}
              >

                <div style={styles.notificationContent}>

                  <div style={styles.titleRow}>

                    <strong>
                      {formatNotificationType(
                        notification.type
                      )}
                    </strong>

                    {!notification.read_status && (
                      <span style={styles.unread}>
                        NEW
                      </span>
                    )}

                  </div>


                  <p style={styles.message}>
                    {notification.message}
                  </p>


                  {notification.order_id && (
                    <p style={styles.order}>
                      Order #{notification.order_id}
                    </p>
                  )}


                  <small style={styles.time}>
                    {formatDate(
                      notification.timestamp
                    )}
                  </small>

                </div>


                {!notification.read_status && (

                  <button
                    onClick={() =>
                      markAsRead(
                        notification.id
                      )
                    }
                    style={styles.readButton}
                  >
                    Mark as Read
                  </button>

                )}

              </div>

            )
          )}

        </div>

      )}

    </div>
  );
}


// ---------------------------------------------
// Notification type formatter
// ---------------------------------------------

function formatNotificationType(type) {

  if (!type) {
    return "Notification";
  }

  return type
    .replaceAll("_", " ")
    .replace(
      /\b\w/g,
      (character) =>
        character.toUpperCase()
    );
}


// ---------------------------------------------
// Date formatter
// ---------------------------------------------

function formatDate(timestamp) {

  if (!timestamp) {
    return "";
  }

  try {

    return new Date(
      timestamp
    ).toLocaleString();

  } catch {
    return timestamp;
  }
}


// ---------------------------------------------
// Styles
// ---------------------------------------------

const styles = {

  container: {
    maxWidth: "900px",
    margin: "40px auto",
    padding: "20px"
  },

  header: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: "20px"
  },

  markAllButton: {
    padding: "10px 16px",
    border: "none",
    borderRadius: "6px",
    cursor: "pointer"
  },

  notification: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    gap: "20px",
    padding: "18px",
    marginBottom: "12px",
    border: "1px solid #ddd",
    borderRadius: "8px"
  },

  notificationContent: {
    flex: 1
  },

  titleRow: {
    display: "flex",
    alignItems: "center",
    gap: "10px"
  },

  unread: {
    fontSize: "11px",
    fontWeight: "bold",
    padding: "3px 7px",
    borderRadius: "10px",
    backgroundColor: "#ff4d4f",
    color: "#ffffff"
  },

  message: {
    margin: "8px 0"
  },

  order: {
    margin: "5px 0",
    fontWeight: "500"
  },

  time: {
    color: "#777"
  },

  readButton: {
    padding: "8px 12px",
    border: "1px solid #ccc",
    backgroundColor: "#ffffff",
    borderRadius: "5px",
    cursor: "pointer"
  },

  empty: {
    textAlign: "center",
    padding: "60px 20px",
    border: "1px solid #ddd",
    borderRadius: "8px"
  },

  error: {
    padding: "12px",
    marginBottom: "15px",
    borderRadius: "5px"
  }
};


export default Notifications;
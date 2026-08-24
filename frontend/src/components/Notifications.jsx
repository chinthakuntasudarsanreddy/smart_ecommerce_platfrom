import { useEffect, useState } from "react";

function Notifications({ userId }) {
  const [notifications, setNotifications] = useState([]);

  useEffect(() => {
    if (!userId) return;

    // Load existing notifications
    fetch(
      `http://127.0.0.1:8000/notifications?user_id=${userId}`
    )
      .then((response) => response.json())
      .then((data) => {
        setNotifications(data);
      });

    // WebSocket
    const socket = new WebSocket(
      `ws://127.0.0.1:8000/ws/notifications/${userId}`
    );

    socket.onmessage = (event) => {
      const data = JSON.parse(event.data);

      if (data.notification) {
        setNotifications((previous) => [
          data.notification,
          ...previous,
        ]);
      }
    };

    socket.onerror = (error) => {
      console.error("WebSocket error:", error);
    };

    return () => {
      socket.close();
    };
  }, [userId]);

  const markAsRead = async (notificationId) => {
    await fetch(
      "http://127.0.0.1:8000/notifications/read",
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
  };

  return (
    <div>
      <h2>Notifications</h2>

      {notifications.length === 0 ? (
        <p>No notifications</p>
      ) : (
        notifications.map((notification) => (
          <div
            key={notification.id}
            onClick={() =>
              markAsRead(notification.id)
            }
            style={{
              padding: "10px",
              marginBottom: "10px",
              border: "1px solid #ddd",
              backgroundColor: notification.read_status
                ? "#ffffff"
                : "#eef6ff",
              cursor: "pointer",
            }}
          >
            <strong>{notification.type}</strong>

            <p>{notification.message}</p>

            <small>
              {notification.timestamp}
            </small>
          </div>
        ))
      )}
    </div>
  );
}

export default Notifications;
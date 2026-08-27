import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

function Navbar() {
  const [unreadCount, setUnreadCount] = useState(0);

  const userId = 1;
  const API_URL = "http://127.0.0.1:8000";

  // ---------------------------------------------
  // Get unread notifications
  // ---------------------------------------------

  const fetchUnreadNotifications = async () => {
    try {
      const response = await fetch(
        `${API_URL}/notifications/unread?user_id=${userId}`
      );

      if (!response.ok) {
        throw new Error(
          "Failed to fetch notifications"
        );
      }

      const data = await response.json();

      setUnreadCount(data.length);

    } catch (error) {
      console.error(
        "Notification error:",
        error
      );
    }
  };


  // ---------------------------------------------
  // WebSocket
  // ---------------------------------------------

  useEffect(() => {

    fetchUnreadNotifications();

    const socket = new WebSocket(
      `ws://127.0.0.1:8000/ws/notifications/${userId}`
    );

    socket.onopen = () => {
      console.log(
        "Navbar notification WebSocket connected"
      );
    };

    socket.onmessage = (event) => {

      try {

        const notification =
          JSON.parse(event.data);

        console.log(
          "New notification:",
          notification
        );

        if (!notification.read_status) {
          setUnreadCount(
            (previous) => previous + 1
          );
        }

      } catch (error) {

        console.error(
          "Invalid WebSocket notification:",
          error
        );

      }

    };

    socket.onerror = (error) => {
      console.error(
        "Navbar WebSocket error:",
        error
      );
    };

    socket.onclose = () => {
      console.log(
        "Navbar WebSocket disconnected"
      );
    };


    return () => {
      socket.close();
    };

  }, []);


  return (
    <nav style={styles.navbar}>

      <div style={styles.logo}>
        <Link
          to="/"
          style={styles.logoLink}
        >
          Smart Ecommerce
        </Link>
      </div>


      <div style={styles.links}>

        <Link
          to="/"
          style={styles.link}
        >
          Home
        </Link>

        <Link
          to="/products"
          style={styles.link}
        >
          Products
        </Link>

        <Link
          to="/cart"
          style={styles.link}
        >
          Cart
        </Link>

        <Link
          to="/profile"
          style={styles.link}
        >
          Profile
        </Link>


        {/* Notification Bell */}

        <Link
          to="/notifications"
          style={styles.notificationLink}
          title="Notifications"
        >

          <span style={styles.bell}>
            🔔
          </span>


          {unreadCount > 0 && (

            <span style={styles.badge}>

              {unreadCount > 99
                ? "99+"
                : unreadCount}

            </span>

          )}

        </Link>

      </div>

    </nav>
  );
}


// ---------------------------------------------
// Styles
// ---------------------------------------------

const styles = {

  navbar: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    padding: "15px 30px",
    borderBottom: "1px solid #ddd",
    backgroundColor: "#ffffff"
  },

  logo: {
    fontSize: "20px",
    fontWeight: "bold"
  },

  logoLink: {
    textDecoration: "none",
    color: "#222"
  },

  links: {
    display: "flex",
    alignItems: "center",
    gap: "20px"
  },

  link: {
    textDecoration: "none",
    color: "#333"
  },

  notificationLink: {
    position: "relative",
    display: "flex",
    alignItems: "center",
    textDecoration: "none",
    cursor: "pointer"
  },

  bell: {
    fontSize: "24px"
  },

  badge: {
    position: "absolute",
    top: "-8px",
    right: "-10px",
    minWidth: "18px",
    height: "18px",
    padding: "0 4px",
    borderRadius: "10px",
    backgroundColor: "red",
    color: "white",
    fontSize: "11px",
    fontWeight: "bold",
    display: "flex",
    justifyContent: "center",
    alignItems: "center"
  }
};


export default Navbar;
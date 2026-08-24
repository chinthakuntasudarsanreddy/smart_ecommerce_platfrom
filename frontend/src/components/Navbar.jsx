import { Link } from "react-router-dom";
import { useAuth0 } from "@auth0/auth0-react";

function Navbar() {
  const {
    isAuthenticated,
    logout,
  } = useAuth0();

  return (
    <nav className="navbar">

      <Link to="/" className="logo">
        Smart E-Commerce
      </Link>

      <div className="nav-links">

        <Link to="/">
          Home
        </Link>

        <Link to="/products">
          Products
        </Link>
        <Link to="/notifications">
            🔔 Notifications
          </Link>

        {/* Notifications */}
        {isAuthenticated && (
          <Link to="/notifications">
            🔔 Notifications
          </Link>
        )}

        {/* Cart always visible */}
        <Link to="/cart">
          Cart
        </Link>

        {/* Profile only after login */}
        {isAuthenticated && (
          <Link to="/profile">
            Profile
          </Link>
        )}

        {!isAuthenticated ? (
          <>
            <Link to="/login">
              Login
            </Link>

            <Link to="/register">
              Register
            </Link>
          </>
        ) : (
          <button
            onClick={() =>
              logout({
                logoutParams: {
                  returnTo: window.location.origin,
                },
              })
            }
          >
            Logout
          </button>
        )}

      </div>
    </nav>
  );
}

export default Navbar;
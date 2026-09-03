
import React from "react";
import { useAuth0 } from "@auth0/auth0-react";
import { Navigate } from "react-router-dom";

function Login() {
  const {
    isAuthenticated,
    isLoading,
    loginWithRedirect,
  } = useAuth0();

  // Auth0 is still checking the session
  if (isLoading) {
    return (
      <div className="auth-container">
        <div className="auth-card">
          <h2>Loading...</h2>
        </div>
      </div>
    );
  }

  // Already logged in
  if (isAuthenticated) {
    return <Navigate to="/profile" replace />;
  }

  const handleLogin = async (event) => {
    // VERY IMPORTANT:
    // Prevent browser/page refresh
    event.preventDefault();

    console.log("LOGIN BUTTON CLICKED");

    try {
      console.log(
        "Starting Auth0 login..."
      );

      await loginWithRedirect({
        authorizationParams: {
          redirect_uri: window.location.origin,
          audience:
            import.meta.env.VITE_AUTH0_AUDIENCE,
        },
      });
    } catch (error) {
      console.error(
        "Auth0 login failed:",
        error
      );
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-card">
        <h1>Login</h1>

        <p>
          Login to your Smart E-Commerce account
        </p>

        <form onSubmit={handleLogin}>
          <button
            type="submit"
            className="login-btn"
          >
            Continue with Google / Facebook
          </button>
        </form>
      </div>
    </div>
  );
}

export default Login;

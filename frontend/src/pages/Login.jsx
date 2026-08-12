import { useAuth0 } from "@auth0/auth0-react";
import { Navigate } from "react-router-dom";

function Login() {

  const {
    isAuthenticated,
    loginWithRedirect,
    isLoading,
  } = useAuth0();

  if (isLoading) {
    return <h2>Loading...</h2>;
  }

  if (isAuthenticated) {
    return <Navigate to="/profile" />;
  }

  return (
    <div className="auth-container">

      <div className="auth-card">

        <h1>Login</h1>

        <p>
          Login to your account
        </p>

        <button
          className="login-btn"
          onClick={() => loginWithRedirect()}
        >
          Continue with Google / Facebook
        </button>

      </div>

    </div>
  );
}

export default Login;
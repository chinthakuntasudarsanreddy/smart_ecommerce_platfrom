import { useAuth0 } from "@auth0/auth0-react";

function Register() {

  const {
    loginWithRedirect,
  } = useAuth0();

  return (
    <div className="auth-container">

      <div className="auth-card">

        <h1>Create Account</h1>

        <p>
          Create your Smart E-Commerce account.
        </p>

        <button
          className="login-btn"
          onClick={() =>
            loginWithRedirect({
              authorizationParams: {
                screen_hint: "signup",
              },
            })
          }
        >
          Create Account
        </button>

      </div>

    </div>
  );
}

export default Register;
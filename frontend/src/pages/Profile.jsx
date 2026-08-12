import { useAuth0 } from "@auth0/auth0-react";
import { Navigate } from "react-router-dom";

function Profile() {

  const {
    user,
    isAuthenticated,
    isLoading,
  } = useAuth0();

  if (isLoading) {
    return <h2>Loading...</h2>;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" />;
  }

  return (
    <div className="profile">

      <h1>
        My Profile
      </h1>

      {user?.picture && (
        <img
          src={user.picture}
          alt="Profile"
          className="profile-image"
        />
      )}

      <h2>
        {user?.name}
      </h2>

      <p>
        Email: {user?.email}
      </p>

    </div>
  );
}

export default Profile;
import { Link } from "react-router-dom";

function Home() {
  return (
    <div className="home">

      <h1>
        Welcome to Smart E-Commerce
      </h1>

      <p>
        Shop your favorite products
        at the best prices.
      </p>

      <Link to="/products">
        <button className="primary-btn">
          Shop Now
        </button>
      </Link>

    </div>
  );
}

export default Home;
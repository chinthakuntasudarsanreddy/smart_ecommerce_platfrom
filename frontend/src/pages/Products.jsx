
import { useEffect, useState } from "react";

function Products({ addToCart }) {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    fetch("http://127.0.0.1:8000/products/")
      .then((response) => {
        if (!response.ok) {
          throw new Error("Failed to fetch products");
        }

        return response.json();
      })
      .then((data) => {
        setProducts(data);
        setLoading(false);
      })
      .catch((error) => {
        console.error(error);
        setError("Unable to connect to backend");
        setLoading(false);
      });
  }, []);

  const handleAddToCart = (product) => {

    if (!addToCart) {
      console.error("addToCart function was not provided");
      alert("Cart system is not configured");
      return;
    }

    addToCart(product);
  };


  if (loading) {
    return <h2>Loading products...</h2>;
  }

  if (error) {
    return <h2>{error}</h2>;
  }


  return (
    <div className="page">

      <h1>Products</h1>

      <div className="product-grid">

        {products.map((product) => (

          <div
            className="product-card"
            key={product.id}
          >

            {product.image_url && (
              <img
                src={product.image_url}
                alt={product.name}
              />
            )}

            <h2>
              {product.name}
            </h2>

            <p>
              {product.description}
            </p>

            <h3>
              ₹{product.price}
            </h3>

            <p>
              Category: {product.category}
            </p>

            <p>
              Stock: {product.stock}
            </p>

            <button
              onClick={() =>
                handleAddToCart(product)
              }
              disabled={product.stock <= 0}
            >
              {product.stock <= 0
                ? "Out of Stock"
                : "Add to Cart"}
            </button>

          </div>

        ))}

      </div>

    </div>
  );
}

export default Products;
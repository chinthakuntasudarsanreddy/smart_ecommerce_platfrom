import { useState } from "react";

function Products() {

  const [cart, setCart] = useState([]);

  const products = [
    {
      id: 1,
      name: "Smart Phone",
      price: 25000,
      image: "https://via.placeholder.com/250",
    },
    {
      id: 2,
      name: "Laptop",
      price: 60000,
      image: "https://via.placeholder.com/250",
    },
    {
      id: 3,
      name: "Smart Watch",
      price: 5000,
      image: "https://via.placeholder.com/250",
    },
  ];

  const addToCart = (product) => {

    setCart([
      ...cart,
      product,
    ]);

    alert(`${product.name} added to cart`);
  };

  return (
    <div className="page">

      <h1>Products</h1>

      <div className="product-grid">

        {products.map((product) => (

          <div
            className="product-card"
            key={product.id}
          >

            <img
              src={product.image}
              alt={product.name}
            />

            <h2>
              {product.name}
            </h2>

            <h3>
              ₹{product.price}
            </h3>

            <button
              onClick={() =>
                addToCart(product)
              }
            >
              Add to Cart
            </button>

          </div>

        ))}

      </div>

    </div>
  );
}

export default Products;
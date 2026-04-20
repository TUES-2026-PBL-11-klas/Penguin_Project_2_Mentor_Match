import React from 'react';
import { useNavigate } from 'react-router-dom';
import './HomePage.css';

const BG_IMAGE = 'https://www.figma.com/api/mcp/asset/045f166c-aee5-4149-9025-c8f67bf7cab0';
const SEARCH_ICON = 'https://www.figma.com/api/mcp/asset/64925700-9ebf-4f4a-8345-93ebaf6839a2';

const HomePage = () => {
  const navigate = useNavigate();

  return (
    <main className="homepage">
      {/* Background gradient mesh */}
      <div className="homepage__bg" aria-hidden="true">
        <img src={BG_IMAGE} alt="" className="homepage__bg-image" />
      </div>

      {/* Navbar */}
      <nav className="homepage__navbar">
        {/* Search bar */}
        <div className="homepage__search-bar">
          <img src={SEARCH_ICON} alt="search" className="homepage__search-icon" />
          <span className="homepage__search-placeholder">Search...</span>
        </div>

        {/* Auth buttons */}
        <div className="homepage__auth-buttons">
          <button
            className="homepage__auth-btn"
            onClick={() => navigate('/login')}
          >
            Log In
          </button>
          <button
            className="homepage__auth-btn"
            onClick={() => navigate('/register')}
          >
            Sign Up
          </button>
        </div>
      </nav>

      {/* Hero text */}
      <section className="homepage__hero">
        <h1 className="homepage__logo-text">
          <span className="homepage__logo-bold">Mentor</span>
          <span className="homepage__logo-regular">Match</span>
        </h1>
      </section>
    </main>
  );
};

export default HomePage;

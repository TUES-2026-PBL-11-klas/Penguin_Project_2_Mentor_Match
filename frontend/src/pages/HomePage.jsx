import React from 'react';
import { useNavigate } from 'react-router-dom';
import './HomePage.css';

const BG_IMAGE = 'https://www.figma.com/api/mcp/asset/045f166c-aee5-4149-9025-c8f67bf7cab0';
const SEARCH_ICON = 'https://www.figma.com/api/mcp/asset/64925700-9ebf-4f4a-8345-93ebaf6839a2';

const getRole = () => {
  const token = localStorage.getItem('token');
  if (!token) return null;
  try {
    return JSON.parse(atob(token.split('.')[1])).role;
  } catch {
    return null;
  }
};

const HomePage = () => {
  const navigate = useNavigate();
  const role = getRole();
  const isLoggedIn = !!role;

  const handleLogout = () => {
    localStorage.removeItem('token');
    window.location.reload();
  };

  return (
    <main className="homepage">
      <div className="homepage__bg" aria-hidden="true">
        <img src={BG_IMAGE} alt="" className="homepage__bg-image" />
      </div>

      <nav className="homepage__navbar">
        {/* Search — само за student и both */}
        {isLoggedIn && (role === 'student' || role === 'both') && (
          <div
            className="homepage__search-bar"
            onClick={() => navigate('/search')}
            style={{ cursor: 'pointer' }}
          >
            <img src={SEARCH_ICON} alt="search" className="homepage__search-icon" />
            <span className="homepage__search-placeholder">Search mentors...</span>
          </div>
        )}

        <div className="homepage__auth-buttons">
          {isLoggedIn ? (
            <>
              <button
                className="homepage__auth-btn"
                onClick={() => navigate('/profile')}
              >
                Profile
              </button>
              {(role === 'mentor' || role === 'both') && (
                <button
                  className="homepage__auth-btn"
                  onClick={() => navigate('/sessions')}
                >
                  Sessions
                </button>
              )}
              <button
                className="homepage__auth-btn"
                onClick={handleLogout}
              >
                Log Out
              </button>
            </>
          ) : (
            <>
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
            </>
          )}
        </div>
      </nav>

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

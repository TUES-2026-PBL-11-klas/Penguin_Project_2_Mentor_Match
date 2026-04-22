import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

const SEARCH_ICON = 'https://www.figma.com/api/mcp/asset/64925700-9ebf-4f4a-8345-93ebaf6839a2';

const getRole = () => {
  const token = sessionStorage.getItem('token');
  if (!token) return null;
  try {
    return JSON.parse(atob(token.split('.')[1])).role;
  } catch {
    return null;
  }
};

const getMentorId = () => {
  const token = sessionStorage.getItem('token');
  if (!token) return null;
  try {
    return JSON.parse(atob(token.split('.')[1])).sub;
  } catch {
    return null;
  }
};

const Navbar = () => {
  const navigate = useNavigate();
  const role = getRole();
  const mentorId = getMentorId();
  const [dropdownOpen, setDropdownOpen] = useState(false);

  const handleLogout = () => {
    sessionStorage.removeItem('token');
    navigate('/');
  };

  return (
    <nav style={{
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      padding: '16px 32px',
      position: 'absolute',
      top: 0,
      left: 0,
      right: 0,
      zIndex: 10,
    }}>
      {(role === 'student' || role === 'both') && (
        <div
          onClick={() => navigate('/search')}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            cursor: 'pointer',
            background: 'rgba(255,255,255,0.3)',
            borderRadius: '20px',
            padding: '8px 16px',
          }}
        >
          <img src={SEARCH_ICON} alt="search" style={{ width: '16px', height: '16px' }} />
          <span style={{ color: '#1a1a6e', fontSize: '14px' }}>Search mentors...</span>
        </div>
      )}

      <div style={{ display: 'flex', gap: '12px', marginLeft: 'auto', alignItems: 'center', position: 'relative' }}>

        {/* Profile dropdown */}
        <div style={{ position: 'relative' }}>
          <button
            onClick={() => setDropdownOpen(!dropdownOpen)}
            style={{
              background: 'rgba(255,255,255,0.3)',
              border: 'none',
              borderRadius: '20px',
              padding: '8px 20px',
              color: '#1a1a6e',
              fontWeight: '600',
              cursor: 'pointer',
              fontSize: '14px',
            }}
          >
            Profile ▾
          </button>

          {dropdownOpen && (
            <div style={{
              position: 'absolute',
              top: '110%',
              right: 0,
              background: 'white',
              borderRadius: '12px',
              boxShadow: '0 4px 20px rgba(0,0,0,0.15)',
              minWidth: '160px',
              overflow: 'hidden',
              zIndex: 100,
            }}>
              <button
                onClick={() => { setDropdownOpen(false); navigate('/profile'); }}
                style={{
                  display: 'block',
                  width: '100%',
                  padding: '12px 16px',
                  background: 'none',
                  border: 'none',
                  textAlign: 'left',
                  cursor: 'pointer',
                  fontSize: '14px',
                  color: '#1a1a6e',
                  fontWeight: '500',
                }}
              >
                My Profile
              </button>

              {(role === 'mentor' || role === 'both') && (
                <button
                  onClick={() => { setDropdownOpen(false); navigate(`/mentor/${mentorId}/reviews`); }}
                  style={{
                    display: 'block',
                    width: '100%',
                    padding: '12px 16px',
                    background: 'none',
                    border: 'none',
                    textAlign: 'left',
                    cursor: 'pointer',
                    fontSize: '14px',
                    color: '#1a1a6e',
                    fontWeight: '500',
                    borderTop: '1px solid #eee',
                  }}
                >
                  My Reviews
                </button>
              )}

              {(role === 'mentor' || role === 'both') && (
                <button
                  onClick={() => { setDropdownOpen(false); navigate('/sessions'); }}
                  style={{
                    display: 'block',
                    width: '100%',
                    padding: '12px 16px',
                    background: 'none',
                    border: 'none',
                    textAlign: 'left',
                    cursor: 'pointer',
                    fontSize: '14px',
                    color: '#1a1a6e',
                    fontWeight: '500',
                    borderTop: '1px solid #eee',
                  }}
                >
                  Sessions
                </button>
              )}

              <button
                onClick={handleLogout}
                style={{
                  display: 'block',
                  width: '100%',
                  padding: '12px 16px',
                  background: 'none',
                  border: 'none',
                  textAlign: 'left',
                  cursor: 'pointer',
                  fontSize: '14px',
                  color: '#e74c3c',
                  fontWeight: '500',
                  borderTop: '1px solid #eee',
                }}
              >
                Log Out
              </button>
            </div>
          )}
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
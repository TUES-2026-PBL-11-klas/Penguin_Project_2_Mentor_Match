import React, { useState, useEffect, useRef } from 'react';
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

const TYPE_LABELS = {
  new_request: 'New Request',
  session_confirmed: 'Session Confirmed',
  session_declined: 'Session Declined',
  session_reminder: 'Reminder',
  rate_session: 'Rate Session',
};

const Navbar = () => {
  const navigate = useNavigate();
  const role = getRole();
  const mentorId = getMentorId();
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const [notifOpen, setNotifOpen] = useState(false);
  const [notifications, setNotifications] = useState([]);
  const notifRef = useRef(null);

  const token = sessionStorage.getItem('token');

  useEffect(() => {
    if (!token) return;
    const fetchNotifs = () => {
      fetch('/api/notifications/', { headers: { Authorization: `Bearer ${token}` } })
        .then((r) => r.ok ? r.json() : [])
        .then(setNotifications)
        .catch(() => {});
    };
    fetchNotifs();
    const interval = setInterval(fetchNotifs, 30000);
    return () => clearInterval(interval);
  }, [token]);

  useEffect(() => {
    const handleClick = (e) => {
      if (notifRef.current && !notifRef.current.contains(e.target)) {
        setNotifOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClick);
    return () => document.removeEventListener('mousedown', handleClick);
  }, []);

  const unreadCount = notifications.filter((n) => !n.is_read).length;

  const handleMarkRead = async (id) => {
    try {
      await fetch(`/api/notifications/${id}/read`, {
        method: 'PATCH',
        headers: { Authorization: `Bearer ${token}` },
      });
      setNotifications((prev) =>
        prev.map((n) => (n.id === id ? { ...n, is_read: true } : n))
      );
    } catch {}
  };

  const handleLogout = () => {
    sessionStorage.removeItem('token');
    navigate('/');
  };

  const sessionsPath = (role === 'mentor' || role === 'both') ? '/sessions' : '/student/sessions';

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

        {/* Notification bell */}
        <div ref={notifRef} style={{ position: 'relative' }}>
          <button
            onClick={() => setNotifOpen(!notifOpen)}
            style={{
              background: 'rgba(255,255,255,0.3)',
              border: 'none',
              borderRadius: '20px',
              padding: '8px 14px',
              color: '#1a1a6e',
              cursor: 'pointer',
              fontSize: '16px',
              position: 'relative',
            }}
            aria-label="Notifications"
          >
            🔔
            {unreadCount > 0 && (
              <span style={{
                position: 'absolute',
                top: '2px',
                right: '4px',
                background: '#e74c3c',
                color: 'white',
                borderRadius: '50%',
                width: '16px',
                height: '16px',
                fontSize: '10px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontWeight: '700',
              }}>
                {unreadCount > 9 ? '9+' : unreadCount}
              </span>
            )}
          </button>

          {notifOpen && (
            <div style={{
              position: 'absolute',
              top: '110%',
              right: 0,
              background: 'white',
              borderRadius: '16px',
              boxShadow: '0 4px 24px rgba(0,0,0,0.15)',
              width: '320px',
              maxHeight: '400px',
              overflowY: 'auto',
              zIndex: 100,
            }}>
              <div style={{ padding: '14px 16px', borderBottom: '1px solid #eee', fontWeight: '700', color: '#1a1a6e', fontSize: '14px' }}>
                Notifications
              </div>
              {notifications.length === 0 && (
                <p style={{ padding: '16px', color: '#888', fontSize: '13px', textAlign: 'center' }}>No notifications.</p>
              )}
              {notifications.map((n) => (
                <div
                  key={n.id}
                  onClick={() => handleMarkRead(n.id)}
                  style={{
                    padding: '12px 16px',
                    borderBottom: '1px solid #f0f0f0',
                    background: n.is_read ? 'white' : 'rgba(80,100,220,0.06)',
                    cursor: 'pointer',
                  }}
                >
                  <p style={{ margin: '0 0 2px', fontSize: '12px', fontWeight: '600', color: '#4d5cd0' }}>
                    {TYPE_LABELS[n.type] || n.type}
                  </p>
                  <p style={{ margin: '0 0 4px', fontSize: '13px', color: '#1a1a6e' }}>{n.message}</p>
                  {n.created_at && (
                    <p style={{ margin: 0, fontSize: '11px', color: '#aaa' }}>
                      {new Date(n.created_at).toLocaleString()}
                    </p>
                  )}
                  {n.type === 'rate_session' && n.session_id && (
                    <button
                      onClick={(e) => { e.stopPropagation(); setNotifOpen(false); navigate(`/review/${n.session_id}`); }}
                      style={{
                        marginTop: '6px',
                        background: 'rgba(60,180,120,0.8)',
                        border: 'none',
                        borderRadius: '10px',
                        padding: '4px 12px',
                        color: 'white',
                        fontSize: '11px',
                        cursor: 'pointer',
                        fontWeight: '600',
                      }}
                    >
                      Leave Review
                    </button>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>

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
                style={{ display: 'block', width: '100%', padding: '12px 16px', background: 'none', border: 'none', textAlign: 'left', cursor: 'pointer', fontSize: '14px', color: '#1a1a6e', fontWeight: '500' }}
              >
                My Profile
              </button>

              {(role === 'mentor' || role === 'both') && (
                <button
                  onClick={() => { setDropdownOpen(false); navigate(`/mentor/${mentorId}/reviews`); }}
                  style={{ display: 'block', width: '100%', padding: '12px 16px', background: 'none', border: 'none', textAlign: 'left', cursor: 'pointer', fontSize: '14px', color: '#1a1a6e', fontWeight: '500', borderTop: '1px solid #eee' }}
                >
                  My Reviews
                </button>
              )}

              <button
                onClick={() => { setDropdownOpen(false); navigate(sessionsPath); }}
                style={{ display: 'block', width: '100%', padding: '12px 16px', background: 'none', border: 'none', textAlign: 'left', cursor: 'pointer', fontSize: '14px', color: '#1a1a6e', fontWeight: '500', borderTop: '1px solid #eee' }}
              >
                Sessions
              </button>

              <button
                onClick={handleLogout}
                style={{ display: 'block', width: '100%', padding: '12px 16px', background: 'none', border: 'none', textAlign: 'left', cursor: 'pointer', fontSize: '14px', color: '#e74c3c', fontWeight: '500', borderTop: '1px solid #eee' }}
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

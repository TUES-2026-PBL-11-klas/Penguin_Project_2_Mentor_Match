import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

const pad = (n) => String(n).padStart(2, '0');

const formatDate = (iso) => {
  const d = new Date(iso);
  return `${pad(d.getDate())}/${pad(d.getMonth() + 1)}/${d.getFullYear()}`;
};

const formatTime = (iso) => {
  const d = new Date(iso);
  return `${pad(d.getHours())}:${pad(d.getMinutes())}`;
};

const StudentSessionsPage = () => {
  const navigate = useNavigate();
  const token = sessionStorage.getItem('token');

  const [upcoming, setUpcoming] = useState([]);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [cancelError, setCancelError] = useState('');

  useEffect(() => {
    if (!token) { navigate('/login'); return; }
    const headers = { Authorization: `Bearer ${token}` };
    Promise.all([
      fetch('/api/sessions/student/calendar', { headers }),
      fetch('/api/sessions/student/history', { headers }),
    ]).then(async ([calRes, histRes]) => {
      setUpcoming(calRes.ok ? await calRes.json() : []);
      setHistory(histRes.ok ? await histRes.json() : []);
    }).catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [token, navigate]);

  const handleCancel = async (sessionId) => {
    setCancelError('');
    try {
      const res = await fetch(`/api/sessions/${sessionId}/cancel`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!res.ok) {
        const d = await res.json();
        throw new Error(d.error || 'Failed to cancel.');
      }
      setUpcoming((prev) => prev.filter((s) => s.id !== sessionId));
    } catch (err) {
      setCancelError(err.message);
    }
  };

  const cardStyle = {
    background: 'rgba(255,255,255,0.18)',
    backdropFilter: 'blur(12px)',
    borderRadius: '16px',
    padding: '18px 22px',
    marginBottom: '12px',
    border: '1px solid rgba(255,255,255,0.25)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    flexWrap: 'wrap',
    gap: '12px',
  };

  return (
    <main style={{
      minHeight: '100vh',
      background: 'radial-gradient(ellipse at 20% 50%, rgba(100,120,255,0.5) 0%, transparent 50%), radial-gradient(ellipse at 80% 20%, rgba(150,180,255,0.4) 0%, transparent 40%), linear-gradient(135deg, #0a1a6e 0%, #1a3a9f 50%, #0d1f7a 100%)',
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      padding: '40px 20px',
      fontFamily: 'system-ui, sans-serif',
    }}>

      <div style={{ width: '100%', maxWidth: '860px', marginBottom: '16px' }}>
        <button onClick={() => navigate('/profile')} style={{
          background: 'rgba(255,255,255,0.2)',
          border: 'none',
          borderRadius: '20px',
          padding: '8px 20px',
          color: 'white',
          cursor: 'pointer',
          fontSize: '14px',
        }}>← Back to Profile</button>
      </div>

      <div style={{
        width: '100%',
        maxWidth: '860px',
        background: 'rgba(255,255,255,0.15)',
        backdropFilter: 'blur(20px)',
        borderRadius: '24px',
        padding: '32px',
        border: '1px solid rgba(255,255,255,0.25)',
      }}>
        <h1 style={{ color: '#1a1a6e', fontWeight: '700', fontSize: '22px', marginBottom: '28px' }}>
          My Sessions
        </h1>

        {loading && <p style={{ color: '#1a1a6e' }}>Loading...</p>}
        {error && <p style={{ color: '#c0392b', fontSize: '14px' }}>{error}</p>}
        {cancelError && <p style={{ color: '#c0392b', fontSize: '13px', marginBottom: '8px' }}>{cancelError}</p>}

        {/* ── Upcoming ── */}
        <h2 style={{ color: '#1a1a6e', fontSize: '16px', fontWeight: '700', marginBottom: '14px' }}>
          Upcoming Sessions
        </h2>

        {!loading && upcoming.length === 0 && (
          <p style={{ color: 'rgba(26,26,110,0.6)', fontSize: '14px', marginBottom: '24px' }}>
            No upcoming sessions.
          </p>
        )}

        {upcoming.map((s) => (
          <div key={s.id} style={cardStyle}>
            <div>
              <p style={{ color: '#1a1a6e', fontWeight: '600', fontSize: '15px', margin: '0 0 4px' }}>
                {s.subject_name || `Subject #${s.subject_id}`}
              </p>
              <p style={{ color: 'rgba(26,26,110,0.7)', fontSize: '13px', margin: '0 0 2px' }}>
                Mentor: {s.mentor_name || s.mentor_id}
              </p>
              <p style={{ color: 'rgba(26,26,110,0.7)', fontSize: '13px', margin: 0 }}>
                {formatDate(s.scheduled_at)} · {formatTime(s.scheduled_at)} — {formatTime(s.end_at)} · {s.duration_minutes} min
              </p>
            </div>
            <button
              onClick={() => handleCancel(s.id)}
              style={{
                background: 'rgba(192,57,43,0.7)',
                border: 'none',
                borderRadius: '14px',
                padding: '8px 18px',
                color: 'white',
                cursor: 'pointer',
                fontSize: '13px',
                fontWeight: '600',
              }}
            >
              Cancel
            </button>
          </div>
        ))}

        {/* ── History ── */}
        <h2 style={{ color: '#1a1a6e', fontSize: '16px', fontWeight: '700', margin: '28px 0 14px' }}>
          Session History
        </h2>

        {!loading && history.length === 0 && (
          <p style={{ color: 'rgba(26,26,110,0.6)', fontSize: '14px' }}>
            No completed sessions yet.
          </p>
        )}

        {history.map((s) => (
          <div key={s.id} style={cardStyle}>
            <div>
              <p style={{ color: '#1a1a6e', fontWeight: '600', fontSize: '15px', margin: '0 0 4px' }}>
                {s.subject_name || `Subject #${s.subject_id}`}
              </p>
              <p style={{ color: 'rgba(26,26,110,0.7)', fontSize: '13px', margin: '0 0 2px' }}>
                Mentor: {s.mentor_name || s.mentor_id}
              </p>
              <p style={{ color: 'rgba(26,26,110,0.7)', fontSize: '13px', margin: 0 }}>
                {formatDate(s.scheduled_at)} · {s.duration_minutes} min
              </p>
            </div>
            {!s.has_review && (
              <button
                onClick={() => navigate(`/review/${s.id}`)}
                style={{
                  background: 'rgba(60,180,120,0.8)',
                  border: 'none',
                  borderRadius: '14px',
                  padding: '8px 18px',
                  color: 'white',
                  cursor: 'pointer',
                  fontSize: '13px',
                  fontWeight: '600',
                }}
              >
                Leave Review
              </button>
            )}
            {s.has_review && (
              <span style={{ color: 'rgba(26,26,110,0.5)', fontSize: '13px' }}>Reviewed</span>
            )}
          </div>
        ))}
      </div>

      <footer style={{ marginTop: '24px', color: 'white', fontSize: '16px' }}>
        <span style={{ fontWeight: '700' }}>Mentor</span>
        <span style={{ fontWeight: '300' }}>Match</span>
      </footer>
    </main>
  );
};

export default StudentSessionsPage;

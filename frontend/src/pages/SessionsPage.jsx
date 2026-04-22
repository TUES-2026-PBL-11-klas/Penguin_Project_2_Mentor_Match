import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import Navbar from '../components/Navbar';

const BG_IMAGE = 'https://www.figma.com/api/mcp/asset/ac149af1-46e1-488c-9826-40e3c006effa';

const fmt = (iso) => {
  const d = new Date(iso);
  return d.toLocaleString([], {
    weekday: 'short', month: 'short', day: 'numeric',
    hour: '2-digit', minute: '2-digit',
  });
};

const fmtTime = (iso) =>
  new Date(iso).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

const STATUS_COLORS = {
  pending:   { bg: 'rgba(255,180,0,0.2)',   border: 'rgba(255,180,0,0.6)',   text: '#7a5500' },
  confirmed: { bg: 'rgba(40,167,69,0.15)',  border: 'rgba(40,167,69,0.5)',   text: '#155724' },
  declined:  { bg: 'rgba(220,53,69,0.15)',  border: 'rgba(220,53,69,0.5)',   text: '#721c24' },
  cancelled: { bg: 'rgba(108,117,125,0.15)',border: 'rgba(108,117,125,0.5)', text: '#383d41' },
  completed: { bg: 'rgba(77,92,208,0.15)',  border: 'rgba(77,92,208,0.5)',   text: '#1a1a6e' },
};

const badge = (status) => {
  const c = STATUS_COLORS[status] || STATUS_COLORS.pending;
  return (
    <span style={{
      background: c.bg, border: `1px solid ${c.border}`, color: c.text,
      borderRadius: '12px', padding: '2px 10px', fontSize: '12px', fontWeight: '600',
      textTransform: 'capitalize',
    }}>
      {status}
    </span>
  );
};

const card = {
  background: 'rgba(255,255,255,0.55)',
  border: '1px solid #4d5cd0',
  borderRadius: '20px',
  padding: '18px 24px',
  display: 'flex',
  flexDirection: 'column',
  gap: '6px',
  boxSizing: 'border-box',
};

const SessionsPage = () => {
  const navigate = useNavigate();
  const token = sessionStorage.getItem('token');

  const [subjects, setSubjects] = useState({});
  const [pending, setPending] = useState([]);
  const [upcoming, setUpcoming] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [actionMsg, setActionMsg] = useState('');

  const flash = (msg) => { setActionMsg(msg); setTimeout(() => setActionMsg(''), 3000); };

  const fetchAll = useCallback(async () => {
    if (!token) { navigate('/login'); return; }
    const headers = { Authorization: `Bearer ${token}` };
    try {
      const [subjRes, pendRes, calRes] = await Promise.all([
        fetch('/api/auth/subjects', { headers }),
        fetch('/api/sessions/requests', { headers }),
        fetch('/api/sessions/mentor/calendar', { headers }),
      ]);
      if (subjRes.ok) {
        const arr = await subjRes.json();
        setSubjects(Object.fromEntries(arr.map((s) => [s.id, s.name])));
      }
      setPending(pendRes.ok ? await pendRes.json() : []);
      setUpcoming(calRes.ok ? await calRes.json() : []);
    } catch {
      setError('Failed to load sessions.');
    } finally {
      setLoading(false);
    }
  }, [token, navigate]);

  useEffect(() => { fetchAll(); }, [fetchAll]);

  const handleAction = async (sessionId, action) => {
    try {
      const res = await fetch(`/api/sessions/${sessionId}/${action}`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!res.ok) {
        const d = await res.json();
        throw new Error(d.error || `Failed to ${action}.`);
      }
      flash(`Session ${action}ed.`);
      fetchAll();
    } catch (err) {
      setError(err.message);
    }
  };

  const handleCancel = (sessionId) => handleAction(sessionId, 'cancel');
  const handleConfirm = (sessionId) => handleAction(sessionId, 'confirm');
  const handleDecline = (sessionId) => handleAction(sessionId, 'decline');

  const sectionTitle = (text) => (
    <h2 style={{
      fontFamily: 'Syne, sans-serif', fontWeight: 800, fontSize: '22px',
      color: '#05068a', margin: '0 0 14px',
    }}>
      {text}
    </h2>
  );

  const empty = (text) => (
    <p style={{ color: 'rgba(5,6,138,0.5)', fontSize: '14px', fontFamily: 'DM Sans, sans-serif', margin: 0 }}>
      {text}
    </p>
  );

  return (
    <main style={{
      position: 'relative', minHeight: '100vh', width: '100%',
      display: 'flex', flexDirection: 'column', alignItems: 'center',
      justifyContent: 'flex-start', overflow: 'hidden',
      background: '#0a0f5c', padding: '100px 20px 60px', boxSizing: 'border-box',
    }}>
      <div style={{ position: 'absolute', inset: 0, pointerEvents: 'none', overflow: 'hidden' }}>
        <img src={BG_IMAGE} alt="" style={{
          position: 'absolute', width: '120.45%', height: '103.89%',
          top: '-2.05%', left: '-10.23%', maxWidth: 'none', objectFit: 'cover',
        }} />
      </div>

      <Navbar />

      <div style={{
        position: 'relative', zIndex: 10,
        width: '100%', maxWidth: '860px',
        display: 'flex', flexDirection: 'column', gap: '24px',
      }}>

        {/* Header row */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <h1 style={{
            fontFamily: 'Syne, sans-serif', fontWeight: 800, fontSize: '32px',
            color: '#ffffff', margin: 0,
          }}>
            Sessions
          </h1>
          <button
            onClick={() => navigate('/profile')}
            style={{
              background: 'rgba(255,255,255,0.2)', border: 'none', borderRadius: '20px',
              padding: '8px 20px', color: 'white', cursor: 'pointer', fontSize: '14px',
            }}
          >
            ← Back to Profile
          </button>
        </div>

        {actionMsg && (
          <div style={{
            background: 'rgba(40,167,69,0.2)', border: '1px solid rgba(40,167,69,0.5)',
            borderRadius: '12px', padding: '10px 16px',
            color: '#d4edda', fontSize: '14px', fontFamily: 'DM Sans, sans-serif',
          }}>
            {actionMsg}
          </div>
        )}

        {error && (
          <div style={{
            background: 'rgba(220,53,69,0.2)', border: '1px solid rgba(220,53,69,0.5)',
            borderRadius: '12px', padding: '10px 16px',
            color: '#f8d7da', fontSize: '14px', fontFamily: 'DM Sans, sans-serif',
          }}>
            {error}
          </div>
        )}

        {loading ? (
          <p style={{ color: '#ffffff', fontFamily: 'DM Sans, sans-serif' }}>Loading...</p>
        ) : (
          <>
            {/* ── Pending Requests ── */}
            <section style={{ ...card, borderRadius: '32px', padding: '28px 32px' }}>
              {sectionTitle(`Pending Requests (${pending.length})`)}
              {pending.length === 0
                ? empty('No pending requests.')
                : pending.map((s) => (
                    <div key={s.id} style={{
                      background: 'rgba(255,255,255,0.6)', border: '1px solid rgba(77,92,208,0.3)',
                      borderRadius: '16px', padding: '16px 20px',
                      display: 'flex', flexDirection: 'column', gap: '6px',
                      marginBottom: '10px',
                    }}>
                      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '8px' }}>
                        <span style={{ fontFamily: 'Syne, sans-serif', fontWeight: 700, fontSize: '16px', color: '#05068a' }}>
                          {subjects[s.subject_id] || `Subject #${s.subject_id}`}
                        </span>
                        {badge('pending')}
                      </div>
                      <span style={{ fontFamily: 'DM Sans, sans-serif', fontSize: '14px', color: 'rgba(5,6,138,0.7)' }}>
                        {fmt(s.scheduled_at)} — {fmtTime(s.end_at)} · {s.duration_minutes} min
                      </span>
                      {s.notes && (
                        <span style={{ fontFamily: 'DM Sans, sans-serif', fontSize: '13px', color: 'rgba(5,6,138,0.55)', fontStyle: 'italic' }}>
                          "{s.notes}"
                        </span>
                      )}
                      <div style={{ display: 'flex', gap: '10px', marginTop: '6px' }}>
                        <button
                          onClick={() => handleConfirm(s.id)}
                          style={{
                            background: 'rgba(40,167,69,0.8)', border: 'none', borderRadius: '12px',
                            padding: '6px 18px', color: 'white', fontWeight: '600',
                            cursor: 'pointer', fontSize: '13px',
                          }}
                        >
                          Confirm
                        </button>
                        <button
                          onClick={() => handleDecline(s.id)}
                          style={{
                            background: 'rgba(220,53,69,0.7)', border: 'none', borderRadius: '12px',
                            padding: '6px 18px', color: 'white', fontWeight: '600',
                            cursor: 'pointer', fontSize: '13px',
                          }}
                        >
                          Decline
                        </button>
                      </div>
                    </div>
                  ))
              }
            </section>

            {/* ── Upcoming Sessions ── */}
            <section style={{ ...card, borderRadius: '32px', padding: '28px 32px' }}>
              {sectionTitle(`Upcoming Sessions (${upcoming.length})`)}
              {upcoming.length === 0
                ? empty('No upcoming sessions.')
                : upcoming.map((s) => (
                    <div key={s.id} style={{
                      background: 'rgba(255,255,255,0.6)', border: '1px solid rgba(77,92,208,0.3)',
                      borderRadius: '16px', padding: '16px 20px',
                      display: 'flex', flexDirection: 'column', gap: '6px',
                      marginBottom: '10px',
                    }}>
                      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '8px' }}>
                        <span style={{ fontFamily: 'Syne, sans-serif', fontWeight: 700, fontSize: '16px', color: '#05068a' }}>
                          {subjects[s.subject_id] || `Subject #${s.subject_id}`}
                        </span>
                        {badge(s.status)}
                      </div>
                      <span style={{ fontFamily: 'DM Sans, sans-serif', fontSize: '14px', color: 'rgba(5,6,138,0.7)' }}>
                        {fmt(s.scheduled_at)} — {fmtTime(s.end_at)} · {s.duration_minutes} min
                      </span>
                      {s.notes && (
                        <span style={{ fontFamily: 'DM Sans, sans-serif', fontSize: '13px', color: 'rgba(5,6,138,0.55)', fontStyle: 'italic' }}>
                          "{s.notes}"
                        </span>
                      )}
                      <div style={{ marginTop: '6px' }}>
                        <button
                          onClick={() => handleCancel(s.id)}
                          style={{
                            background: 'rgba(108,117,125,0.6)', border: 'none', borderRadius: '12px',
                            padding: '6px 18px', color: 'white', fontWeight: '600',
                            cursor: 'pointer', fontSize: '13px',
                          }}
                        >
                          Cancel
                        </button>
                      </div>
                    </div>
                  ))
              }
            </section>
          </>
        )}
      </div>

      <footer style={{ position: 'relative', zIndex: 10, marginTop: '32px', fontSize: '20px' }}>
        <span style={{ fontFamily: 'Syne, sans-serif', fontWeight: 800, color: '#ffffff' }}>Mentor</span>
        <span style={{ fontFamily: 'DM Sans, sans-serif', fontWeight: 300, color: '#ffffff' }}>Match</span>
      </footer>
    </main>
  );
};

export default SessionsPage;

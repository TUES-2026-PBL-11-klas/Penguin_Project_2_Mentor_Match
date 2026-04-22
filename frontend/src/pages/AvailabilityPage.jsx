import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

const MONTH_NAMES = [
  'January', 'February', 'March', 'April', 'May', 'June',
  'July', 'August', 'September', 'October', 'November', 'December',
];
const DAY_NAMES = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];

const buildCalendarDays = (year, month) => {
  const firstDay = new Date(year, month, 1);
  const startOffset = (firstDay.getDay() + 6) % 7;
  const daysInMonth = new Date(year, month + 1, 0).getDate();
  const cells = [];
  for (let i = 0; i < startOffset; i++) cells.push(null);
  for (let d = 1; d <= daysInMonth; d++) cells.push(d);
  while (cells.length % 7 !== 0) cells.push(null);
  return cells;
};

const pad = (n) => String(n).padStart(2, '0');

const AvailabilityPage = () => {
  const navigate = useNavigate();
  const token = sessionStorage.getItem('token');
  const today = new Date();

  const [calYear, setCalYear] = useState(today.getFullYear());
  const [calMonth, setCalMonth] = useState(today.getMonth());
  const [unavailableSlots, setUnavailableSlots] = useState([]);
  const [confirmedSessions, setConfirmedSessions] = useState([]);
  const [selectedDay, setSelectedDay] = useState(null);
  const [startTime, setStartTime] = useState('');
  const [endTime, setEndTime] = useState('');
  const [reason, setReason] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(true);

  const getMentorId = () => {
    try {
      return JSON.parse(atob(token.split('.')[1])).sub;
    } catch { return null; }
  };

  const mentorId = getMentorId();

  useEffect(() => {
    if (!token) { navigate('/login'); return; }
    fetchSlots();
  }, []);

  const fetchSlots = async () => {
    try {
      const [unavailRes, sessRes] = await Promise.all([
        fetch(`/api/sessions/unavailable?mentor_id=${mentorId}`, {
          headers: { Authorization: `Bearer ${token}` },
        }),
        fetch('/api/sessions/mentor/calendar', {
          headers: { Authorization: `Bearer ${token}` },
        }),
      ]);
      setUnavailableSlots(unavailRes.ok ? await unavailRes.json() : []);
      setConfirmedSessions(sessRes.ok ? await sessRes.json() : []);
    } catch {
      setUnavailableSlots([]);
      setConfirmedSessions([]);
    } finally {
      setLoading(false);
    }
  };

  const handleAddSlot = async () => {
    setError('');
    if (!selectedDay || !startTime || !endTime) {
      setError('Please select a day and fill in start and end time.');
      return;
    }
    if (startTime >= endTime) {
      setError('End time must be after start time.');
      return;
    }

    const dateStr = `${calYear}-${pad(calMonth + 1)}-${pad(selectedDay)}`;

    try {
      const res = await fetch('/api/sessions/unavailable', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          start_datetime: `${dateStr}T${startTime}:00`,
          end_datetime: `${dateStr}T${endTime}:00`,
          reason: reason || undefined,
        }),
      });
      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.message || 'Failed to add slot.');
      }
      setSuccess('Unavailable slot added!');
      setTimeout(() => setSuccess(''), 3000);
      setSelectedDay(null);
      setStartTime('');
      setEndTime('');
      setReason('');
      fetchSlots();
    } catch (err) {
      setError(err.message);
    }
  };

  const handleDeleteSlot = async (slotId) => {
    try {
      await fetch(`/api/sessions/unavailable/${slotId}`, {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${token}` },
      });
      fetchSlots();
    } catch {
      setError('Failed to delete slot.');
    }
  };

  const unavailableDays = new Set(
    unavailableSlots
      .map((s) => new Date(s.start_datetime))
      .filter((d) => d.getFullYear() === calYear && d.getMonth() === calMonth)
      .map((d) => d.getDate())
  );

  const sessionDays = new Set(
    confirmedSessions
      .map((s) => new Date(s.scheduled_at))
      .filter((d) => d.getFullYear() === calYear && d.getMonth() === calMonth)
      .map((d) => d.getDate())
  );

  const calDays = buildCalendarDays(calYear, calMonth);

  const prevMonth = () => {
    setSelectedDay(null);
    if (calMonth === 0) { setCalMonth(11); setCalYear((y) => y - 1); }
    else setCalMonth((m) => m - 1);
  };
  const nextMonth = () => {
    setSelectedDay(null);
    if (calMonth === 11) { setCalMonth(0); setCalYear((y) => y + 1); }
    else setCalMonth((m) => m + 1);
  };

  const slotsForSelectedDay = selectedDay
    ? unavailableSlots.filter((s) => {
        const d = new Date(s.start_datetime);
        return d.getFullYear() === calYear && d.getMonth() === calMonth && d.getDate() === selectedDay;
      })
    : [];

  return (
    <main style={{
      minHeight: '100vh',
      background: 'radial-gradient(ellipse at 20% 50%, rgba(100,120,255,0.5) 0%, transparent 50%), radial-gradient(ellipse at 80% 20%, rgba(150,180,255,0.4) 0%, transparent 40%), linear-gradient(135deg, #0a1a6e 0%, #1a3a9f 50%, #0d1f7a 100%)',
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '40px 20px',
      fontFamily: 'system-ui, sans-serif',
    }}>

      {/* Back button */}
      <div style={{ width: '100%', maxWidth: '900px', marginBottom: '16px' }}>
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
        maxWidth: '900px',
        background: 'rgba(255,255,255,0.15)',
        backdropFilter: 'blur(20px)',
        borderRadius: '24px',
        padding: '32px',
        border: '1px solid rgba(255,255,255,0.25)',
      }}>
        <h1 style={{ color: '#1a1a6e', fontWeight: '700', fontSize: '22px', marginBottom: '24px' }}>
          Manage Availability
        </h1>

        {/* Calendar navigation */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '24px', marginBottom: '16px' }}>
          <button onClick={prevMonth} style={{ background: 'none', border: 'none', fontSize: '20px', cursor: 'pointer', color: '#1a1a6e' }}>‹</button>
          <h2 style={{ color: '#1a1a6e', fontWeight: '700', fontSize: '20px', margin: 0 }}>
            {MONTH_NAMES[calMonth]} {calYear}
          </h2>
          <button onClick={nextMonth} style={{ background: 'none', border: 'none', fontSize: '20px', cursor: 'pointer', color: '#1a1a6e' }}>›</button>
        </div>

        {/* Calendar grid */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(7, 1fr)', gap: '4px', marginBottom: '24px' }}>
          {DAY_NAMES.map((day) => (
            <div key={day} style={{ textAlign: 'center', fontWeight: '600', fontSize: '12px', color: '#3a3a8e', padding: '8px 0' }}>
              {day.slice(0, 3)}
            </div>
          ))}
          {calDays.map((day, idx) => {
            const isToday = day === today.getDate() && calMonth === today.getMonth() && calYear === today.getFullYear();
            const isSelected = day === selectedDay;
            const isUnavail = day && unavailableDays.has(day);
            const hasSession = day && sessionDays.has(day);

            return (
              <div
                key={idx}
                onClick={() => day && setSelectedDay(day)}
                style={{
                  textAlign: 'center',
                  padding: '10px 4px',
                  borderRadius: '8px',
                  cursor: day ? 'pointer' : 'default',
                  fontWeight: isToday ? '700' : '400',
                  fontSize: '14px',
                  position: 'relative',
                  background: isSelected
                    ? 'rgba(80,100,220,0.7)'
                    : isUnavail
                    ? 'rgba(220,80,80,0.4)'
                    : hasSession
                    ? 'rgba(60,180,120,0.35)'
                    : isToday
                    ? 'rgba(255,255,255,0.3)'
                    : 'transparent',
                  color: isSelected ? 'white' : '#1a1a6e',
                  border: isToday && !isSelected ? '2px solid rgba(80,100,220,0.5)' : 'none',
                }}
              >
                {day || ''}
              </div>
            );
          })}
        </div>

        {/* Legend */}
        <div style={{ display: 'flex', gap: '20px', marginBottom: '24px', fontSize: '13px', flexWrap: 'wrap' }}>
          <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <span style={{ width: '14px', height: '14px', borderRadius: '4px', background: 'rgba(220,80,80,0.4)', display: 'inline-block' }} />
            <span style={{ color: '#1a1a6e' }}>Unavailable</span>
          </span>
          <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <span style={{ width: '14px', height: '14px', borderRadius: '4px', background: 'rgba(60,180,120,0.35)', display: 'inline-block' }} />
            <span style={{ color: '#1a1a6e' }}>Confirmed Session</span>
          </span>
          <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <span style={{ width: '14px', height: '14px', borderRadius: '4px', background: 'rgba(80,100,220,0.7)', display: 'inline-block' }} />
            <span style={{ color: '#1a1a6e' }}>Selected</span>
          </span>
        </div>

        {/* Selected day form */}
        {selectedDay && (
          <div style={{
            background: 'rgba(255,255,255,0.3)',
            borderRadius: '16px',
            padding: '20px',
            marginBottom: '24px',
          }}>
            <h3 style={{ color: '#1a1a6e', marginBottom: '16px', fontSize: '16px' }}>
              Mark unavailable — {pad(selectedDay)}/{pad(calMonth + 1)}/{calYear}
            </h3>

            <div style={{ display: 'flex', gap: '16px', flexWrap: 'wrap', marginBottom: '12px' }}>
              <div>
                <label style={{ display: 'block', fontSize: '13px', color: '#3a3a8e', marginBottom: '4px' }}>Start time</label>
                <input type="time" value={startTime} onChange={(e) => setStartTime(e.target.value)}
                  style={{ padding: '8px 12px', borderRadius: '8px', border: '1px solid rgba(80,100,220,0.4)', background: 'rgba(255,255,255,0.7)', color: '#1a1a6e', fontSize: '14px' }} />
              </div>
              <div>
                <label style={{ display: 'block', fontSize: '13px', color: '#3a3a8e', marginBottom: '4px' }}>End time</label>
                <input type="time" value={endTime} onChange={(e) => setEndTime(e.target.value)}
                  style={{ padding: '8px 12px', borderRadius: '8px', border: '1px solid rgba(80,100,220,0.4)', background: 'rgba(255,255,255,0.7)', color: '#1a1a6e', fontSize: '14px' }} />
              </div>
              <div style={{ flex: 1, minWidth: '200px' }}>
                <label style={{ display: 'block', fontSize: '13px', color: '#3a3a8e', marginBottom: '4px' }}>Reason (optional)</label>
                <input type="text" value={reason} onChange={(e) => setReason(e.target.value)} placeholder="e.g. Exam"
                  style={{ padding: '8px 12px', borderRadius: '8px', border: '1px solid rgba(80,100,220,0.4)', background: 'rgba(255,255,255,0.7)', color: '#1a1a6e', fontSize: '14px', width: '100%' }} />
              </div>
            </div>

            {error && <p style={{ color: '#c0392b', fontSize: '13px', marginBottom: '8px' }}>{error}</p>}
            {success && <p style={{ color: '#27ae60', fontSize: '13px', marginBottom: '8px' }}>{success}</p>}

            <button onClick={handleAddSlot} style={{
              background: 'rgba(80,100,220,0.8)',
              border: 'none',
              borderRadius: '20px',
              padding: '10px 24px',
              color: 'white',
              fontWeight: '600',
              cursor: 'pointer',
              fontSize: '14px',
            }}>
              Mark as Unavailable
            </button>

            {/* Existing slots for this day */}
            {slotsForSelectedDay.length > 0 && (
              <div style={{ marginTop: '16px' }}>
                <p style={{ fontSize: '13px', color: '#3a3a8e', marginBottom: '8px' }}>Existing unavailable slots:</p>
                {slotsForSelectedDay.map((slot) => (
                  <div key={slot.id} style={{
                    display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                    background: 'rgba(220,80,80,0.2)', borderRadius: '8px', padding: '8px 12px', marginBottom: '6px',
                  }}>
                    <span style={{ fontSize: '13px', color: '#1a1a6e' }}>
                      {new Date(slot.start_datetime).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                      {' — '}
                      {new Date(slot.end_datetime).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                      {slot.reason ? ` (${slot.reason})` : ''}
                    </span>
                    <button onClick={() => handleDeleteSlot(slot.id)} style={{
                      background: 'rgba(192,57,43,0.7)', border: 'none', borderRadius: '12px',
                      padding: '4px 12px', color: 'white', cursor: 'pointer', fontSize: '12px',
                    }}>Delete</button>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Footer */}
      <footer style={{ marginTop: '24px', color: 'white', fontSize: '16px' }}>
        <span style={{ fontWeight: '700' }}>Mentor</span>
        <span style={{ fontWeight: '300' }}>Match</span>
      </footer>
    </main>
  );
};

export default AvailabilityPage;
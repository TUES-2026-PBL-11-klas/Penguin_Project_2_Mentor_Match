import React, { useState, useEffect, useRef } from 'react';
import { useNavigate, useParams, useLocation } from 'react-router-dom';
import './SessionBookingCalendarPage.css';

const BG_IMAGE = 'https://www.figma.com/api/mcp/asset/1ddeb178-7545-433b-b9de-bde0fc359784';

const DAY_NAMES = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
const MONTH_NAMES = [
  'January', 'February', 'March', 'April', 'May', 'June',
  'July', 'August', 'September', 'October', 'November', 'December',
];
const DAY_SHORT = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];

const buildCalendarDays = (year, month) => {
  const firstDay = new Date(year, month, 1);
  const startOffset = (firstDay.getDay() + 6) % 7; // Mon = 0
  const daysInMonth = new Date(year, month + 1, 0).getDate();
  const cells = [];
  for (let i = 0; i < startOffset; i++) cells.push(null);
  for (let d = 1; d <= daysInMonth; d++) cells.push(d);
  while (cells.length % 7 !== 0) cells.push(null);
  return cells;
};

const SessionBookingCalendarPage = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { mentorId } = useParams();
  const token = localStorage.getItem('token');

  // Mentor info + subjects passed from MentorSearchPage/MentorPublicProfilePage
  const mentorInfo = location.state?.mentor || null;

  const [subjects, setSubjects] = useState([]);
  const [unavailableSlots, setUnavailableSlots] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [successMsg, setSuccessMsg] = useState('');

  const today = new Date();
  const [calYear, setCalYear] = useState(today.getFullYear());
  const [calMonth, setCalMonth] = useState(today.getMonth());

  // Selected day popup state
  const [selectedDay, setSelectedDay] = useState(null);
  const [popupPos, setPopupPos] = useState({ top: 0, left: 0 });
  const [form, setForm] = useState({
    subject_id: '',
    start_time: '',
    end_time: '',
    notes: '',
  });
  const [submitting, setSubmitting] = useState(false);
  const [bookingError, setBookingError] = useState('');
  const popupRef = useRef(null);

  useEffect(() => {
    if (!token) { navigate('/login'); return; }
    const headers = { Authorization: `Bearer ${token}` };

    const fetchData = async () => {
      try {
        const [subjRes, unavailRes] = await Promise.all([
          fetch('http://localhost:5000/api/auth/subjects', { headers }),
          fetch(`http://localhost:5000/api/sessions/unavailable?mentor_id=${mentorId}`, { headers }),
        ]);
        const subjData = subjRes.ok ? await subjRes.json() : [];
        const unavailData = unavailRes.ok ? await unavailRes.json() : [];

        // Filter subjects to only those the mentor teaches
        const mentorSubjectIds = new Set((mentorInfo?.subjects || []).map((s) => s.id));
        const filtered = mentorSubjectIds.size > 0
          ? subjData.filter((s) => mentorSubjectIds.has(s.id))
          : subjData;

        setSubjects(filtered);
        setUnavailableSlots(unavailData);
        if (filtered.length > 0) setForm((f) => ({ ...f, subject_id: filtered[0].id }));
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [token, mentorId, navigate, mentorInfo]);

  // Close popup on outside click
  useEffect(() => {
    const handleClick = (e) => {
      if (popupRef.current && !popupRef.current.contains(e.target)) {
        setSelectedDay(null);
        setBookingError('');
      }
    };
    document.addEventListener('mousedown', handleClick);
    return () => document.removeEventListener('mousedown', handleClick);
  }, []);

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

  const handleDayClick = (day, e) => {
    if (!day) return;
    const rect = e.currentTarget.getBoundingClientRect();
    const containerRect = e.currentTarget.closest('.session-booking__calendar-card').getBoundingClientRect();
    setSelectedDay(day);
    setBookingError('');
    setForm((f) => ({ ...f, start_time: '', end_time: '', notes: '' }));
    setPopupPos({
      top: rect.top - containerRect.top + rect.height / 2,
      left: rect.left - containerRect.left + rect.width / 2,
    });
  };

  // Check if selected time overlaps any unavailable slot
  const isUnavailable = (date, startTime, endTime) => {
    const start = new Date(`${date}T${startTime}`);
    const end = new Date(`${date}T${endTime}`);
    return unavailableSlots.some((slot) => {
      const sStart = new Date(slot.start_datetime);
      const sEnd = new Date(slot.end_datetime);
      return start < sEnd && end > sStart;
    });
  };

  const handleReserve = async () => {
    setBookingError('');
    if (!form.subject_id || !form.start_time || !form.end_time) {
      setBookingError('Please fill in all fields.');
      return;
    }
    if (form.start_time >= form.end_time) {
      setBookingError('End time must be after start time.');
      return;
    }

    // Build ISO datetime strings
    const pad = (n) => String(n).padStart(2, '0');
    const dateStr = `${calYear}-${pad(calMonth + 1)}-${pad(selectedDay)}`;
    const scheduledAt = `${dateStr}T${form.start_time}:00`;
    const endAt = `${dateStr}T${form.end_time}:00`;

    if (isUnavailable(dateStr, `${form.start_time}:00`, `${form.end_time}:00`)) {
      setBookingError('The mentor is unavailable at the selected time.');
      return;
    }

    setSubmitting(true);
    try {
      const res = await fetch('http://localhost:5000/api/sessions/request', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          mentor_id: mentorId,
          subject_id: Number(form.subject_id),
          scheduled_at: scheduledAt,
          end_at: endAt,
          notes: form.notes || undefined,
        }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.message || 'Failed to book session.');
      setSelectedDay(null);
      setSuccessMsg('Session requested! Waiting for mentor confirmation.');
      setTimeout(() => setSuccessMsg(''), 4000);
    } catch (err) {
      setBookingError(err.message);
    } finally {
      setSubmitting(false);
    }
  };

  const getDayOfWeek = (day) => {
    const d = new Date(calYear, calMonth, day);
    return DAY_SHORT[(d.getDay() + 6) % 7];
  };

  const pad = (n) => String(n).padStart(2, '0');

  return (
    <main className="session-booking">
      {/* Background */}
      <div className="session-booking__bg" aria-hidden="true">
        <img src={BG_IMAGE} alt="" className="session-booking__bg-image" />
      </div>

      <div className="session-booking__outer-card">

        {/* Title bar */}
        <header className="session-booking__title-bar">
          <h1 className="session-booking__title">Reserve a session</h1>
          {mentorInfo && (
            <p className="session-booking__mentor-name">
              with {mentorInfo.first_name} {mentorInfo.last_name}
            </p>
          )}
        </header>

        {/* Calendar card */}
        <section className="session-booking__calendar-card">
          {/* Month navigation */}
          <div className="session-booking__cal-header">
            <button className="session-booking__cal-nav" onClick={prevMonth} aria-label="Previous month">‹</button>
            <h2 className="session-booking__cal-title">
              {MONTH_NAMES[calMonth]} {calYear}
            </h2>
            <button className="session-booking__cal-nav" onClick={nextMonth} aria-label="Next month">›</button>
          </div>

          {error && <p className="session-booking__error">{error}</p>}
          {successMsg && <p className="session-booking__success">{successMsg}</p>}

          {/* Calendar grid */}
          <div className="session-booking__cal-grid">
            {/* Day name headers */}
            {DAY_NAMES.map((day) => (
              <div key={day} className="session-booking__cal-day-name">{day}</div>
            ))}

            {/* Day cells */}
            {calDays.map((day, idx) => {
              const isToday =
                day === today.getDate() &&
                calMonth === today.getMonth() &&
                calYear === today.getFullYear();
              const isSelected = day === selectedDay;
              const isPast = day && new Date(calYear, calMonth, day) < new Date(today.getFullYear(), today.getMonth(), today.getDate());

              return (
                <div
                  key={idx}
                  className={[
                    'session-booking__cal-day',
                    !day ? 'session-booking__cal-day--empty' : '',
                    isToday ? 'session-booking__cal-day--today' : '',
                    isSelected ? 'session-booking__cal-day--selected' : '',
                    isPast ? 'session-booking__cal-day--past' : '',
                    day && !isPast ? 'session-booking__cal-day--clickable' : '',
                  ].join(' ')}
                  onClick={(e) => !isPast && handleDayClick(day, e)}
                >
                  {day || ''}
                </div>
              );
            })}
          </div>

          {/* Day popup */}
          {selectedDay && (
            <div
              ref={popupRef}
              className="session-booking__popup"
              style={{ top: popupPos.top, left: popupPos.left }}
            >
              <p className="session-booking__popup-subject-label">Subject</p>
              <select
                className="session-booking__popup-select"
                value={form.subject_id}
                onChange={(e) => setForm({ ...form, subject_id: e.target.value })}
              >
                {loading
                  ? <option>Loading...</option>
                  : subjects.map((s) => (
                    <option key={s.id} value={s.id}>{s.name}</option>
                  ))
                }
              </select>

              <p className="session-booking__popup-date">
                Date: {pad(selectedDay)} {MONTH_NAMES[calMonth].slice(0, 3)} — {getDayOfWeek(selectedDay)}
              </p>

              <div className="session-booking__popup-time-row">
                <span className="session-booking__popup-time-label">Start time:</span>
                <input
                  type="time"
                  className="session-booking__popup-time-input"
                  value={form.start_time}
                  onChange={(e) => setForm({ ...form, start_time: e.target.value })}
                />
              </div>

              <div className="session-booking__popup-time-row">
                <span className="session-booking__popup-time-label">End time:</span>
                <input
                  type="time"
                  className="session-booking__popup-time-input"
                  value={form.end_time}
                  onChange={(e) => setForm({ ...form, end_time: e.target.value })}
                />
              </div>

              <textarea
                className="session-booking__popup-notes"
                placeholder="Notes (optional)"
                value={form.notes}
                onChange={(e) => setForm({ ...form, notes: e.target.value })}
                rows={2}
              />

              {bookingError && (
                <p className="session-booking__popup-error">{bookingError}</p>
              )}

              <button
                className="session-booking__popup-reserve-btn"
                onClick={handleReserve}
                disabled={submitting}
              >
                {submitting ? '...' : 'Reserve'}
              </button>
            </div>
          )}
        </section>

      </div>

      {/* Footer logo */}
      <footer className="session-booking__footer">
        <span className="session-booking__footer-bold">Mentor</span>
        <span className="session-booking__footer-regular">Match</span>
      </footer>
    </main>
  );
};

export default SessionBookingCalendarPage;

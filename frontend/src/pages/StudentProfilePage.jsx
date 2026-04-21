import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import './StudentProfilePage.css';
import Navbar from '../components/Navbar';

const BG_IMAGE = 'https://www.figma.com/api/mcp/asset/78a80476-c4b9-4de1-907e-b1be62e5dcf1';

const DAY_NAMES = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
const MONTH_NAMES = [
  'January', 'February', 'March', 'April', 'May', 'June',
  'July', 'August', 'September', 'October', 'November', 'December',
];

// Returns days array for a given month/year, starting from Monday
const buildCalendarDays = (year, month) => {
  const firstDay = new Date(year, month, 1);
  // JS getDay(): 0=Sun, 1=Mon ... 6=Sat → convert to Mon-first index
  const startOffset = (firstDay.getDay() + 6) % 7;
  const daysInMonth = new Date(year, month + 1, 0).getDate();

  const cells = [];
  for (let i = 0; i < startOffset; i++) cells.push(null);
  for (let d = 1; d <= daysInMonth; d++) cells.push(d);
  // Pad to complete last row
  while (cells.length % 7 !== 0) cells.push(null);
  return cells;
};

const StudentProfilePage = () => {
  const navigate = useNavigate();
  const token = localStorage.getItem('token');

  const [profile, setProfile] = useState(null);
  const [sessions, setSessions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const today = new Date();
  const [calYear, setCalYear] = useState(today.getFullYear());
  const [calMonth, setCalMonth] = useState(today.getMonth());

  useEffect(() => {
    if (!token) { navigate('/login'); return; }

    const headers = { Authorization: `Bearer ${token}` };

    const fetchData = async () => {
      try {
        const [profRes, sessRes] = await Promise.all([
          fetch('/api/auth/profile', { headers }),
          fetch('/api/sessions/student/calendar', { headers }),
        ]);
        if (!profRes.ok) throw new Error('Failed to load profile.');
        const profData = await profRes.json();
        const sessData = sessRes.ok ? await sessRes.json() : [];
        setProfile(profData);
        setSessions(sessData);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [token, navigate]);

  // Set of day numbers that have a confirmed session in the current month/year
  const sessionDays = new Set(
    sessions
      .map((s) => new Date(s.scheduled_at))
      .filter((d) => d.getFullYear() === calYear && d.getMonth() === calMonth)
      .map((d) => d.getDate())
  );

  const calDays = buildCalendarDays(calYear, calMonth);

  const prevMonth = () => {
    if (calMonth === 0) { setCalMonth(11); setCalYear((y) => y - 1); }
    else setCalMonth((m) => m - 1);
  };
  const nextMonth = () => {
    if (calMonth === 11) { setCalMonth(0); setCalYear((y) => y + 1); }
    else setCalMonth((m) => m + 1);
  };

  const handleAddMentorRole = () => {
    navigate('/register/subjects', {
      state: { addingRole: true },
    });
  };

  const isMentor = profile?.role === 'mentor' || profile?.role === 'both';
  const isBoth = profile?.role === 'both';

  if (loading) return (
    <main className="student-profile-page">
      <div className="student-profile-page__bg" aria-hidden="true">
        <img src={BG_IMAGE} alt="" className="student-profile-page__bg-image" />
      </div>
      <p className="student-profile-page__loading">Loading profile...</p>
    </main>
  );

  if (error) return (
    <main className="student-profile-page">
      <div className="student-profile-page__bg" aria-hidden="true">
        <img src={BG_IMAGE} alt="" className="student-profile-page__bg-image" />
      </div>
      <p className="student-profile-page__loading">{error}</p>
    </main>
  );

  return (
    <main className="student-profile-page">
      {/* Background */}
      <div className="student-profile-page__bg" aria-hidden="true">
        <img src={BG_IMAGE} alt="" className="student-profile-page__bg-image" />
      </div>

      <Navbar />

      <div className="student-profile-page__outer-card">

        {/* ── Info card ── */}
        <section className="student-profile-page__info-card">
          <div className="student-profile-page__info-left">
            <h1 className="student-profile-page__name">
              {profile?.first_name} {profile?.last_name}
              {' '}
              <span className="student-profile-page__role-label">
                — {profile?.role?.charAt(0).toUpperCase() + profile?.role?.slice(1)}
              </span>
            </h1>
            <p className="student-profile-page__class">
              Grade {profile?.grade}{profile?.class_letter}
            </p>
            <p className="student-profile-page__email">{profile?.email}</p>
            <p className="student-profile-page__sessions">
              Total sessions:{' '}
              <strong>{profile?.total_sessions ?? 0}</strong>
            </p>
          </div>

          {/* Add role button — only shown if not already both */}
          {!isBoth && (
            <button
              className="student-profile-page__add-role-btn"
              onClick={handleAddMentorRole}
            >
              {isMentor ? 'Add role as Student' : 'Add role as Mentor'}
            </button>
          )}
        </section>

        {/* ── Calendar card ── */}
        <section className="student-profile-page__calendar-card">
          {/* Calendar header */}
          <div className="student-profile-page__cal-header">
            <button
              className="student-profile-page__cal-nav"
              onClick={prevMonth}
              aria-label="Previous month"
            >
              ‹
            </button>
            <h2 className="student-profile-page__cal-title">
              {MONTH_NAMES[calMonth]} {calYear}
            </h2>
            <button
              className="student-profile-page__cal-nav"
              onClick={nextMonth}
              aria-label="Next month"
            >
              ›
            </button>
          </div>

          {/* Day name headers */}
          <div className="student-profile-page__cal-grid">
            {DAY_NAMES.map((day) => (
              <div key={day} className="student-profile-page__cal-day-name">
                {day}
              </div>
            ))}

            {/* Day cells */}
            {calDays.map((day, idx) => {
              const isToday =
                day === today.getDate() &&
                calMonth === today.getMonth() &&
                calYear === today.getFullYear();
              const hasSession = day && sessionDays.has(day);

              return (
                <div
                  key={idx}
                  className={[
                    'student-profile-page__cal-day',
                    day ? '' : 'student-profile-page__cal-day--empty',
                    isToday ? 'student-profile-page__cal-day--today' : '',
                    hasSession ? 'student-profile-page__cal-day--session' : '',
                  ].join(' ')}
                >
                  {day || ''}
                </div>
              );
            })}
          </div>
        </section>

      </div>

      {/* Footer logo */}
      <footer className="student-profile-page__footer">
        <span className="student-profile-page__footer-bold">Mentor</span>
        <span className="student-profile-page__footer-regular">Match</span>
      </footer>
    </main>
  );
};

export default StudentProfilePage;


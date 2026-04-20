import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import './MentorProfilePage.css';

const BG_IMAGE = 'https://www.figma.com/api/mcp/asset/ac149af1-46e1-488c-9826-40e3c006effa';

const DAY_NAMES = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
const MONTH_NAMES = [
  'January', 'February', 'March', 'April', 'May', 'June',
  'July', 'August', 'September', 'October', 'November', 'December',
];

const buildCalendarDays = (year, month) => {
  const firstDay = new Date(year, month, 1);
  const startOffset = (firstDay.getDay() + 6) % 7; // Mon=0
  const daysInMonth = new Date(year, month + 1, 0).getDate();
  const cells = [];
  for (let i = 0; i < startOffset; i++) cells.push(null);
  for (let d = 1; d <= daysInMonth; d++) cells.push(d);
  while (cells.length % 7 !== 0) cells.push(null);
  return cells;
};

const StarRating = ({ rating, max = 5 }) => {
  return (
    <div className="mentor-profile__stars" aria-label={`Rating: ${rating} out of ${max}`}>
      {Array.from({ length: max }, (_, i) => (
        <span
          key={i}
          className={`mentor-profile__star ${i < Math.round(rating) ? 'mentor-profile__star--filled' : 'mentor-profile__star--empty'}`}
        >
          ★
        </span>
      ))}
    </div>
  );
};

const MentorProfilePage = () => {
  const navigate = useNavigate();
  const token = localStorage.getItem('token');

  const [profile, setProfile] = useState(null);
  const [reviews, setReviews] = useState([]);
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
          fetch('http://localhost:5000/api/auth/profile', { headers }),
          fetch('http://localhost:5000/api/sessions/mentor/calendar', { headers }),
        ]);

        if (!profRes.ok) throw new Error('Failed to load profile.');
        const profData = await profRes.json();
        const sessData = sessRes.ok ? await sessRes.json() : [];
        setProfile(profData);
        setSessions(sessData);

        // Fetch reviews if we have a mentor profile id
        if (profData.mentor_profile_id) {
          const revRes = await fetch(
            `http://localhost:5000/api/reviews/mentor/${profData.mentor_profile_id}`,
            { headers }
          );
          if (revRes.ok) {
            const revData = await revRes.json();
            setReviews(revData.reviews || []);
          }
        }
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [token, navigate]);

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

  const isBoth = profile?.role === 'both';
  const averageRating = profile?.average_rating ?? 0;

  if (loading) return (
    <main className="mentor-profile-page">
      <div className="mentor-profile-page__bg" aria-hidden="true">
        <img src={BG_IMAGE} alt="" className="mentor-profile-page__bg-image" />
      </div>
      <p className="mentor-profile-page__loading">Loading profile...</p>
    </main>
  );

  if (error) return (
    <main className="mentor-profile-page">
      <div className="mentor-profile-page__bg" aria-hidden="true">
        <img src={BG_IMAGE} alt="" className="mentor-profile-page__bg-image" />
      </div>
      <p className="mentor-profile-page__loading">{error}</p>
    </main>
  );

  return (
    <main className="mentor-profile-page">
      {/* Background */}
      <div className="mentor-profile-page__bg" aria-hidden="true">
        <img src={BG_IMAGE} alt="" className="mentor-profile-page__bg-image" />
      </div>

      <div className="mentor-profile-page__outer-card">

        {/* ── Info card ── */}
        <section className="mentor-profile-page__info-card">
          <div className="mentor-profile-page__info-left">
            <h1 className="mentor-profile-page__name">
              {profile?.first_name} {profile?.last_name}
              <span className="mentor-profile-page__role-label"> — Mentor</span>
            </h1>
            <p className="mentor-profile-page__class">
              Grade {profile?.grade}{profile?.class_letter}
            </p>
            <p className="mentor-profile-page__email">{profile?.email}</p>

            {/* Subjects */}
            {profile?.subjects?.length > 0 && (
              <p className="mentor-profile-page__subjects">
                {profile.subjects.map((s) => s.name).join(' · ')}
              </p>
            )}

            {/* Sessions + Rating row */}
            <div className="mentor-profile-page__stats-row">
              <p className="mentor-profile-page__sessions">
                Total sessions: <strong>{profile?.total_sessions ?? 0}</strong>
              </p>
              <div className="mentor-profile-page__rating-group">
                <p className="mentor-profile-page__rating-text">
                  Rating: {averageRating.toFixed(1)}/5
                </p>
                <StarRating rating={averageRating} />
              </div>
            </div>
          </div>

          {/* Add role as Student — only if not already both */}
          {!isBoth && (
            <button
              className="mentor-profile-page__add-role-btn"
              onClick={() => navigate('/register/subjects', { state: { addingRole: true, role: 'student' } })}
            >
              Add role as Student
            </button>
          )}
        </section>

        {/* ── Calendar card ── */}
        <section className="mentor-profile-page__calendar-card">
          <div className="mentor-profile-page__cal-header">
            <button
              className="mentor-profile-page__cal-nav"
              onClick={prevMonth}
              aria-label="Previous month"
            >
              ‹
            </button>
            <h2 className="mentor-profile-page__cal-title">
              {MONTH_NAMES[calMonth]} {calYear}
            </h2>
            <button
              className="mentor-profile-page__cal-nav"
              onClick={nextMonth}
              aria-label="Next month"
            >
              ›
            </button>
          </div>

          <div className="mentor-profile-page__cal-grid">
            {DAY_NAMES.map((day) => (
              <div key={day} className="mentor-profile-page__cal-day-name">
                {day}
              </div>
            ))}

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
                    'mentor-profile-page__cal-day',
                    !day ? 'mentor-profile-page__cal-day--empty' : '',
                    isToday ? 'mentor-profile-page__cal-day--today' : '',
                    hasSession ? 'mentor-profile-page__cal-day--session' : '',
                  ].join(' ')}
                >
                  {day || ''}
                </div>
              );
            })}
          </div>
        </section>

        {/* ── Reviews section ── */}
        {reviews.length > 0 && (
          <section className="mentor-profile-page__reviews-card">
            <h3 className="mentor-profile-page__reviews-title">Reviews</h3>
            <div className="mentor-profile-page__reviews-list">
              {reviews.map((review) => (
                <div key={review.id} className="mentor-profile-page__review-item">
                  <div className="mentor-profile-page__review-header">
                    <StarRating rating={review.rating} />
                    <span className="mentor-profile-page__review-date">
                      {new Date(review.created_at).toLocaleDateString()}
                    </span>
                  </div>
                  {review.comment && (
                    <p className="mentor-profile-page__review-comment">{review.comment}</p>
                  )}
                </div>
              ))}
            </div>
          </section>
        )}

      </div>

      {/* Footer logo */}
      <footer className="mentor-profile-page__footer">
        <span className="mentor-profile-page__footer-bold">Mentor</span>
        <span className="mentor-profile-page__footer-regular">Match</span>
      </footer>
    </main>
  );
};

export default MentorProfilePage;

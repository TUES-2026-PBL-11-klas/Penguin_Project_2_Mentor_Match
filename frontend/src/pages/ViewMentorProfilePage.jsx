import React, { useState, useEffect } from 'react';
import { useNavigate, useParams, useLocation } from 'react-router-dom';
import Navbar from '../components/Navbar';
import './MentorProfilePage.css';

const BG_IMAGE = 'https://www.figma.com/api/mcp/asset/ac149af1-46e1-488c-9826-40e3c006effa';

const DAY_NAMES = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
const MONTH_NAMES = [
  'January', 'February', 'March', 'April', 'May', 'June',
  'July', 'August', 'September', 'October', 'November', 'December',
];

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

const StarRating = ({ rating, max = 5 }) => (
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

const ViewMentorProfilePage = () => {
  const navigate = useNavigate();
  const { mentorId } = useParams();
  const location = useLocation();
  const token = sessionStorage.getItem('token');

  const mentor = location.state?.mentor || null;

  const [reviews, setReviews] = useState([]);
  const [unavailableSlots, setUnavailableSlots] = useState([]);
  const [loading, setLoading] = useState(true);

  const today = new Date();
  const [calYear, setCalYear] = useState(today.getFullYear());
  const [calMonth, setCalMonth] = useState(today.getMonth());

  const viewerId = (() => {
    try { return String(JSON.parse(atob(token.split('.')[1])).sub); }
    catch { return null; }
  })();
  const isOwnProfile = viewerId === String(mentorId);

  useEffect(() => {
    if (!token) { navigate('/login'); return; }
    const headers = { Authorization: `Bearer ${token}` };
    Promise.all([
      fetch(`/api/sessions/unavailable?mentor_id=${mentorId}`, { headers }),
      fetch(`/api/reviews/mentor/${mentorId}`, { headers }),
    ]).then(async ([unavailRes, reviewRes]) => {
      setUnavailableSlots(unavailRes.ok ? await unavailRes.json() : []);
      const revData = reviewRes.ok ? await reviewRes.json() : {};
      setReviews(revData.reviews || []);
    }).catch(() => {}).finally(() => setLoading(false));
  }, [mentorId, token, navigate]);

  const unavailDays = new Set(
    unavailableSlots
      .map((s) => new Date(s.start_datetime))
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

  const handleCalendarClick = (day) => {
    if (!day) return;
    if (isOwnProfile) {
      navigate('/availability');
    } else {
      navigate(`/book/${mentorId}`, { state: { mentor } });
    }
  };

  const averageRating = mentor?.average_rating ?? 0;

  if (loading) return (
    <main className="mentor-profile-page">
      <div className="mentor-profile-page__bg" aria-hidden="true">
        <img src={BG_IMAGE} alt="" className="mentor-profile-page__bg-image" />
      </div>
      <p className="mentor-profile-page__loading">Loading...</p>
    </main>
  );

  if (!mentor) return (
    <main className="mentor-profile-page">
      <div className="mentor-profile-page__bg" aria-hidden="true">
        <img src={BG_IMAGE} alt="" className="mentor-profile-page__bg-image" />
      </div>
      <Navbar />
      <p className="mentor-profile-page__loading">
        Mentor not found.{' '}
        <button
          onClick={() => navigate('/search')}
          style={{ background: 'none', border: 'none', color: '#fff', textDecoration: 'underline', cursor: 'pointer', fontSize: 'inherit' }}
        >
          Back to search
        </button>
      </p>
    </main>
  );

  return (
    <main className="mentor-profile-page">
      <div className="mentor-profile-page__bg" aria-hidden="true">
        <img src={BG_IMAGE} alt="" className="mentor-profile-page__bg-image" />
      </div>

      <Navbar />

      <div className="mentor-profile-page__outer-card">

        {/* ── Info card ── */}
        <section className="mentor-profile-page__info-card">
          <div className="mentor-profile-page__info-left">
            <h1 className="mentor-profile-page__name">
              {mentor.first_name} {mentor.last_name}
              <span className="mentor-profile-page__role-label"> — Mentor</span>
            </h1>
            <p className="mentor-profile-page__class">
              Grade {mentor.grade}{mentor.class_letter}
            </p>
            {mentor.subjects?.length > 0 && (
              <p className="mentor-profile-page__subjects">
                {mentor.subjects.map((s) => s.name).join(' · ')}
              </p>
            )}
            <div className="mentor-profile-page__stats-row">
              <p className="mentor-profile-page__sessions">
                Total sessions: <strong>{mentor.total_sessions ?? 0}</strong>
              </p>
              <div
                className="mentor-profile-page__rating-group"
                onClick={() => navigate(`/mentor/${mentorId}/reviews`, {
                  state: { mentorName: `${mentor.first_name} ${mentor.last_name}` },
                })}
                style={{ cursor: 'pointer' }}
                title="View all reviews"
              >
                <p className="mentor-profile-page__rating-text">
                  Rating: {averageRating.toFixed(1)}/5
                </p>
                <StarRating rating={averageRating} />
              </div>
            </div>
          </div>

          {!isOwnProfile && (
            <button
              className="mentor-profile-page__add-role-btn"
              onClick={() => navigate(`/book/${mentorId}`, { state: { mentor } })}
            >
              Book a Session
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

          <p style={{
            textAlign: 'center',
            color: 'rgba(5,6,138,0.6)',
            marginBottom: '12px',
            fontSize: '14px',
            fontFamily: 'DM Sans, sans-serif',
          }}>
            {isOwnProfile
              ? 'Click any date to manage your availability'
              : 'Click any date to request a session'}
          </p>

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
              const isUnavail = day && unavailDays.has(day);

              return (
                <div
                  key={idx}
                  className={[
                    'mentor-profile-page__cal-day',
                    !day ? 'mentor-profile-page__cal-day--empty' : '',
                    isToday && !isUnavail ? 'mentor-profile-page__cal-day--today' : '',
                  ].join(' ')}
                  style={{
                    cursor: day ? 'pointer' : 'default',
                    background: isUnavail ? 'rgba(220,80,80,0.25)' : undefined,
                    color: isUnavail ? '#8b0000' : undefined,
                  }}
                  onClick={() => handleCalendarClick(day)}
                >
                  {day || ''}
                </div>
              );
            })}
          </div>

          <div style={{ display: 'flex', gap: '20px', marginTop: '16px', fontSize: '13px', fontFamily: 'DM Sans, sans-serif' }}>
            <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <span style={{
                width: '14px', height: '14px', borderRadius: '4px',
                background: 'rgba(220,80,80,0.25)', border: '1px solid rgba(220,80,80,0.5)',
                display: 'inline-block',
              }} />
              <span style={{ color: 'rgba(5,6,138,0.6)' }}>Unavailable</span>
            </span>
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

      <footer className="mentor-profile-page__footer">
        <span className="mentor-profile-page__footer-bold">Mentor</span>
        <span className="mentor-profile-page__footer-regular">Match</span>
      </footer>
    </main>
  );
};

export default ViewMentorProfilePage;

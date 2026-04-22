import React, { useState, useEffect } from 'react';
import { useNavigate, useParams, useLocation } from 'react-router-dom';
import './MentorReviewsPage.css';

const BG_IMAGE = 'https://www.figma.com/api/mcp/asset/343e8506-8931-4938-aa8e-6e9e704fe1a3';

const StarRating = ({ rating, max = 5 }) => (
  <div className="mentor-reviews__stars" aria-label={`${rating} out of ${max} stars`}>
    {Array.from({ length: max }, (_, i) => {
      const filled = i < Math.floor(rating);
      const half = !filled && i < rating;
      return (
        <span
          key={i}
          className={[
            'mentor-reviews__star',
            filled ? 'mentor-reviews__star--filled' : '',
            half ? 'mentor-reviews__star--half' : '',
            !filled && !half ? 'mentor-reviews__star--empty' : '',
          ].join(' ')}
        >
          ★
        </span>
      );
    })}
  </div>
);

const MentorReviewsPage = () => {
  const navigate = useNavigate();
  const { mentorId } = useParams();
  const location = useLocation();
  const token = sessionStorage.getItem('token');

  const mentorName = location.state?.mentorName || 'Mentor';

  const [reviews, setReviews] = useState([]);
  const [averageRating, setAverageRating] = useState(0);
  const [eligibleSessions, setEligibleSessions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!token) { navigate('/login'); return; }

    const fetchData = async () => {
      try {
        const headers = { Authorization: `Bearer ${token}` };
        const [reviewsRes, historyRes] = await Promise.all([
          fetch(`/api/reviews/mentor/${mentorId}`, { headers }),
          fetch('/api/sessions/student/history', { headers }),
        ]);
        if (!reviewsRes.ok) throw new Error('Failed to load reviews.');
        const data = await reviewsRes.json();
        setReviews(data.reviews || []);
        setAverageRating(data.average_rating ?? 0);

        if (historyRes.ok) {
          const history = await historyRes.json();
          const eligible = (Array.isArray(history) ? history : []).filter(
            (s) => String(s.mentor_id) === String(mentorId) && s.has_review === false
          );
          setEligibleSessions(eligible);
        }
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [token, mentorId, navigate]);

  const formatDate = (iso) => {
    if (!iso) return '';
    return new Date(iso).toLocaleDateString('en-GB', {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
    });
  };

  return (
    <main className="mentor-reviews-page">
      {/* Background */}
      <div className="mentor-reviews-page__bg" aria-hidden="true">
        <img src={BG_IMAGE} alt="" className="mentor-reviews-page__bg-image" />
      </div>

      <div className="mentor-reviews-page__outer-card">

        {/* ── Title bar ── */}
        <header className="mentor-reviews-page__title-bar">
          <button
            className="mentor-reviews-page__back-btn"
            onClick={() => navigate(-1)}
            aria-label="Go back"
          >
            ‹
          </button>
          <h1 className="mentor-reviews-page__title">
            Reviews for {mentorName}
          </h1>
          {reviews.length > 0 && (
            <span className="mentor-reviews-page__avg-badge">
              Avg {averageRating.toFixed(1)}/5
            </span>
          )}
        </header>

        {/* ── Add Review prompt ── */}
        {eligibleSessions.length > 0 && (
          <div className="mentor-reviews-page__add-review-banner">
            <p className="mentor-reviews-page__add-review-text">
              You have {eligibleSessions.length} completed session{eligibleSessions.length > 1 ? 's' : ''} with this mentor — leave a review!
            </p>
            <button
              className="mentor-reviews-page__add-review-btn"
              onClick={() => navigate(`/review/${eligibleSessions[0].id}`)}
            >
              Add Review
            </button>
          </div>
        )}

        {/* ── Review list ── */}
        <div className="mentor-reviews-page__list">
          {loading && (
            <p className="mentor-reviews-page__status">Loading reviews...</p>
          )}
          {!loading && error && (
            <p className="mentor-reviews-page__status mentor-reviews-page__status--error">{error}</p>
          )}
          {!loading && !error && reviews.length === 0 && (
            <p className="mentor-reviews-page__status">No reviews yet for this mentor.</p>
          )}

          {reviews.map((review, idx) => (
            <article key={review.id} className="mentor-reviews-page__review-card">
              {/* Top row: label + rating */}
              <div className="mentor-reviews-page__review-top">
                <h2 className="mentor-reviews-page__review-label">
                  Review {idx + 1}
                </h2>
                <div className="mentor-reviews-page__review-rating-group">
                  <span className="mentor-reviews-page__rating-text">
                    Rating: {(review.rating ?? 0).toFixed(1)}/5
                  </span>
                  <StarRating rating={review.rating ?? 0} />
                </div>
              </div>

              {/* Comment */}
              {review.comment && (
                <p className="mentor-reviews-page__review-comment">
                  {review.comment}
                </p>
              )}

              {/* Date */}
              {review.created_at && (
                <p className="mentor-reviews-page__review-date">
                  {formatDate(review.created_at)}
                </p>
              )}
            </article>
          ))}
        </div>

      </div>

      {/* Footer logo */}
      <footer className="mentor-reviews-page__footer">
        <span className="mentor-reviews-page__footer-bold">Mentor</span>
        <span className="mentor-reviews-page__footer-regular">Match</span>
      </footer>
    </main>
  );
};

export default MentorReviewsPage;


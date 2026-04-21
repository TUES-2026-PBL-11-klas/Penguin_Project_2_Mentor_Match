import React, { useState, useEffect } from 'react';
import { useNavigate, useParams, useLocation } from 'react-router-dom';
import './LeaveReviewPage.css';

const BG_IMAGE = 'https://www.figma.com/api/mcp/asset/6b3977b4-09ed-4e94-a7bd-d47757bbcc22';

const LeaveReviewPage = () => {
  const navigate = useNavigate();
  const { sessionId } = useParams();
  const location = useLocation();
  const token = localStorage.getItem('token');

  // Session info passed via navigation state
  const sessionInfo = location.state?.session || null;

  const [wantsToReview, setWantsToReview] = useState(null); // null | true | false
  const [rating, setRating] = useState(0);
  const [hoverRating, setHoverRating] = useState(0);
  const [comment, setComment] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [submitted, setSubmitted] = useState(false);

  useEffect(() => {
    if (!token) navigate('/login');
  }, [token, navigate]);

  const formatDate = (iso) => {
    if (!iso) return 'date';
    return new Date(iso).toLocaleDateString('en-GB', {
      day: '2-digit', month: 'short', year: 'numeric',
    });
  };

  const formatTime = (iso) => {
    if (!iso) return 'time';
    return new Date(iso).toLocaleTimeString('en-GB', {
      hour: '2-digit', minute: '2-digit',
    });
  };

  const handleSubmit = async () => {
    if (rating === 0) {
      setError('Please select a star rating.');
      return;
    }
    setError('');
    setSubmitting(true);

    try {
      const res = await fetch(
        `/api/reviews/session/${sessionId}`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({
            rating,
            comment: comment.trim() || undefined,
          }),
        }
      );
      const data = await res.json();
      if (!res.ok) throw new Error(data.message || 'Failed to submit review.');
      setSubmitted(true);
    } catch (err) {
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  };

  if (submitted) {
    return (
      <main className="leave-review-page">
        <div className="leave-review-page__bg" aria-hidden="true">
          <img src={BG_IMAGE} alt="" className="leave-review-page__bg-image" />
        </div>
        <div className="leave-review-page__outer-card">
          <div className="leave-review-page__success">
            <p className="leave-review-page__success-icon">★</p>
            <h2 className="leave-review-page__success-title">Thank you for your review!</h2>
            <p className="leave-review-page__success-sub">Your feedback helps other students choose the right mentor.</p>
            <button
              className="leave-review-page__done-btn"
              onClick={() => navigate('/profile')}
            >
              Back to profile
            </button>
          </div>
        </div>
        <footer className="leave-review-page__footer">
          <span className="leave-review-page__footer-bold">Mentor</span>
          <span className="leave-review-page__footer-regular">Match</span>
        </footer>
      </main>
    );
  }

  return (
    <main className="leave-review-page">
      {/* Background */}
      <div className="leave-review-page__bg" aria-hidden="true">
        <img src={BG_IMAGE} alt="" className="leave-review-page__bg-image" />
      </div>

      <div className="leave-review-page__outer-card">
        <h1 className="leave-review-page__page-title">Leave a review</h1>

        {/* Inner form card */}
        <div className="leave-review-page__form-card">

          {/* Session context sentence */}
          <p className="leave-review-page__context">
            On{' '}
            <strong>"{formatDate(sessionInfo?.scheduled_at)}"</strong>{' '}
            you had a{' '}
            <strong>"{sessionInfo?.subject_name || 'subject'}"</strong>{' '}
            session with{' '}
            <strong>"{sessionInfo?.mentor_name || 'mentor name'}"</strong>{' '}
            at{' '}
            <strong>"{formatTime(sessionInfo?.scheduled_at)}"</strong>
            , would you like to leave them a review?
          </p>

          {/* Yes / No buttons */}
          <div className="leave-review-page__yn-row">
            <button
              type="button"
              className={`leave-review-page__yn-btn ${wantsToReview === true ? 'leave-review-page__yn-btn--active' : ''}`}
              onClick={() => setWantsToReview(true)}
            >
              Yes
            </button>
            <button
              type="button"
              className={`leave-review-page__yn-btn ${wantsToReview === false ? 'leave-review-page__yn-btn--active' : ''}`}
              onClick={() => {
                setWantsToReview(false);
                navigate(-1);
              }}
            >
              No
            </button>
          </div>

          {/* Review form — only shown after clicking Yes */}
          {wantsToReview === true && (
            <div className="leave-review-page__review-form">
              {/* Star rating */}
              <div className="leave-review-page__rate-row">
                <span className="leave-review-page__rate-label">Rate</span>
                <div
                  className="leave-review-page__stars"
                  role="group"
                  aria-label="Rating out of 5"
                >
                  {[1, 2, 3, 4, 5].map((star) => (
                    <button
                      key={star}
                      type="button"
                      className={[
                        'leave-review-page__star-btn',
                        (hoverRating || rating) >= star
                          ? 'leave-review-page__star-btn--filled'
                          : 'leave-review-page__star-btn--empty',
                      ].join(' ')}
                      onClick={() => setRating(star)}
                      onMouseEnter={() => setHoverRating(star)}
                      onMouseLeave={() => setHoverRating(0)}
                      aria-label={`${star} star${star > 1 ? 's' : ''}`}
                    >
                      ★
                    </button>
                  ))}
                </div>
              </div>

              {/* Comment */}
              <div className="leave-review-page__comment-section">
                <p className="leave-review-page__comment-label">Write a review:</p>
                <p className="leave-review-page__comment-optional">(Optional)</p>
                <textarea
                  className="leave-review-page__comment-input"
                  placeholder="Share your experience with this mentor..."
                  value={comment}
                  onChange={(e) => setComment(e.target.value)}
                  rows={5}
                />
              </div>

              {error && <p className="leave-review-page__error">{error}</p>}

              <button
                type="button"
                className="leave-review-page__submit-btn"
                onClick={handleSubmit}
                disabled={submitting}
              >
                {submitting ? 'Submitting...' : 'Submit Review'}
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Footer logo */}
      <footer className="leave-review-page__footer">
        <span className="leave-review-page__footer-bold">Mentor</span>
        <span className="leave-review-page__footer-regular">Match</span>
      </footer>
    </main>
  );
};

export default LeaveReviewPage;


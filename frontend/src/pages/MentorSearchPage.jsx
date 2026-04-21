import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import './MentorSearchPage.css';

const BG_IMAGE = 'https://www.figma.com/api/mcp/asset/641ff419-d131-4507-9089-854d65596d6f';

const StarRating = ({ rating, max = 5 }) => (
  <div className="mentor-search__stars" aria-label={`${rating} out of ${max} stars`}>
    {Array.from({ length: max }, (_, i) => {
      const filled = i < Math.floor(rating);
      const half = !filled && i < rating;
      return (
        <span
          key={i}
          className={[
            'mentor-search__star',
            filled ? 'mentor-search__star--filled' : '',
            half ? 'mentor-search__star--half' : '',
            !filled && !half ? 'mentor-search__star--empty' : '',
          ].join(' ')}
        >
          {half ? '½' : '★'}
        </span>
      );
    })}
  </div>
);

const MentorSearchPage = () => {
  const navigate = useNavigate();
  const token = localStorage.getItem('token');

  const [mentors, setMentors] = useState([]);
  const [subjects, setSubjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const [nameQuery, setNameQuery] = useState('');
  const [subjectId, setSubjectId] = useState('');

  // Fetch subjects once for the dropdown
  useEffect(() => {
    if (!token) { navigate('/login'); return; }
    fetch('/api/auth/subjects', {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then((r) => r.json())
      .then(setSubjects)
      .catch(() => {});
  }, [token, navigate]);

  // Fetch mentors whenever filters change
  const fetchMentors = useCallback(async () => {
    if (!token) return;
    setLoading(true);
    setError('');
    try {
      const params = new URLSearchParams();
      if (nameQuery.trim()) params.set('name', nameQuery.trim());
      if (subjectId) params.set('subject_id', subjectId);

      const res = await fetch(
        `/api/sessions/mentors/search?${params.toString()}`,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      if (!res.ok) throw new Error('Failed to load mentors.');
      const data = await res.json();
      setMentors(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [token, nameQuery, subjectId]);

  useEffect(() => {
    const timer = setTimeout(fetchMentors, 300); // debounce name search
    return () => clearTimeout(timer);
  }, [fetchMentors]);

  const handleMentorClick = (mentor) => {
    navigate(`/mentor/${mentor.id}`, { state: { mentor } });
  };

  return (
    <main className="mentor-search-page">
      {/* Background */}
      <div className="mentor-search-page__bg" aria-hidden="true">
        <img src={BG_IMAGE} alt="" className="mentor-search-page__bg-image" />
      </div>

      <div className="mentor-search-page__outer-card">

        {/* ── Search / filter bar ── */}
        <div className="mentor-search-page__filter-bar">
          {/* Name search */}
          <input
            className="mentor-search-page__name-input"
            type="text"
            placeholder="Search by name..."
            value={nameQuery}
            onChange={(e) => setNameQuery(e.target.value)}
            aria-label="Search mentor by name"
          />

          {/* Subject filter */}
          <div className="mentor-search-page__subject-wrapper">
            <select
              className="mentor-search-page__subject-select"
              value={subjectId}
              onChange={(e) => setSubjectId(e.target.value)}
              aria-label="Filter by subject"
            >
              <option value="">All Subjects</option>
              {subjects.map((s) => (
                <option key={s.id} value={s.id}>{s.name}</option>
              ))}
            </select>
          </div>
        </div>

        {/* ── Results list ── */}
        <div className="mentor-search-page__results">
          {loading && (
            <p className="mentor-search-page__status">Searching...</p>
          )}
          {!loading && error && (
            <p className="mentor-search-page__status mentor-search-page__status--error">{error}</p>
          )}
          {!loading && !error && mentors.length === 0 && (
            <p className="mentor-search-page__status">No mentors found. Try a different search.</p>
          )}

          {mentors.map((mentor) => (
            <button
              key={mentor.id}
              className="mentor-search-page__mentor-card"
              onClick={() => handleMentorClick(mentor)}
              aria-label={`View profile of ${mentor.first_name} ${mentor.last_name}`}
            >
              {/* Left: name + sessions */}
              <div className="mentor-search-page__card-left">
                <h2 className="mentor-search-page__mentor-name">
                  {mentor.first_name} {mentor.last_name}
                </h2>
                <p className="mentor-search-page__mentor-meta">
                  Grade {mentor.grade}{mentor.class_letter}
                </p>
                <p className="mentor-search-page__mentor-sessions">
                  Total sessions: <strong>{mentor.total_sessions ?? 0}</strong>
                </p>
              </div>

              {/* Right: rating + stars */}
              <div className="mentor-search-page__card-right">
                <p className="mentor-search-page__rating-text">
                  Rating: {(mentor.average_rating ?? 0).toFixed(1)}/5
                </p>
                <StarRating rating={mentor.average_rating ?? 0} />
              </div>
            </button>
          ))}
        </div>

      </div>

      {/* Footer logo */}
      <footer className="mentor-search-page__footer">
        <span className="mentor-search-page__footer-bold">Mentor</span>
        <span className="mentor-search-page__footer-regular">Match</span>
      </footer>
    </main>
  );
};

export default MentorSearchPage;


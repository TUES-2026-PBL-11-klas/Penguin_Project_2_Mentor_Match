import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import './MentorSubjectSelectionPage.css';

const BG_IMAGE = 'https://www.figma.com/api/mcp/asset/44785db6-b0d3-4ef0-9309-3ce20c2e4bee';

const MentorSubjectSelectionPage = () => {
  const navigate = useNavigate();
  const location = useLocation();

  // email + password passed from SignUpPage so we can auto-login after
  const { email, password } = location.state || {};

  const [subjects, setSubjects] = useState([]);
  const [selectedIds, setSelectedIds] = useState([]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');

  // Fetch all available subjects from the API
  useEffect(() => {
    const fetchSubjects = async () => {
      try {
        const res = await fetch('/api/auth/subjects');
        const data = await res.json();
        if (!res.ok) throw new Error('Failed to load subjects.');
        setSubjects(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };
    fetchSubjects();
  }, []);

  const toggleSubject = (id) => {
    setSelectedIds((prev) =>
      prev.includes(id) ? prev.filter((s) => s !== id) : [...prev, id]
    );
  };

const handleSubmit = async () => {
    if (selectedIds.length === 0) {
      setError('Please select at least one subject.');
      return;
    }
    setError('');
    setSubmitting(true);

    try {
      // Use existing token if available, otherwise login first
      let token = localStorage.getItem('token');

      if (!token && email && password) {
        const loginRes = await fetch('/api/auth/login', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email, password }),
        });
        const loginData = await loginRes.json();
        if (!loginRes.ok) throw new Error('Login after registration failed.');
        token = loginData.access_token;
        localStorage.setItem('token', token);
      }

      if (!token) throw new Error('Not authenticated.');

      const roleRes = await fetch('/api/auth/add-role', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ role: 'mentor', subject_ids: selectedIds }),
      });

      if (!roleRes.ok) {
        const roleData = await roleRes.json();
        throw new Error(roleData.error || roleData.message || 'Failed to set subjects.');
      }

      navigate('/profile');
    } catch (err) {
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  };

  // Group subjects by category
  const grouped = subjects.reduce((acc, subject) => {
    const cat = subject.category || 'General';
    if (!acc[cat]) acc[cat] = [];
    acc[cat].push(subject);
    return acc;
  }, {});

  return (
    <main className="subject-selection-page">
      {/* Background */}
      <div className="subject-selection-page__bg" aria-hidden="true">
        <img src={BG_IMAGE} alt="" className="subject-selection-page__bg-image" />
      </div>

      {/* Wide frosted glass card */}
      <section className="subject-selection-page__card">
        <h1 className="subject-selection-page__title">Continue Sign Up</h1>
        <p className="subject-selection-page__subtitle">
          Select the subjects you can help with
        </p>

        {loading && (
          <p className="subject-selection-page__status">Loading subjects...</p>
        )}

        {!loading && subjects.length === 0 && !error && (
          <p className="subject-selection-page__status">No subjects available.</p>
        )}

        {/* Subject list — grouped by category */}
        <div className="subject-selection-page__list">
          {Object.entries(grouped).map(([category, items]) => (
            <div key={category} className="subject-selection-page__category">
              {Object.keys(grouped).length > 1 && (
                <p className="subject-selection-page__category-label">{category}</p>
              )}
              {items.map((subject) => {
                const isChecked = selectedIds.includes(subject.id);
                return (
                  <button
                    key={subject.id}
                    type="button"
                    className={`subject-selection-page__row${isChecked ? ' subject-selection-page__row--checked' : ''}`}
                    onClick={() => toggleSubject(subject.id)}
                    aria-pressed={isChecked}
                  >
                    <span className="subject-selection-page__subject-name">
                      {subject.name}
                    </span>
                    <span
                      className={`subject-selection-page__checkbox${isChecked ? ' subject-selection-page__checkbox--checked' : ''}`}
                      aria-hidden="true"
                    >
                      {isChecked && (
                        <svg width="20" height="16" viewBox="0 0 20 16" fill="none">
                          <path
                            d="M2 8L7.5 13.5L18 2"
                            stroke="#4d5cd0"
                            strokeWidth="3"
                            strokeLinecap="round"
                            strokeLinejoin="round"
                          />
                        </svg>
                      )}
                    </span>
                  </button>
                );
              })}
            </div>
          ))}
        </div>

        {error && <p className="subject-selection-page__error">{error}</p>}

        <button
          type="button"
          className="subject-selection-page__submit-btn"
          onClick={handleSubmit}
          disabled={submitting}
        >
          {submitting ? 'Finishing setup...' : 'Finish Sign Up'}
        </button>
      </section>

      {/* Footer logo */}
      <footer className="subject-selection-page__footer">
        <span className="subject-selection-page__footer-bold">Mentor</span>
        <span className="subject-selection-page__footer-regular">Match</span>
      </footer>
    </main>
  );
};

export default MentorSubjectSelectionPage;


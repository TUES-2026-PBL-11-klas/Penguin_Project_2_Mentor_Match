import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './SignUpPage.css';

const BG_IMAGE = 'https://www.figma.com/api/mcp/asset/4dd02d25-3866-4a15-b953-ab7f37b7bf81';
const ARROW_ICON = 'https://www.figma.com/api/mcp/asset/228e00cb-d198-4914-882d-bc1d445f2b8f';

const GRADES = [8, 9, 10, 11, 12];
const CLASSES = ['А', 'Б', 'В', 'Г'];

const SignUpPage = () => {
  const navigate = useNavigate();

  const [form, setForm] = useState({
    first_name: '',
    last_name: '',
    email: '',
    password: '',
    grade: '',
    class_letter: '',
    role: '',
  });

  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleRoleSelect = (role) => {
    setForm({ ...form, role });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (!form.role) {
      setError('Please select Student or Mentor.');
      return;
    }

    setLoading(true);
    try {
      const res = await fetch('/api/auth/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          first_name: form.first_name,
          last_name: form.last_name,
          email: form.email,
          password: form.password,
          grade: Number(form.grade),
          class_letter: form.class_letter,
          role: form.role,
        }),
      });

      const data = await res.json();
      if (!res.ok) throw new Error(data.message || 'Registration failed.');

      // If mentor or both → go to subject selection page
      if (form.role === 'mentor' || form.role === 'both') {
        navigate('/register/subjects', { state: { email: form.email, password: form.password } });
      } else {
        navigate('/login');
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="signup-page">
      {/* Background */}
      <div className="signup-page__bg" aria-hidden="true">
        <img src={BG_IMAGE} alt="" className="signup-page__bg-image" />
      </div>

      {/* Card */}
      <section className="signup-page__card">
        <h1 className="signup-page__title">Sign Up</h1>

        <form className="signup-page__form" onSubmit={handleSubmit} noValidate>
          {/* Name */}
          <input
            className="signup-page__input"
            type="text"
            name="first_name"
            placeholder="Name"
            value={form.first_name}
            onChange={handleChange}
            required
            autoComplete="given-name"
          />

          {/* Second name */}
          <input
            className="signup-page__input"
            type="text"
            name="last_name"
            placeholder="Second name"
            value={form.last_name}
            onChange={handleChange}
            required
            autoComplete="family-name"
          />

          {/* Email */}
          <input
            className="signup-page__input"
            type="email"
            name="email"
            placeholder="Email"
            value={form.email}
            onChange={handleChange}
            required
            autoComplete="email"
          />

          {/* Password */}
          <input
            className="signup-page__input"
            type="password"
            name="password"
            placeholder="Password"
            value={form.password}
            onChange={handleChange}
            required
            autoComplete="new-password"
          />

          {/* Grade + Class row */}
          <div className="signup-page__row">
            {/* Grade dropdown */}
            <div className="signup-page__select-wrapper">
              <select
                className="signup-page__select"
                name="grade"
                value={form.grade}
                onChange={handleChange}
                required
              >
                <option value="" disabled>Grade</option>
                {GRADES.map((g) => (
                  <option key={g} value={g}>{g}</option>
                ))}
              </select>
              <img src={ARROW_ICON} alt="" className="signup-page__select-arrow" aria-hidden="true" />
            </div>

            {/* Class dropdown */}
            <div className="signup-page__select-wrapper">
              <select
                className="signup-page__select"
                name="class_letter"
                value={form.class_letter}
                onChange={handleChange}
                required
              >
                <option value="" disabled>Class</option>
                {CLASSES.map((c) => (
                  <option key={c} value={c}>{c}</option>
                ))}
              </select>
              <img src={ARROW_ICON} alt="" className="signup-page__select-arrow" aria-hidden="true" />
            </div>
          </div>

          {/* Role toggle buttons */}
          <div className="signup-page__role-row">
            <button
              type="button"
              className={`signup-page__role-btn ${form.role === 'student' ? 'signup-page__role-btn--active' : ''}`}
              onClick={() => handleRoleSelect('student')}
            >
              Student
            </button>
            <button
              type="button"
              className={`signup-page__role-btn ${form.role === 'both' ? 'signup-page__role-btn--active' : ''}`}
              onClick={() => handleRoleSelect('both')}
            >
              Both
            </button>
            <button
              type="button"
              className={`signup-page__role-btn ${form.role === 'mentor' ? 'signup-page__role-btn--active' : ''}`}
              onClick={() => handleRoleSelect('mentor')}
            >
              Mentor
            </button>
          </div>

          {error && <p className="signup-page__error">{error}</p>}

          <button
            type="submit"
            className="signup-page__submit-btn"
            disabled={loading}
          >
            {loading ? 'Creating account...' : 'Continue'}
          </button>
        </form>

        <p className="signup-page__login-link">
          Already have an account?{' '}
          <button
            type="button"
            className="signup-page__login-btn"
            onClick={() => navigate('/login')}
          >
            Log In
          </button>
        </p>
      </section>

      {/* Footer logo */}
      <footer className="signup-page__footer">
        <span className="signup-page__footer-bold">Mentor</span>
        <span className="signup-page__footer-regular">Match</span>
      </footer>
    </main>
  );
};

export default SignUpPage;


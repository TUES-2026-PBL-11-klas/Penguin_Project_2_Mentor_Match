import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './LoginPage.css';

const BG_IMAGE = 'https://www.figma.com/api/mcp/asset/fcb18d42-8920-489e-9b71-6580709bedcb';

const LoginPage = () => {
  const navigate = useNavigate();

  const [form, setForm] = useState({ email: '', password: '' });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const res = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: form.email, password: form.password }),
      });

      const data = await res.json();
      if (!res.ok) throw new Error(data.message || 'Login failed.');

      sessionStorage.setItem('token', data.access_token);
      navigate('/');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="login-page">
      {/* Background */}
      <div className="login-page__bg" aria-hidden="true">
        <img src={BG_IMAGE} alt="" className="login-page__bg-image" />
      </div>

      {/* Frosted glass card */}
      <section className="login-page__card">
        <h1 className="login-page__title">Log In</h1>

        <form className="login-page__form" onSubmit={handleSubmit} noValidate>
          <input
            className="login-page__input"
            type="email"
            name="email"
            placeholder="Email"
            value={form.email}
            onChange={handleChange}
            required
            autoComplete="email"
          />

          <input
            className="login-page__input"
            type="password"
            name="password"
            placeholder="Password"
            value={form.password}
            onChange={handleChange}
            required
            autoComplete="current-password"
          />

          {error && <p className="login-page__error">{error}</p>}

          <button
            type="submit"
            className="login-page__submit-btn"
            disabled={loading}
          >
            {loading ? 'Logging in...' : 'Log In'}
          </button>
        </form>

        <p className="login-page__signup-link">
          Don't have an account?{' '}
          <button
            type="button"
            className="login-page__signup-btn"
            onClick={() => navigate('/register')}
          >
            Sign Up
          </button>
        </p>
      </section>

      {/* Footer logo */}
      <footer className="login-page__footer">
        <span className="login-page__footer-bold">Mentor</span>
        <span className="login-page__footer-regular">Match</span>
      </footer>
    </main>
  );
};

export default LoginPage;


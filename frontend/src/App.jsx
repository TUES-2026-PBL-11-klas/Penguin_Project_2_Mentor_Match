import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';

// ─── Pages (one per Figma frame) ─────────────────────────────────────────────
import HomePage                    from './pages/HomePage';               // Figma 1:2
import LoginPage                   from './pages/LoginPage';              // Figma 6:32
import SignUpPage                  from './pages/SignUpPage';             // Figma 2:20
import MentorSubjectSelectionPage  from './pages/MentorSubjectSelectionPage'; // Figma 4:14
import StudentProfilePage          from './pages/StudentProfilePage';     // Figma 6:67
import MentorProfilePage           from './pages/MentorProfilePage';     // Figma 9:210
import MentorSearchPage            from './pages/MentorSearchPage';      // Figma 11:450
import MentorReviewsPage           from './pages/MentorReviewsPage';     // Figma 11:564
import SessionBookingCalendarPage  from './pages/SessionBookingCalendarPage';  // Figma 9:281
import BothRoleBookingCalendarPage from './pages/BothRoleBookingCalendarPage'; // Figma 11:375
import LeaveReviewPage             from './pages/LeaveReviewPage';       // Figma 11:523
import AvailabilityPage            from './pages/AvailabilityPage';
import ViewMentorProfilePage       from './pages/ViewMentorProfilePage';
import SessionsPage                from './pages/SessionsPage';

// ─── Helpers ─────────────────────────────────────────────────────────────────

/** Decode the JWT payload and return it, or null if missing/invalid. */
const getJwtPayload = () => {
  const token = sessionStorage.getItem('token');
  if (!token) return null;
  try {
    return JSON.parse(atob(token.split('.')[1]));
  } catch {
    return null;
  }
};

/** Return the user's role ('student' | 'mentor' | 'both') or null. */
const getUserRole = () => {
  const payload = getJwtPayload();
  if (!payload) return null;
  return payload.role || payload.sub?.role || null;
};

// ─── Route guards ─────────────────────────────────────────────────────────────

/**
 * PrivateRoute
 * Blocks unauthenticated users and sends them to /login.
 * The browser back button works normally — navigate() builds history as usual.
 */
const PrivateRoute = ({ children }) => {
  const token = sessionStorage.getItem('token');
  return token ? children : <Navigate to="/login" replace />;
};

/**
 * GuestRoute
 * Blocks already-logged-in users from reaching /login and /register,
 * bouncing them straight to /profile instead.
 */
const GuestRoute = ({ children }) => {
  const token = sessionStorage.getItem('token');
  return token ? <Navigate to="/profile" replace /> : children;
};

// ─── Smart routers ────────────────────────────────────────────────────────────

/**
 * ProfileRouter  →  Figma 6:67 (Student) | Figma 9:210 (Mentor)
 *
 * /profile always shows the right dashboard for the logged-in user:
 *   role === 'mentor'          → MentorProfilePage   (Figma 9:210)
 *   role === 'student' | 'both'→ StudentProfilePage  (Figma 6:67)
 */
const ProfileRouter = () => {
  const role = getUserRole();
  if (role === 'mentor' || role === 'both') return <MentorProfilePage />;
  return <StudentProfilePage />;
};

/**
 * BookingRouter  →  Figma 9:281 (student) | Figma 11:375 (both)
 *
 * /book/:mentorId picks the right calendar:
 *   role === 'both'    → BothRoleBookingCalendarPage  (Figma 11:375)
 *   role === 'student' → SessionBookingCalendarPage   (Figma 9:281)
 */
const BookingRouter = () => {
  const role = getUserRole();
  if (role === 'both') return <BothRoleBookingCalendarPage />;
  return <SessionBookingCalendarPage />;
};

// ─── App ─────────────────────────────────────────────────────────────────────
function App() {
  return (
    <BrowserRouter>
      <Routes>
        
        <Route path="/availability" element={<PrivateRoute><AvailabilityPage /></PrivateRoute>} />
        <Route path="/sessions" element={<PrivateRoute><SessionsPage /></PrivateRoute>} />
        {/* ════════════════════════════════════════════════════════════════════
            PUBLIC ROUTES — no login required
            ════════════════════════════════════════════════════════════════ */}

        {/* Figma 1:2 — Homepage
            The landing page everyone sees first.
            Shows Log In / Sign Up buttons.                                  */}
        <Route path="/" element={<HomePage />} />

        {/* Figma 6:32 — Log In
            If already logged in, skip to /profile.                         */}
        <Route
          path="/login"
          element={
            <GuestRoute>
              <LoginPage />
            </GuestRoute>
          }
        />

        {/* Figma 2:20 — Sign Up
            If already logged in, skip to /profile.                         */}
        <Route
          path="/register"
          element={
            <GuestRoute>
              <SignUpPage />
            </GuestRoute>
          }
        />

        {/* ════════════════════════════════════════════════════════════════════
            REGISTRATION STEP 2 — requires being logged in
            ════════════════════════════════════════════════════════════════ */}

        {/* Figma 4:14 — Sign Up Mentor (subject picker)
            Reached after choosing mentor/both role in SignUpPage.
            Also used when an existing student adds the mentor role.
            SignUpPage navigates here with:
              navigate('/register/subjects', { state: { email, password } }) */}
        <Route
          path="/register/subjects"
          element={
            <PrivateRoute>
              <MentorSubjectSelectionPage />
            </PrivateRoute>
          }
        />

        {/* ════════════════════════════════════════════════════════════════════
            PROFILE — role-aware, requires login
            ════════════════════════════════════════════════════════════════ */}

        {/* Figma 6:67 + 9:210 — Profile dashboard
            ProfileRouter automatically sends:
              mentor → MentorProfilePage
              student / both → StudentProfilePage                            */}
        <Route
          path="/profile"
          element={
            <PrivateRoute>
              <ProfileRouter />
            </PrivateRoute>
          }
        />

        {/* Explicit student profile — used when a mentor clicks "Add role as
            Student" and you want to show the student view directly.         */}
        <Route
          path="/profile/student"
          element={
            <PrivateRoute>
              <StudentProfilePage />
            </PrivateRoute>
          }
        />

        {/* Explicit mentor profile — used when a student clicks "Add role as
            Mentor" and you want to show the mentor view directly.           */}
        <Route
          path="/profile/mentor"
          element={
            <PrivateRoute>
              <MentorProfilePage />
            </PrivateRoute>
          }
        />

        {/* ════════════════════════════════════════════════════════════════════
            MENTOR SEARCH & REVIEWS — students only (guard keeps it clean)
            ════════════════════════════════════════════════════════════════ */}

        {/* Figma 11:450 — Search for mentor
            Name + subject filter, list of mentor cards.
            Each card navigates to /book/:mentorId                          */}
        <Route
          path="/search"
          element={
            <PrivateRoute>
              <MentorSearchPage />
            </PrivateRoute>
          }
        />

        {/* Public mentor profile — accessible by students from search results.
            Navigate here with:
              navigate(`/mentor/${mentor.id}`, { state: { mentor } })        */}
        <Route
          path="/mentor/:mentorId"
          element={
            <PrivateRoute>
              <ViewMentorProfilePage />
            </PrivateRoute>
          }
        />

        {/* Figma 11:564 — Reviews for a specific mentor
            Navigate here with:
              navigate(`/mentor/${id}/reviews`, {
                state: { mentorName: 'First Last' }
              })                                                              */}
        <Route
          path="/mentor/:mentorId/reviews"
          element={
            <PrivateRoute>
              <MentorReviewsPage />
            </PrivateRoute>
          }
        />

        {/* ════════════════════════════════════════════════════════════════════
            SESSION BOOKING — role-aware calendar
            ════════════════════════════════════════════════════════════════ */}

        {/* Figma 9:281 (student) / Figma 11:375 (both)
            BookingRouter picks the right calendar based on role.
            Navigate here with:
              navigate(`/book/${mentor.id}`, { state: { mentor } })         */}
        <Route
          path="/book/:mentorId"
          element={
            <PrivateRoute>
              <BookingRouter />
            </PrivateRoute>
          }
        />

        {/* ════════════════════════════════════════════════════════════════════
            LEAVE A REVIEW
            ════════════════════════════════════════════════════════════════ */}

        {/* Figma 11:523 — Leave a review
            Triggered from a notification or session history after a
            completed session. Navigate here with:
              navigate(`/review/${session.id}`, {
                state: {
                  session: {
                    scheduled_at: '...',
                    subject_name: '...',
                    mentor_name: '...',
                  }
                }
              })                                                              */}
        <Route
          path="/review/:sessionId"
          element={
            <PrivateRoute>
              <LeaveReviewPage />
            </PrivateRoute>
          }
        />

        {/* ════════════════════════════════════════════════════════════════════
            CATCH-ALL — unknown paths go back to homepage
            ════════════════════════════════════════════════════════════════ */}
        <Route path="*" element={<Navigate to="/" replace />} />

      </Routes>
    </BrowserRouter>
  );
}

export default App;

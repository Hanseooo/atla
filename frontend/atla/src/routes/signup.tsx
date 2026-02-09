import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { useState } from "react";
import { useAuthStore } from "../stores/authStore";
import { requireGuest } from "../lib/auth-guards";

export const Route = createFileRoute("/signup")({
  component: SignupPage,
  beforeLoad: requireGuest,
});

function SignupPage() {
  const navigate = useNavigate();
  const signUp = useAuthStore((state) => state.signUp);
  const isLoading = useAuthStore((state) => state.isLoading);

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [username, setUsername] = useState("");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    try {
      await signUp(email, password, username);
      setSuccess(true);
      // After successful signup, redirect to home
      // Note: If email confirmation is required, user will be redirected to login
      setTimeout(() => {
        navigate({ to: "/" });
      }, 2000);
    } catch (err) {
      // added better error handling to display actual error message from supabase
      setError(err instanceof Error ? err.message : "Failed to sign up");
    }
  };

  if (success) {
    return (
      <div>
        <h1>Success!</h1>
        <p>Your account has been created. Redirecting...</p>
      </div>
    );
  }

  return (
    // <div className="w-full h-screen flex flex-col justify-center items-center">
    <div>
    <h1 className="text-2xl font-bold mb-4 text-center">Sign Up</h1>
      {error && <div style={{ color: "red" }}>{error}</div>}

      <form className="flex flex-col gap-4 w-80" onSubmit={handleSubmit}>
        <div className="flex flex-col">
          <label>Username</label>
          <input
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
            className="border p-2 rounded"
          />
        </div>
        <div className="flex flex-col">
          <label>Email</label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            className="border p-2 rounded"
          />
        </div>
        <div className="flex flex-col">
          <label>Password</label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            minLength={6}
            className="border p-2 rounded"
          />
        </div>
        <button className="text-white" type="submit" disabled={isLoading}>
          {isLoading ? "Creating account..." : "Sign Up"}
        </button>
      </form>
      <div className="mt-4 text-center">
        Already have an account? <a href="/login">Sign in</a>
      </div>
    </div>
  );
}

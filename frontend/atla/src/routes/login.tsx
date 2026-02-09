import {
  createFileRoute,
  useNavigate,
  useSearch,
} from "@tanstack/react-router";
import { useState } from "react";
import { useAuthStore } from "../stores/authStore";
import { requireGuest } from "../lib/auth-guards";

export const Route = createFileRoute("/login")({
  component: LoginPage,
  beforeLoad: requireGuest,
});

function LoginPage() {
  const navigate = useNavigate();
  const search = useSearch({ from: "/login" });
  const signIn = useAuthStore((state) => state.signIn);
  const isLoading = useAuthStore((state) => state.isLoading);

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    try {
      await signIn(email, password);
      // Redirect to original page or home
      const redirectTo = (search as any).redirect || "/";
      navigate({ to: redirectTo });
    } catch (err) {
      // added better error handling to display actual error message from supabase
      setError(err instanceof Error ? err.message : "Failed to sign in");
    }
  };
  return (
    // <div className="w-full h-screen flex flex-col justify-center items-center">
      <div>
      <h1 className="text-2xl font-bold mb-4 text-center">Login</h1>
      {error && <div style={{ color: "red" }}>{error}</div>}
      <form onSubmit={handleSubmit} className="flex flex-col gap-4 w-80">
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
            className="border p-2 rounded"
          />
        </div>
        <button
          className="bg-blue-500 text-white py-2 rounded disabled:opacity-50"
          type="submit"
          disabled={isLoading}
        >
          {isLoading ? "Signing in..." : "Sign In"}
        </button>
      </form>
      <div className="mt-4 text-center">
        Don't have an account? <a href="/signup">Sign up</a>
      </div>
    </div>
  );
}

import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { requireAuth } from "../lib/auth-guards";
import { useAuthStore } from "@/stores/authStore";

export const Route = createFileRoute("/")({
  component: HomePage,
  beforeLoad: requireAuth,
});

function HomePage() {
  const navigate = useNavigate()
  const signOut = useAuthStore((state) => state.signOut)
  // const isLoading = useAuthStore((state) => state.isLoading)

  return (
    <div>
      <div>Home Page - Trip Dashboard</div>
      <div>Welcome! Your trips will appear here.</div>
      <button 
      onClick={() => {
        signOut()
        navigate({ to: '/login' })
      }}
      className="text-white">Signout</button>
    </div>
  );
}

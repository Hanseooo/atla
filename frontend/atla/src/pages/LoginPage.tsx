import { useState } from "react";
import { Link } from "@tanstack/react-router";
import { useAuthStore } from "../stores/authStore";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Label } from "../components/ui/label";
import { Card, CardContent, CardHeader } from "../components/ui/card";
import { Alert, AlertDescription } from "../components/ui/alert";
import { Loader2, Compass, ArrowRight, ShieldCheck, Zap } from "lucide-react";

interface LoginPageProps {
  redirectTo?: string;
  onLogin?: () => void;
}

export function LoginPage({ onLogin }: LoginPageProps) {
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
      onLogin?.();
    } catch (err: unknown) {
      const error = err as Error;
      const errorMessage = error.message || "Failed to sign in";
      if (errorMessage.includes("Invalid login credentials")) {
        setError("Invalid email or password. Please try again.");
      } else if (errorMessage.includes("Email not confirmed")) {
        setError("Please confirm your email address before signing in.");
      } else {
        setError(errorMessage);
      }
    }
  };

  return (
    <div className="min-h-screen grid lg:grid-cols-2 bg-zinc-50 text-black">
      {/* Left Side - Hero/Branding */}
      <div className="hidden lg:flex flex-col justify-between p-12 bg-zinc-950 relative overflow-hidden">
        <div className="absolute inset-0 bg-[url('https://images.unsplash.com/photo-1518509562904-e7ef99cdcc86?q=80&w=2000&auto=format&fit=crop')] bg-cover bg-center mix-blend-overlay opacity-10 grayscale" />

        <Link
          to="/"
          className="flex items-center gap-2 relative z-10 text-white"
        >
          <div className="bg-emerald-600 p-2 rounded-xl border border-emerald-500/20 shadow-xl shadow-emerald-900/20">
            <Compass className="w-8 h-8" />
          </div>
          <span className="text-3xl font-black tracking-tighter text-white uppercase">
            Atla
          </span>
        </Link>

        <div className="relative z-10 space-y-8">
          <div className="space-y-4">
            <h1 className="text-5xl font-bold text-white leading-tight">
              Unlock the secrets of the <br />
              <span className="text-white/60 italic">7,641 islands.</span>
            </h1>
            <p className="text-xl text-zinc-400 max-w-lg leading-relaxed">
              Your personalized AI travel companion for discovering the hidden
              gems of the Philippines.
            </p>
          </div>

          <div className="grid grid-cols-2 gap-6 pt-8 border-t border-white/10">
            <div className="flex items-start gap-3">
              <div className="mt-1 bg-emerald-500/10 p-1.5 rounded-lg border border-emerald-500/20">
                <ShieldCheck className="w-5 h-5 text-emerald-400" />
              </div>
              <div>
                <h4 className="font-bold text-white uppercase tracking-wider text-xs">
                  Secure Planning
                </h4>
                <p className="text-[10px] text-zinc-500 uppercase tracking-widest font-black">
                  Your itineraries, synced and protected.
                </p>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <div className="mt-1 bg-emerald-500/10 p-1.5 rounded-lg border border-emerald-500/20">
                <Zap className="w-5 h-5 text-emerald-400" />
              </div>
              <div>
                <h4 className="font-bold text-white uppercase tracking-wider text-xs">
                  Instant Results
                </h4>
                <p className="text-[10px] text-zinc-500 uppercase tracking-widest font-black">
                  AI-generated routes in seconds.
                </p>
              </div>
            </div>
          </div>
        </div>

        <div className="relative z-10 text-sm text-zinc-600 font-medium tracking-wide">
          © 2026 Atla Philippines • Discover the magic
        </div>
      </div>

      {/* Right Side - Login Form */}
      <div className="flex items-center justify-center p-6 md:p-8 lg:p-12 overflow-y-auto">
        <div className="w-full max-w-md space-y-8">
          <div className="lg:hidden flex justify-center mb-8">
            <Link to="/" className="flex items-center gap-2">
              <div className="bg-emerald-600 p-2 rounded-xl shadow-lg">
                <Compass className="w-7 h-7 text-white" />
              </div>
              <span className="text-2xl font-black tracking-tighter text-black uppercase">
                Atla
              </span>
            </Link>
          </div>

          <div className="space-y-2 text-center lg:text-left">
            <h2 className="text-3xl font-black tracking-tighter text-black uppercase">
              Sign In
            </h2>
            <p className="text-zinc-500 font-medium">
              Enter your credentials to access <br/> your dream trips in Philippines.
            </p>
          </div>

          <Card className="border gap-0 pb-8 border-zinc-200 shadow-2xl shadow-emerald-100/20 bg-white overflow-hidden transition-all duration-300">
            <CardHeader className="space-y-1 pb-4">
              {error && (
                <Alert
                  variant="destructive"
                  className="animate-in fade-in slide-in-from-top-2 duration-300 rounded-xl"
                >
                  <AlertDescription>{error}</AlertDescription>
                </Alert>
              )}
            </CardHeader>

            <CardContent className="space-y-6">
              <form onSubmit={handleSubmit} className="space-y-5">
                <div className="space-y-2">
                  <Label
                    htmlFor="email"
                    className="text-[10px] font-black text-zinc-700 ml-1 uppercase tracking-widest"
                  >
                    Email Address
                  </Label>
                  <Input
                    id="email"
                    type="email"
                    placeholder="name@example.com"
                    className="h-12 border-zinc-200 focus:border-emerald-500 focus:ring-emerald-500/5 transition-all rounded-md px-4 text-base bg-zinc-50/50"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                  />
                </div>

                <div className="space-y-2">
                  <div className="flex items-center justify-between ml-1">
                    <Label
                      htmlFor="password"
                      className="text-[10px] font-black text-zinc-700 uppercase tracking-widest"
                    >
                      Password
                    </Label>
                    <Link
                      to="/login"
                      className="relative text-xs font-bold text-emerald-600 
                      after:absolute after:left-0 after:-bottom-0.5 after:h-[2px] after:w-0 after:bg-emerald-600 
                      after:transition-all after:duration-500 after:ease-in-out
                      hover:after:w-full"
                    >
                      Forgot Password?
                    </Link>
                  </div>
                  <Input
                    id="password"
                    type="password"
                    placeholder="••••••••"
                    className="h-12 border-zinc-200 focus:border-emerald-500 focus:ring-emerald-500/5 transition-all rounded-md px-4 text-base bg-zinc-50/50"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                  />
                </div>

                <Button
                  type="submit"
                  className="w-full h-12 text-base font-black bg-emerald-600 text-white hover:bg-emerald-700 transition-all rounded-md group shadow-xl shadow-emerald-100 uppercase tracking-widest"
                  disabled={isLoading}
                >
                  {isLoading ? (
                    <>
                      <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                      Authenticating...
                    </>
                  ) : (
                    <span className="flex items-center gap-2">
                      Unlock{" "}
                      <ArrowRight className="w-4 h-4 group-hover:translate-x-0.5 transition-transform" />
                    </span>
                  )}
                </Button>
              </form>

              <div className="relative">
                <div className="absolute inset-0 flex items-center">
                  <span className="w-full border-t border-zinc-100" />
                </div>
                <div className="relative flex justify-center text-[10px] uppercase tracking-widest font-black">
                  <span className="bg-white px-3 text-zinc-400">or</span>
                </div>
              </div>

              <div className="flex flex-col items-center space-y-2 text-sm text-zinc-500 font-medium">
                <p>Don't have an account yet?</p>
                <Link
                  to="/signup"
                  className="relative text-emerald-600 font-bold flex items-center gap-1
                  after:absolute after:left-0 after:-bottom-0.5 after:h-[2px] after:w-0 after:bg-emerald-600 
                  after:transition-all after:duration-500 after:ease-in-out
                  hover:after:w-full uppercase text-xs tracking-widest"
                >
                  Create free account
                </Link>
              </div>
            </CardContent>
          </Card>

          <p className="text-center text-[10px] font-bold uppercase tracking-widest text-zinc-400 px-6 leading-relaxed">
            By logging in, you agree to our{" "}
            <Link
              to="/"
              className=" text-zinc-950 hover:text-emerald-600 transition-colors"
            >
              Terms of Service
            </Link>{" "}
            and{" "}
            <Link
              to="/"
              className=" text-zinc-950 hover:text-emerald-600 transition-colors"
            >
              Privacy Policy
            </Link>
            .
          </p>
        </div>
      </div>
    </div>
  );
}

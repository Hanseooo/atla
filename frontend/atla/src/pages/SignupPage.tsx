import { useState, useEffect } from "react";
import { Link } from "@tanstack/react-router";
import { useAuthStore } from "../stores/authStore";
import { useUsernameCheck } from "../hooks/useUsernameCheck";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Label } from "../components/ui/label";
import { Card, CardContent } from "../components/ui/card";
import { Alert, AlertDescription } from "../components/ui/alert";
import {
  Loader2,
  CheckCircle2,
  AlertCircle,
  RefreshCw,
  Compass,
  ArrowRight,
  Palmtree,
  Map,
  Eye,
  EyeOff,
} from "lucide-react";

interface SignupPageProps {
  onSignup?: () => void;
}

export function SignupPage({ onSignup }: SignupPageProps) {
  const signUp = useAuthStore((state) => state.signUp);
  const retryProfileCreation = useAuthStore(
    (state) => state.retryProfileCreation
  );
  const clearProfileError = useAuthStore((state) => state.clearProfileError);
  const isLoading = useAuthStore((state) => state.isLoading);
  const profileCreationError = useAuthStore(
    (state) => state.profileCreationError
  );
  const {
    isAvailable,
    isChecking,
    error: usernameError,
    checkUsername,
  } = useUsernameCheck(500);

  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState(false);
  const [isRetrying, setIsRetrying] = useState(false);

  // Check username availability when username changes
  useEffect(() => {
    checkUsername(username);
  }, [username, checkUsername]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    clearProfileError();

    // Validate username
    if (username.length < 3) {
      setError("Username must be at least 3 characters");
      return;
    }

    if (isAvailable === false) {
      setError(usernameError || "Username is not available");
      return;
    }

    // Validate password match
    if (password !== confirmPassword) {
      setError("Passwords do not match");
      return;
    }

    // Validate password length
    if (password.length < 6) {
      setError("Password must be at least 6 characters");
      return;
    }

    try {
      await signUp(email, password, username);
      setSuccess(true);
      setTimeout(() => {
        onSignup?.();
      }, 2000);
    } catch (err: any) {
      setError(err.message || "Failed to sign up");
    }
  };

  const handleRetry = async () => {
    setIsRetrying(true);
    setError("");
    clearProfileError();

    try {
      await retryProfileCreation();
      setSuccess(true);
      setTimeout(() => {
        onSignup?.();
      }, 2000);
    } catch (err: any) {
      setError(err.message || "Failed to retry profile creation");
    } finally {
      setIsRetrying(false);
    }
  };

  // Show profile creation error with retry option
  if (profileCreationError?.canRetry) {
    return (
      <div className="min-h-screen grid lg:grid-cols-2 bg-zinc-50">
        <div className="hidden lg:flex flex-col justify-between p-12 bg-zinc-950 relative overflow-hidden">
          <div className="absolute inset-0 bg-[url('https://images.unsplash.com/photo-1528127269322-539801943592?q=80&w=2000&auto=format&fit=crop')] bg-cover bg-center mix-blend-overlay opacity-10 grayscale" />
          <Link
            to="/"
            className="flex items-center gap-2 relative z-10 text-white"
          >
            <div className="bg-white/10 backdrop-blur-md p-2 rounded-xl border border-white/20">
              <Compass className="w-8 h-8" />
            </div>
            <span className="text-3xl font-bold tracking-tight">Atla</span>
          </Link>
          <div className="relative z-10 text-sm text-zinc-600 font-medium">
            © 2026 Atla Philippines
          </div>
        </div>
        <div className="flex items-center justify-center p-6">
          <div className="w-full max-w-md space-y-8 text-center">
            <h1 className="text-3xl font-bold text-black">Almost Done!</h1>
            <Card className="border border-zinc-200 shadow-xl shadow-zinc-200/50 bg-white rounded-2xl p-6 transition-all duration-300">
              <div className="space-y-6">
                <Alert className="border-zinc-200 bg-zinc-50 text-black">
                  <AlertCircle className="h-4 w-4 text-black" />
                  <AlertDescription className="text-zinc-700 font-medium">
                    {profileCreationError.message}
                  </AlertDescription>
                </Alert>
                <Button
                  onClick={handleRetry}
                  className="w-full h-12 rounded-xl bg-black text-white hover:bg-zinc-800"
                  disabled={isRetrying}
                >
                  {isRetrying ? (
                    <Loader2 className="animate-spin" />
                  ) : (
                    <RefreshCw className="mr-2" />
                  )}{" "}
                  Retry Setup
                </Button>
              </div>
            </Card>
          </div>
        </div>
      </div>
    );
  }

  if (success) {
    return (
      <div className="min-h-screen grid lg:grid-cols-2 bg-zinc-50">
        <div className="hidden lg:flex flex-col justify-between p-12 bg-zinc-950 relative overflow-hidden">
          <div className="absolute inset-0 bg-[url('https://images.unsplash.com/photo-1528127269322-539801943592?q=80&w=2000&auto=format&fit=crop')] bg-cover bg-center mix-blend-overlay opacity-10 grayscale" />
          <Link
            to="/"
            className="flex items-center gap-2 relative z-10 text-white"
          >
            <div className="bg-emerald-600 p-2 rounded-xl border border-emerald-500/20 shadow-xl shadow-emerald-900/20">
              <Compass className="w-8 h-8" />
            </div>
            <span className="text-3xl font-black tracking-tighter uppercase">
              Atla
            </span>
          </Link>
          <div className="relative z-10 text-[10px] text-zinc-600 font-black uppercase tracking-[0.3em]">
            © 2026 Atla Philippines
          </div>
        </div>
        <div className="flex items-center justify-center p-6 text-center">
          <div className="w-full max-w-md space-y-6">
            <div className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-emerald-50 text-emerald-600 animate-in zoom-in duration-500 shadow-2xl shadow-emerald-100">
              <CheckCircle2 className="w-10 h-10" />
            </div>
            <h2 className="text-3xl font-black tracking-tighter text-black uppercase">
              Welcome Aboard!
            </h2>
            <p className="text-zinc-500 font-medium uppercase text-[10px] tracking-widest">
              Preparing your dashboard...
            </p>
            <Loader2 className="w-6 h-6 animate-spin mx-auto text-emerald-600" />
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen grid lg:grid-cols-2 bg-zinc-50">
      {/* Left Side - Hero/Branding */}
      <div className="hidden lg:flex flex-col justify-between p-12 bg-zinc-950 relative overflow-hidden">
        <div className="absolute inset-0 bg-[url('https://images.unsplash.com/photo-1528127269322-539801943592?q=80&w=2000&auto=format&fit=crop')] bg-cover bg-center mix-blend-overlay opacity-10 grayscale" />
        <Link
          to="/"
          className="flex items-center gap-2 relative z-10 text-white"
        >
          <div className="bg-emerald-600 p-2 rounded-xl border border-emerald-500/20 shadow-xl shadow-emerald-900/20">
            <Compass className="w-8 h-8 text-white" />
          </div>
          <span className="text-3xl font-black tracking-tighter text-white uppercase">
            Atla
          </span>
        </Link>

        <div className="relative z-10 space-y-8">
          <div className="space-y-4">
            <h1 className="text-5xl font-black text-white leading-tight uppercase tracking-tighter">
              Start your journey <br />
              <span className="text-emerald-500 italic">
                across the archipelago.
              </span>
            </h1>
            <p className="text-xl text-zinc-400 max-w-lg leading-relaxed font-medium">
              Join thousands of travelers planning their perfect Philippine
              getaway with AI-powered itineraries.
            </p>
          </div>

          <div className="grid grid-cols-2 gap-6 pt-8 border-t border-white/10">
            <div className="flex items-start gap-3">
              <div className="mt-1 bg-emerald-500/10 p-1.5 rounded-lg border border-emerald-500/20">
                <Map className="w-5 h-5 text-emerald-400" />
              </div>
              <div>
                <h4 className="font-bold text-white uppercase text-xs tracking-widest">
                  Custom Maps
                </h4>
                <p className="text-[10px] text-zinc-500 font-black uppercase tracking-widest leading-relaxed">
                  Visualize your entire trip on one map.
                </p>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <div className="mt-1 bg-emerald-500/10 p-1.5 rounded-lg border border-emerald-500/20">
                <Palmtree className="w-5 h-5 text-emerald-400" />
              </div>
              <div>
                <h4 className="font-bold text-white uppercase text-xs tracking-widest">
                  Island Guides
                </h4>
                <p className="text-[10px] text-zinc-500 font-black uppercase tracking-widest leading-relaxed">
                  Expert tips for every destination.
                </p>
              </div>
            </div>
          </div>
        </div>

        <div className="relative z-10 text-[10px] text-zinc-600 font-black uppercase tracking-[0.3em]">
          © 2026 Atla Philippines • Adventure awaits
        </div>
      </div>

      {/* Right Side - Signup Form */}
      <div className="flex items-center justify-center p-6 md:p-12 lg:p-16">
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
              Get Started
            </h2>
            <p className="text-zinc-500 font-medium">
              Start planning your Philippine adventures today
            </p>
          </div>

          <Card className="border border-zinc-200 shadow-2xl shadow-emerald-100/20 overflow-hidden transition-all duration-300 bg-white">
            <CardContent className="pt-6 space-y-6">
              {error && (
                <Alert
                  variant="destructive"
                  className="animate-in fade-in slide-in-from-top-2 duration-300 rounded-xl"
                >
                  <AlertDescription>{error}</AlertDescription>
                </Alert>
              )}

              <form onSubmit={handleSubmit} className="space-y-4">
                <div className="space-y-1.5">
                  <Label
                    htmlFor="username"
                    className="text-[10px] font-black text-zinc-700 ml-1 uppercase tracking-widest"
                  >
                    Username
                  </Label>
                  <div className="relative">
                    <Input
                      id="username"
                      type="text"
                      placeholder="juan_dela_cruz"
                      className={`h-12 border-zinc-200 focus:border-emerald-500 focus:ring-emerald-500/5 transition-all rounded-md px-4 pr-10 bg-zinc-50/50 ${
                        isAvailable === true
                          ? "border-emerald-200"
                          : isAvailable === false
                            ? "border-red-200 bg-red-50/10"
                            : ""
                      }`}
                      value={username}
                      onChange={(e) => setUsername(e.target.value)}
                      required
                    />
                    <div className="absolute right-3 top-1/2 -translate-y-1/2">
                      {isChecking && (
                        <Loader2 className="w-4 h-4 animate-spin text-zinc-400" />
                      )}
                      {isAvailable === true && !isChecking && (
                        <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                      )}
                      {isAvailable === false && !isChecking && (
                        <AlertCircle className="w-4 h-4 text-red-500" />
                      )}
                    </div>
                  </div>
                  <p className="text-[10px] text-zinc-400 font-bold uppercase tracking-wider pl-1">
                    3–50 chars • letters, numbers, underscores
                  </p>
                </div>

                <div className="space-y-1.5">
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
                    className="h-12 border-zinc-200 focus:border-emerald-500 focus:ring-emerald-500/5 transition-all rounded-md px-4 bg-zinc-50/50"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                  />
                </div>

                <div className="space-y-2">
                  <Label
                    htmlFor="password"
                    className="text-[10px] font-black text-zinc-700 ml-1 uppercase tracking-widest"
                  >
                    Password
                  </Label>
                  <div className="relative">
                    <Input
                      id="password"
                      type={showPassword ? "text" : "password"}
                      placeholder="••••••••"
                      className="h-12 border-zinc-200 focus:border-emerald-500 focus:ring-emerald-500/5 transition-all rounded-md px-4 pr-10 bg-zinc-50/50"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      required
                    />
                    <div
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute right-4 top-1/2 -translate-y-1/2 text-zinc-400 hover:text-emerald-600 transition-colors bg-transparent border-none p-0 flex items-center justify-center cursor-pointer"
                    >
                      {showPassword ? (
                        <EyeOff className="w-4 h-4" />
                      ) : (
                        <Eye className="w-4 h-4" />
                      )}
                    </div>
                  </div>
                </div>
                <div className="space-y-1.5">
                  <Label
                    htmlFor="confirmPassword"
                    className="text-[10px] font-black text-zinc-700 ml-1 uppercase tracking-widest"
                  >
                    Confirm Password
                  </Label>
                  <div className="relative">
                    <Input
                      id="confirmPassword"
                      type={showConfirmPassword ? "text" : "password"}
                      placeholder="••••••••"
                      className="h-12 border-zinc-200 focus:border-emerald-500 focus:ring-emerald-500/5 transition-all rounded-md px-4 pr-10 bg-zinc-50/50"
                      value={confirmPassword}
                      onChange={(e) => setConfirmPassword(e.target.value)}
                      required
                    />
                    <div
                      onClick={() =>
                        setShowConfirmPassword(!showConfirmPassword)
                      }
                      className="absolute right-4 top-1/2 -translate-y-1/2 text-zinc-400 hover:text-emerald-600 transition-colors bg-none border-none p-0 flex items-center justify-center cursor-pointer"
                    >
                      {showConfirmPassword ? (
                        <EyeOff className="w-4 h-4 " />
                      ) : (
                        <Eye className="w-4 h-4" />
                      )}
                    </div>
                  </div>
                </div>

                <Button
                  type="submit"
                  className="w-full h-12 text-base font-black bg-emerald-600 text-white hover:bg-emerald-700 transition-all group mt-2 shadow-xl shadow-emerald-100 uppercase tracking-widest"
                  disabled={isLoading || isChecking || isAvailable === false}
                >
                  {isLoading ? (
                    <>
                      <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                      Creating Account...
                    </>
                  ) : (
                    <span className="flex items-center gap-2">
                      Start Planning{" "}
                      <ArrowRight className="w-4 h-4 group-hover:translate-x-0.5  transition-transform" />
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

              <div className="flex flex-col items-center space-y-2 md:justify-center text-sm text-zinc-500 font-medium">
                <p>Already have an account?</p>
                <Link
                  to="/login"
                  className="relative text-emerald-600 font-bold flex items-center gap-1
                            after:absolute after:left-0 after:-bottom-0.5 after:h-[2px] after:w-0 after:bg-emerald-600 
                            after:transition-all after:duration-500 after:ease-in-out
                            hover:after:w-full uppercase text-xs tracking-widest"
                >
                  Sign in here
                </Link>
              </div>
            </CardContent>
          </Card>

          <p className="text-center text-[10px] font-bold uppercase tracking-widest text-zinc-400 px-6 leading-relaxed">
            By signing up, you agree to our{" "}
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

import { Link } from "@tanstack/react-router";
import { Button } from "../components/ui/button";
import {
  Compass,
  ArrowRight,
  Sparkles,
  Globe,
  Shield,
  CheckCircle2,
  Menu,
  X,
  Navigation,
} from "lucide-react";
import { useState, useEffect } from "react";

// mock data for destinations
// will be replaced with API data in the future, 
// but this allows us to build the UI and interactions first
const DESTINATIONS = [
  {
    id: "el-nido",
    name: "El Nido",
    province: "Palawan",
    image:
      "https://images.unsplash.com/photo-1518509562904-e7ef99cdcc86?q=80&w=2000&auto=format&fit=crop",
    tag: "Island Hopping",
    progress: "4 of 6 spots visited",
  },
  {
    id: "siargao",
    name: "Siargao",
    province: "Surigao del Norte",
    image:
      "https://images.unsplash.com/photo-1537996194471-e657df975ab4?q=80&w=2000&auto=format&fit=crop",
    tag: "Surfing Capital",
    progress: "2 of 5 spots visited",
  },
  {
    id: "boracay",
    name: "Boracay",
    province: "Aklan",
    image:
      "https://images.unsplash.com/photo-1583212292454-1fe6229603b7?q=80&w=2000&auto=format&fit=crop",
    tag: "White Beach",
    progress: "1 of 4 spots visited",
  },
  {
    id: "batanes",
    name: "Batanes",
    province: "Basco",
    image:
      "https://images.unsplash.com/photo-1516690561799-46d8f74f9abf?q=80&w=2000&auto=format&fit=crop",
    tag: "Rolling Hills",
    progress: "5 of 8 spots visited",
  },
];

export default function LandingPage() {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [activeDest, setActiveDest] = useState(0);

  // Auto-rotate destinations
  useEffect(() => {
    const timer = setInterval(() => {
      setActiveDest((prev) => (prev + 1) % DESTINATIONS.length);
    }, 6000);
    return () => clearInterval(timer);
  }, []);

  return (
    <div className="min-h-screen bg-white text-zinc-950 selection:bg-emerald-600 selection:text-white overflow-x-hidden">
      {/* Navigation */}
      <nav className="fixed top-0 inset-x-0 z-50 bg-white/90 backdrop-blur-xl border-b border-zinc-100">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-3 items-center h-16 md:h-20">
            {/* Logo */}
            <div className="flex items-center gap-2">
              <div className="bg-emerald-600 p-1.5 rounded-lg text-white group-hover:rotate-12 transition-transform duration-300">
                <Compass className="w-5 h-5" />
              </div>
              <span className="text-xl font-black tracking-tighter uppercase whitespace-nowrap">
                Atla
              </span>
            </div>

            {/* Desktop Nav */}
            <div className="hidden md:flex justify-center gap-8 lg:gap-12">
              <a
                href="#features"
                className="text-[10px] font-black uppercase tracking-[0.2em] hover:text-emerald-600 transition-colors"
              >
                Features
              </a>
              <a
                href="#destinations"
                className="text-[10px] font-black uppercase tracking-[0.2em] hover:text-emerald-600 transition-colors"
              >
                Destinations
              </a>
              <Link
                to="/login"
                className="text-[10px] font-black uppercase tracking-[0.2em] hover:text-emerald-600 transition-colors"
              >
                Login
              </Link>
            </div>

            {/* Desktop CTA */}
            <div className="hidden md:flex justify-end">
              <Link to="/signup">
                <Button
                  size="sm"
                  className="bg-emerald-600 text-white hover:bg-emerald-700 rounded-full px-6 font-black uppercase tracking-[0.15em] text-[9px] h-10 shadow-lg shadow-emerald-100 transition-all active:scale-95"
                >
                  Get Started
                </Button>
              </Link>
            </div>

            {/* Mobile Button */}
            <div className="md:hidden col-span-2 flex justify-end">
              <button
                onClick={() => setIsMenuOpen(!isMenuOpen)}
                className="p-2 text-zinc-950 hover:bg-zinc-50 rounded-xl transition-colors"
              >
                {isMenuOpen ? (
                  <X className="w-6 h-6" />
                ) : (
                  <Menu className="w-6 h-6 text-emerald-600" />
                )}
              </button>
            </div>
          </div>
        </div>
      </nav>

      {isMenuOpen && (
        <div className="fixed top-16 inset-x-0 z-40 bg-white border-b border-zinc-100 md:hidden h-screen">
          <div className="px-6 py-8 space-y-6 animate-in slide-in-from-top duration-300">
            <a
              href="#features"
              onClick={() => setIsMenuOpen(false)}
              className="block text-3xl font-black tracking-tighter uppercase border-b border-zinc-100 pb-4 hover:text-emerald-600 transition-colors"
            >
              Features
            </a>
            <a
              href="#destinations"
              onClick={() => setIsMenuOpen(false)}
              className="block text-3xl font-black tracking-tighter uppercase border-b border-zinc-100 pb-4 hover:text-emerald-600 transition-colors"
            >
              Destinations
            </a>
            <Link
              to="/login"
              onClick={() => setIsMenuOpen(false)}
              className="block text-3xl font-black tracking-tighter uppercase border-b border-zinc-100 pb-4 hover:text-emerald-600 transition-colors"
            >
              Login
            </Link>
            <Link
              to="/signup"
              onClick={() => setIsMenuOpen(false)}
              className="block pt-4"
            >
              <Button className="w-full bg-emerald-600 text-white font-black uppercase tracking-widest text-sm h-16 rounded-2xl shadow-2xl shadow-emerald-100">
                Get Started
              </Button>
            </Link>
          </div>
        </div>
      )}

      {/* Hero Section */}
      <main>
        <section className="relative pt-32 pb-20 md:pt-48 md:pb-32">
          <div className="overflow-hidden">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10 text-center">
              <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full border border-emerald-100 bg-emerald-50/50 text-emerald-700 text-[10px] font-black uppercase tracking-[0.2em] mb-8 animate-in fade-in slide-in-from-bottom-3 duration-500">
                <Sparkles className="w-3 h-3 text-emerald-600" />
                <span>AI-Powered Travel Intelligence</span>
              </div>

              <h2 className="text-4xl md:text-5xl lg:text-7xl xl:text-9xl font-black tracking-tighter text-zinc-950 mb-8 md:mb-10 leading-[0.85] animate-in fade-in slide-in-from-bottom-4 duration-700 uppercase">
                EXPLORE THE <br className="hidden md:block" />
                <span className="text-transparent bg-clip-text bg-gradient-to-r from-zinc-950 via-emerald-600 to-emerald-400">
                  ARCHIPELAGO.
                </span>
              </h2>

              <p className="max-w-2xl mx-auto text-base md:text-xl text-zinc-500 mb-12 animate-in fade-in slide-in-from-bottom-5 duration-1000 leading-relaxed font-medium px-4">
                Personalized itineraries for the 7,641 islands of the
                Philippines. Our AI understands your vibe and plans the perfect
                escape.
              </p>

              <div className="flex flex-col sm:flex-row items-center justify-center gap-4 animate-in fade-in slide-in-from-bottom-6 duration-1000 px-4">
                <Link to="/signup" className="w-full sm:w-auto">
                  <Button
                    size="lg"
                    className="h-14 px-8 md:px-10 text-base font-black bg-emerald-600 text-white hover:bg-emerald-700 rounded-full group shadow-2xl shadow-emerald-100 transition-all uppercase tracking-widest w-full"
                  >
                    Start Planning{" "}
                    <ArrowRight className="ml-2 w-4 h-4 group-hover:translate-x-1 transition-transform" />
                  </Button>
                </Link>
                <Link to="/explore" className="w-full sm:w-auto">
                  <Button
                    variant="outline"
                    size="lg"
                    className="h-14 px-8 md:px-10 text-base font-black border-zinc-200 text-zinc-950 rounded-full hover:bg-emerald-50 hover:border-emerald-200 transition-all uppercase tracking-widest w-full"
                  >
                    Browse Spots
                  </Button>
                </Link>
              </div>

              {/* Destination Showcase Carousel */}
              <div className="mt-20 md:mt-32 relative animate-in zoom-in duration-1000 overflow-hidden px-4 sm:px-0">
                <div className="aspect-[4/3] md:aspect-[21/9] bg-zinc-100 rounded-[1.5rem] md:rounded-[3rem] overflow-hidden border border-zinc-200 shadow-[0_32px_64px_-16px_rgba(0,0,0,0.1)] relative group">
                  {/* Images Layer */}
                  <div className="absolute inset-0 z-0">
                    {DESTINATIONS.map((dest, index) => (
                      <div
                        key={dest.id}
                        className={`absolute inset-0 transition-all duration-1000 ease-in-out transform ${index === activeDest ? "opacity-100 scale-100" : "opacity-0 scale-105"}`}
                      >
                        <img
                          src={dest.image}
                          alt={dest.name}
                          className="w-full h-full object-cover grayscale opacity-60 contrast-125"
                        />
                      </div>
                    ))}
                  </div>

                  {/* Visual Overlays */}
                  <div className="absolute inset-0 bg-gradient-to-t from-white via-transparent to-transparent z-10" />
                  <div className="absolute inset-0 bg-gradient-to-r from-white/20 via-transparent to-white/20 z-10" />

                  {/* Floating Navigation Card */}
                  <div className="absolute bottom-4 left-4 right-4 md:bottom-12 md:left-12 p-4 md:p-8 bg-white/95 backdrop-blur-2xl rounded-[1.5rem] md:rounded-[2rem] border border-emerald-100 shadow-2xl text-left z-20 transition-all duration-500 hover:translate-y-[-4px] mx-auto max-w-xs md:max-w-sm">
                    <div className="flex items-center gap-4 mb-6">
                      <div className="w-10 h-10 md:w-12 md:h-12 rounded-2xl bg-emerald-600 flex items-center justify-center shadow-xl shadow-emerald-200 rotate-[-4deg]">
                        <Navigation className="w-5 h-5 md:w-6 md:h-6 text-white fill-current" />
                      </div>
                      <div>
                        <p className="text-[9px] md:text-[10px] font-black uppercase tracking-[0.2em] md:tracking-[0.25em] text-emerald-600 leading-none mb-1.5">
                          Intelligent Route
                        </p>
                        <h4 className="text-lg md:text-xl font-black text-zinc-950 tracking-tighter">
                          {DESTINATIONS[activeDest].name}
                        </h4>
                      </div>
                    </div>

                    <div className="space-y-4">
                      <div className="flex items-center justify-between text-[9px] md:text-[10px] font-black uppercase tracking-[0.15em] text-zinc-500">
                        <span>{DESTINATIONS[activeDest].tag}</span>
                        <span className="text-emerald-600">Active Now</span>
                      </div>
                      <div className="h-2 w-full bg-emerald-50 rounded-full overflow-hidden p-[2px] border border-emerald-100">
                        <div className="h-full w-4/5 bg-emerald-500 rounded-full transition-all duration-1000" />
                      </div>
                      <div className="flex items-center gap-2 text-[9px] md:text-[10px] text-zinc-400 font-bold uppercase tracking-wider">
                        <CheckCircle2 className="w-3 h-3 text-emerald-600" />
                        <span>{DESTINATIONS[activeDest].progress}</span>
                      </div>
                    </div>
                  </div>

                  {/* Desktop Thumbnails */}
                  <div className="absolute top-1/2 -translate-y-1/2 right-4 md:right-12 flex flex-col gap-4 md:gap-6 z-20 hidden lg:flex">
                    {DESTINATIONS.map((dest, index) => (
                      <button
                        key={dest.id + "-thumb"}
                        onClick={() => setActiveDest(index)}
                        className={`group flex items-center gap-3 md:gap-4 transition-all duration-300 ${index === activeDest ? "translate-x-0" : "translate-x-6 md:translate-x-8 opacity-40 hover:opacity-100"}`}
                      >
                        <span
                          className={`text-[9px] md:text-[10px] font-black uppercase tracking-widest transition-all ${index === activeDest ? "text-emerald-600" : "text-zinc-400"}`}
                        >
                          0{index + 1}
                        </span>
                        <div
                          className={`w-12 h-12 md:w-16 md:h-16 rounded-xl md:rounded-2xl overflow-hidden border-2 transition-all ${index === activeDest ? "border-emerald-600 scale-110 shadow-xl shadow-emerald-100" : "border-transparent"}`}
                        >
                          <img
                            src={dest.image}
                            alt={dest.name}
                            className="w-full h-full object-cover grayscale"
                          />
                        </div>
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Features Section */}
        <section
          id="features"
          className="py-20 md:py-32 bg-zinc-50 border-y border-zinc-100"
        >
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="grid md:grid-cols-3 gap-12 md:gap-16">
              <div className="space-y-6">
                <div className="w-12 h-12 md:w-14 md:h-14 rounded-2xl bg-emerald-600 flex items-center justify-center mb-6 md:mb-8 shadow-2xl shadow-emerald-100">
                  <Sparkles className="w-6 h-6 md:w-7 md:h-7 text-white" />
                </div>
                <h3 className="text-xl md:text-2xl font-black tracking-tighter uppercase">
                  AI Itineraries
                </h3>
                <p className="text-zinc-500 leading-relaxed font-medium text-sm md:text-base">
                  Forget generic guides. Our AI builds routes based on your
                  interests, pace, and the best local travel windows across the
                  archipelago.
                </p>
              </div>

              <div className="space-y-6">
                <div className="w-12 h-12 md:w-14 md:h-14 rounded-2xl bg-emerald-600 flex items-center justify-center mb-6 md:mb-8 shadow-2xl shadow-emerald-100">
                  <Globe className="w-6 h-6 md:w-7 md:h-7 text-white" />
                </div>
                <h3 className="text-xl md:text-2xl font-black tracking-tighter uppercase">
                  Island Logistics
                </h3>
                <p className="text-zinc-500 leading-relaxed font-medium text-sm md:text-base">
                  We handle the complexity of ferry schedules, tricycle routes,
                  and local flights so you can focus on the view of the islands.
                </p>
              </div>

              <div className="space-y-6">
                <div className="w-12 h-12 md:w-14 md:h-14 rounded-2xl bg-emerald-600 flex items-center justify-center mb-6 md:mb-8 shadow-2xl shadow-emerald-100">
                  <Shield className="w-6 h-6 md:w-7 md:h-7 text-white" />
                </div>
                <h3 className="text-xl md:text-2xl font-black tracking-tighter uppercase">
                  Local Verified
                </h3>
                <p className="text-zinc-500 leading-relaxed font-medium text-sm md:text-base">
                  Every recommendation is cross-referenced with local community
                  data to ensure safety and authenticity in your Philippine
                  trip.
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* Curated Spots Gallery */}
        <section id="destinations" className="py-20 md:py-32">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex flex-col md:flex-row justify-between items-start md:items-end gap-8 mb-12 md:mb-20">
              <div className="max-w-xl">
                <h2 className="text-3xl md:text-5xl lg:text-6xl font-black tracking-tighter text-zinc-950 mb-4 md:mb-6 leading-none">
                  CURATED SPOTS.
                </h2>
                <p className="text-emerald-600 font-black uppercase tracking-[0.2em] text-[10px] leading-relaxed">
                  Intelligence-engine picks for your next trip.
                </p>
              </div>
              <Link to="/explore">
                <Button
                  variant="outline"
                  className="rounded-full font-black uppercase tracking-[0.2em] text-[10px] h-10 md:h-12 px-6 md:px-8 border-zinc-200 hover:text-emerald-600 hover:border-emerald-200 transition-all mt-4 md:mt-0"
                >
                  View all 150+ spots
                </Button>
              </Link>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 md:gap-6">
              {DESTINATIONS.map((dest) => (
                <div
                  key={dest.id + "-card"}
                  className="group relative aspect-[4/5] rounded-[1.5rem] md:rounded-[2rem] overflow-hidden cursor-pointer bg-zinc-100 border border-zinc-200 transition-all duration-500 hover:shadow-2xl hover:translate-y-[-8px] hover:border-emerald-100"
                >
                  <img
                    src={dest.image}
                    alt={dest.name}
                    className="w-full h-full object-cover grayscale transition-all duration-700 group-hover:grayscale-0 group-hover:scale-110"
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-zinc-950/90 via-zinc-950/20 to-transparent opacity-60 group-hover:opacity-100 transition-opacity duration-500" />
                  <div className="absolute bottom-6 md:bottom-8 left-6 md:left-8 text-white">
                    <p className="text-[10px] font-black uppercase tracking-[0.25em] text-emerald-400 mb-2">
                      {dest.province}
                    </p>
                    <h5 className="font-black text-lg md:text-2xl tracking-tighter uppercase">
                      {dest.name}
                    </h5>
                  </div>
                  <div className="absolute top-6 right-6 opacity-0 group-hover:opacity-100 transition-opacity duration-500">
                    <div className="bg-white/10 backdrop-blur-md p-2 rounded-xl border border-white/20 group-hover:bg-emerald-600 group-hover:border-emerald-400 transition-all">
                      <ArrowRight className="w-5 h-5 text-white" />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Final CTA */}
        <section className="py-20 md:py-56 bg-zinc-950 text-white relative overflow-hidden">
          <div className="absolute inset-0 bg-[url('https://images.unsplash.com/photo-1516690561799-46d8f74f9abf?q=80&w=2000&auto=format&fit=crop')] bg-cover bg-center mix-blend-overlay opacity-10 grayscale" />
          <div className="max-w-4xl mx-auto px-4 text-center relative z-10">
            <h2 className="text-3xl md:text-5xl lg:text-8xl font-black tracking-tighter mb-8 md:mb-10 leading-[0.85] uppercase">
              PLAN YOUR NEXT <br className="hidden md:block" />
              <span className="text-emerald-500 italic">ADVENTURE.</span>
            </h2>
            <p className="text-zinc-500 text-base md:text-lg lg:text-xl mb-8 md:mb-12 max-w-xl mx-auto font-medium">
              Join 10,000+ travelers exploring the Philippines with Atla. Sign
              up today and get your first AI itinerary for free.
            </p>
            <Link to="/signup" className="w-full sm:w-auto">
              <Button
                size="lg"
                className="h-14 md:h-20 px-8 md:px-12 text-base md:text-lg font-black bg-emerald-600 text-white rounded-full hover:bg-emerald-500 transition-all shadow-2xl shadow-emerald-900/20 uppercase tracking-widest w-full"
              >
                Create Free Account
              </Button>
            </Link>
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="bg-zinc-950 text-zinc-600 py-12 md:py-24 border-t border-zinc-900">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid md:grid-cols-4 gap-12 md:gap-16 mb-12 md:mb-24">
            <div className="space-y-6 md:space-y-8 col-span-2">
              <div className="flex items-center gap-2 text-white">
                <div className="bg-emerald-600 p-1.5 rounded-lg shrink-0">
                  <Compass className="w-5 h-5 text-white" />
                </div>
                <span className="text-xl md:text-2xl font-bold tracking-tight uppercase whitespace-nowrap">
                  Atla
                </span>
              </div>
              <p className="max-w-sm text-sm font-medium leading-relaxed">
                The intelligent way to explore the 7,641 islands of the
                Philippines. Smarter planning, deeper discovery for your
                Philippine travel.
              </p>
            </div>

            <div>
              <h4 className="font-black uppercase tracking-[0.25em] text-[10px] text-white mb-6 md:mb-8">
                Product
              </h4>
              <ul className="space-y-4 md:space-y-5 text-[10px] font-black uppercase tracking-[0.15em]">
                <li>
                  <Link
                    to="/explore"
                    className="hover:text-emerald-500 transition-colors"
                  >
                    Destinations
                  </Link>
                </li>
                <li>
                  <Link
                    to="/signup"
                    className="hover:text-emerald-500 transition-colors"
                  >
                    AI Planner
                  </Link>
                </li>
                <li>
                  <Link
                    to="/login"
                    className="hover:text-emerald-500 transition-colors"
                  >
                    Dashboard
                  </Link>
                </li>
              </ul>
            </div>

            <div>
              <h4 className="font-black uppercase tracking-[0.25em] text-[10px] text-white mb-6 md:mb-8">
                Legal
              </h4>
              <ul className="space-y-4 md:space-y-5 text-[10px] font-black uppercase tracking-[0.15em]">
                <li>
                  <Link
                    to="/"
                    className="hover:text-emerald-500 transition-colors"
                  >
                    Privacy Policy
                  </Link>
                </li>
                <li>
                  <Link
                    to="/"
                    className="hover:text-emerald-500 transition-colors"
                  >
                    Terms of Service
                  </Link>
                </li>
                <li>
                  <Link
                    to="/"
                    className="hover:text-emerald-500 transition-colors"
                  >
                    Cookie Policy
                  </Link>
                </li>
              </ul>
            </div>
          </div>

          <div className="pt-8 md:pt-12 border-t border-zinc-900 flex flex-col-reverse items-center md:flex-row justify-between gap-6 text-[10px] font-black uppercase tracking-[0.3em] text-zinc-800">
            <p className="text-center text-zinc-600">
              © 2026 ATLA PHILIPPINES. ALL RIGHTS RESERVED.
            </p>
            <div className="flex gap-6 md:gap-10">
              <a
                href="#"
                className="text-zinc-600 hover:text-emerald-500 transition-colors"
              >
                TWITTER
              </a>
              <a
                href="#"
                className="text-zinc-600 hover:text-emerald-500 transition-colors"
              >
                INSTAGRAM
              </a>
              <a
                href="#"
                className="text-zinc-600 hover:text-emerald-500 transition-colors"
              >
                FACEBOOK
              </a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}

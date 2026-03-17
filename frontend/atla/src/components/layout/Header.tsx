import { Link, useRouterState } from "@tanstack/react-router";
import { Compass, MessageSquarePlus, Map, User } from "lucide-react";

export function Header() {
  const routerState = useRouterState();
  const currentPath = routerState.location.pathname;

  const navItems = [
    { name: "Plan", path: "/chat", icon: MessageSquarePlus },
    { name: "My Trips", path: "/trips", icon: Map },
    { name: "Explore", path: "/explore", icon: Compass },
  ];

  return (
    <header className="sticky top-0 z-40 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="max-w-4xl md:mx-auto border-b flex h-16 items-center md:justify-between justify-center">
        <Link to="/home" className="flex items-center space-x-2">
          <div className="flex items-center gap-2">
            <div className="bg-emerald-600 p-1.5 rounded-lg text-white group-hover:rotate-12 transition-transform duration-300">
              <Compass className="w-5 h-5" />
            </div>
            <span className="text-xl font-black tracking-tighter uppercase whitespace-nowrap">
              Atla
            </span>
          </div>
        </Link>

        {/* Desktop Navigation */}
        <nav className="hidden md:flex items-center gap-6 ml-4">
          {navItems.map((item) => {
            const isActive =
              currentPath === item.path ||
              (item.path !== "/" && currentPath.startsWith(item.path));

            return (
              <Link
                key={item.name}
                to={item.path}
                className={`text-[10px] uppercase font-black tracking-[0.2em] ${
                  isActive && "text-emerald-600"
                }`}
              >
                {item.name}
              </Link>
            );
          })}
          <div className="hidden sm:flex">
            <div className="h-8 w-8 rounded-full bg-primary/10 flex items-center justify-center text-primary">
              <Link to="/profile">
                <User className="h-4 w-4" />
              </Link>
            </div>
          </div>
        </nav>
      </div>
    </header>
  );
}

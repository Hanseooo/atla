import { Link, useRouterState } from '@tanstack/react-router';
import { MessageSquarePlus, Map, MapPin, User } from 'lucide-react';
import { useScrollDirection } from '../../hooks/useScrollDirection';

export function BottomNav() {
  const routerState = useRouterState();
  const currentPath = routerState.location.pathname;
  const isVisible = useScrollDirection();

  const navItems = [
    { name: 'Chat', path: '/chat', icon: MessageSquarePlus },
    { name: 'Trips', path: '/trips', icon: Map },
    { name: 'Explore', path: '/explore', icon: MapPin },
    { name: 'Profile', path: '/profile', icon: User },
  ];

  return (
    <nav
      className={`fixed bottom-0 left-0 right-0 z-50 bg-background/80 backdrop-blur-lg border-t pb-safe transition-transform duration-300 md:hidden ${
        isVisible ? 'translate-y-0' : 'translate-y-full'
      }`}
    >
      <div className="flex justify-around items-center h-16 px-2 max-w-lg mx-auto">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = currentPath === item.path || 
                          (item.path !== '/' && currentPath.startsWith(item.path));

          return (
            <Link
              key={item.name}
              to={item.path}
              className={`flex flex-col items-center justify-center flex-1 h-full space-y-1 transition-colors ${
                isActive ? 'text-primary' : 'text-muted-foreground hover:text-foreground'
              }`}
            >
              <Icon className={`w-6 h-6 ${isActive ? 'fill-primary/20' : ''}`} strokeWidth={isActive ? 2.5 : 2} />
              <span className="text-[11px] font-semibold leading-none whitespace-nowrap">{item.name}</span>
            </Link>
          );
        })}
      </div>
    </nav>
  );
}

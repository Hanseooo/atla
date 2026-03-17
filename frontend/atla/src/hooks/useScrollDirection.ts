import { useState, useEffect } from 'react';

/**
 * Custom hook to determine the user's scroll direction.
 * Returns true if the user is scrolling UP (or at the top), 
 * and false if the user is scrolling DOWN.
 * 
 * This is primarily used to hide the BottomNav to maximize 
 * screen real estate when reading content.
 */
export function useScrollDirection() {
  const [isVisible, setIsVisible] = useState(true);
  const [lastScrollY, setLastScrollY] = useState(0);

  useEffect(() => {
    const handleScroll = () => {
      const currentScrollY = window.scrollY;
      
      // If we're at the top of the page, always show it
      if (currentScrollY < 10) {
        setIsVisible(true);
        setLastScrollY(currentScrollY);
        return;
      }

      // If scrolling UP, show the nav
      if (currentScrollY < lastScrollY) {
        setIsVisible(true);
      } 
      // If scrolling DOWN, hide the nav
      else if (currentScrollY > lastScrollY) {
        setIsVisible(false);
      }

      setLastScrollY(currentScrollY);
    };

    // Add event listener with passive option for better scroll performance
    window.addEventListener('scroll', handleScroll, { passive: true });
    
    return () => {
      window.removeEventListener('scroll', handleScroll);
    };
  }, [lastScrollY]);

  return isVisible;
}

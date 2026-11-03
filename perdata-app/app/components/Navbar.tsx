'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useState } from 'react';
import { Menu, X } from 'lucide-react';

const navLinks = [
  { href: '/', label: 'Beranda' },
  { href: '/chat', label: 'Tanya Jawab' },
  { href: '/database', label: 'Database' },
];

export default function Navbar() {
  const pathname = usePathname();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  return (
    <div className="fixed top-0 left-0 w-full px-4 md:px-8 py-4 z-50 flex justify-center pointer-events-none">
      <nav className="pointer-events-auto flex items-center justify-between px-6 md:px-8 py-3 bg-white/95 backdrop-blur-md shadow-lg shadow-[#75162D]/5 w-full max-w-5xl rounded-full border border-[#E8DEC9] font-montserrat relative">
        {/* Brand / Logo in Cyntho Next */}
        <Link href="/" className="flex items-center gap-3 group shrink-0">
          <div className="w-8 h-8 rounded-full bg-[#75162D] text-[#F2E5C6] flex items-center justify-center font-cyntho text-sm font-bold group-hover:scale-105 transition-transform">
            §
          </div>
          <div className="flex flex-col">
            <span className="font-cyntho text-lg font-bold tracking-tight text-[#3B010B]">
              CiviLex<span className="text-[#75162D]">.AI</span>
            </span>
            <span className="text-[9px] tracking-widest uppercase text-[#6B5559] font-semibold -mt-1 font-montserrat">
              KUHPerdata &amp; HIR
            </span>
          </div>
        </Link>

        {/* Desktop Navigation */}
        <div className="hidden md:flex items-center gap-8 font-bold text-sm">
          {navLinks.map((link) => {
            const isActive = pathname === link.href;
            return (
              <Link
                key={link.href}
                href={link.href}
                className={`relative py-1 transition-colors ${
                  isActive
                    ? 'text-[#75162D] font-bold'
                    : 'text-[#6B5559] hover:text-[#3B010B]'
                }`}
              >
                <span>{link.label}</span>
                {isActive && (
                  <span className="absolute left-0 bottom-0 h-[2px] bg-[#75162D] w-full rounded-full" />
                )}
              </Link>
            );
          })}
        </div>

        {/* Mobile menu trigger */}
        <button
          onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          className="md:hidden p-2 rounded-full text-[#3B010B] hover:bg-[#F2E5C6]/50 transition-colors"
          aria-label="Toggle navigation"
        >
          {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
        </button>
      </nav>

      {/* Mobile Drawer */}
      {mobileMenuOpen && (
        <div className="pointer-events-auto absolute top-20 inset-x-4 max-w-lg mx-auto bg-white/95 backdrop-blur-md rounded-2xl border border-[#E8DEC9] p-5 shadow-xl flex flex-col gap-3 font-montserrat">
          {navLinks.map((link) => {
            const isActive = pathname === link.href;
            return (
              <Link
                key={link.href}
                href={link.href}
                onClick={() => setMobileMenuOpen(false)}
                className={`text-sm font-semibold py-2 px-3 rounded-lg transition-colors ${
                  isActive ? 'bg-[#F2E5C6]/60 text-[#75162D] font-bold' : 'text-[#6B5559]'
                }`}
              >
                {link.label}
              </Link>
            );
          })}
        </div>
      )}
    </div>
  );
}

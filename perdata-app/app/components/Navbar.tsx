'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useState } from 'react';
import { Menu, X, ArrowUpRight, Scale } from 'lucide-react';

const navLinks = [
  { href: '/', label: 'Beranda' },
  { href: '/chat', label: 'Konsultasi Hukum' },
  { href: '/database', label: 'Katalog Pasal' },
  { href: '/evaluasi', label: 'Keandalan Sistem' },
];

export default function Navbar() {
  const pathname = usePathname();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  return (
    <header className="fixed top-0 left-0 right-0 z-50 bg-[#faf7f2]/90 backdrop-blur-md border-b border-[#e7dfd5]">
      <div className="max-w-6xl mx-auto px-6 h-20 flex items-center justify-between">
        {/* Brand / Logo */}
        <Link href="/" className="flex items-center gap-2 group">
          <div className="w-8 h-8 rounded-full bg-[#7a1827] text-white flex items-center justify-center font-editorial-display text-lg font-bold group-hover:scale-105 transition-transform">
            §
          </div>
          <div className="flex flex-col">
            <span className="font-editorial-title text-xl font-bold tracking-tight text-[#1c1917]">
              LexPerdata<span className="text-[#7a1827]">.</span>
            </span>
            <span className="text-[10px] tracking-widest uppercase text-[#8a847c] font-medium -mt-1">
              KUHPerdata &amp; HIR
            </span>
          </div>
        </Link>

        {/* Desktop Navigation */}
        <nav className="hidden md:flex items-center gap-8">
          {navLinks.map((link) => {
            const isActive = pathname === link.href;
            return (
              <Link
                key={link.href}
                href={link.href}
                className={`text-sm font-medium tracking-wide transition-colors relative py-1 ${
                  isActive
                    ? 'text-[#7a1827] font-semibold'
                    : 'text-[#57534e] hover:text-[#1c1917]'
                }`}
              >
                {isActive && <span className="inline-block w-1.5 h-1.5 rounded-full bg-[#7a1827] mr-1.5 align-middle"></span>}
                {link.label}
              </Link>
            );
          })}
        </nav>

        {/* Action Button */}
        <div className="hidden md:flex items-center gap-4">
          <Link
            href="/chat"
            className="btn-burgundy px-5 py-2.5 rounded-full text-xs font-semibold tracking-wide flex items-center gap-1.5"
          >
            <span>Mulai Konsultasi</span>
            <ArrowUpRight className="w-3.5 h-3.5" />
          </Link>
        </div>

        {/* Mobile menu trigger */}
        <button
          onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          className="md:hidden p-2 rounded-lg text-[#1c1917] hover:bg-[#f0ebe1] transition-colors"
          aria-label="Toggle navigation"
        >
          {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
        </button>
      </div>

      {/* Mobile Drawer */}
      {mobileMenuOpen && (
        <div className="md:hidden border-t border-[#e7dfd5] bg-[#faf7f2] px-6 py-4 flex flex-col gap-3">
          {navLinks.map((link) => {
            const isActive = pathname === link.href;
            return (
              <Link
                key={link.href}
                href={link.href}
                onClick={() => setMobileMenuOpen(false)}
                className={`text-sm font-medium py-2 transition-colors ${
                  isActive ? 'text-[#7a1827] font-bold' : 'text-[#57534e]'
                }`}
              >
                {link.label}
              </Link>
            );
          })}
          <Link
            href="/chat"
            onClick={() => setMobileMenuOpen(false)}
            className="btn-burgundy mt-2 py-3 rounded-full text-center text-xs font-semibold flex items-center justify-center gap-1.5"
          >
            <span>Mulai Konsultasi</span>
            <ArrowUpRight className="w-3.5 h-3.5" />
          </Link>
        </div>
      )}
    </header>
  );
}

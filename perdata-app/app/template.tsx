'use client';

import { usePathname, useSearchParams } from 'next/navigation';
import { Suspense } from 'react';

function TransitionContent({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const key = `${pathname}?${searchParams.toString()}`;

  return (
    <div key={key} className="animate-page-transition w-full">
      {children}
    </div>
  );
}

export default function Template({ children }: { children: React.ReactNode }) {
  return (
    <Suspense fallback={<div className="w-full">{children}</div>}>
      <TransitionContent>{children}</TransitionContent>
    </Suspense>
  );
}

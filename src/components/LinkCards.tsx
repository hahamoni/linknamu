"use client";

import { useEffect, useState } from "react";

type Link = {
  id: string;
  label: string;
  href: string;
  icon: string;
};

export function LinkCards({ links }: { links: Link[] }) {
  const [counts, setCounts] = useState<Record<string, number>>({});

  useEffect(() => {
    fetch("/api/clicks")
      .then((res) => res.json())
      .then((data: Record<string, number>) => setCounts(data))
      .catch(() => {});
  }, []);

  const handleClick = (id: string) => {
    setCounts((prev) => ({ ...prev, [id]: (prev[id] ?? 0) + 1 }));

    fetch("/api/clicks", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ id }),
      keepalive: true,
    })
      .then((res) => res.json())
      .then((data: { count?: number }) => {
        if (typeof data.count === "number") {
          setCounts((prev) => ({ ...prev, [id]: data.count! }));
        }
      })
      .catch(() => {});
  };

  return (
    <div className="flex w-full flex-col gap-3.5">
      {links.map((link) => (
        <a
          key={link.id}
          href={link.href}
          onClick={() => handleClick(link.id)}
          className="flex w-full items-center justify-between rounded-2xl border border-white/70 bg-white/50 px-4 py-3.5 text-sm font-medium text-slate-700 shadow-sm backdrop-blur-md transition-all duration-200 hover:-translate-y-0.5 hover:bg-white/70 hover:shadow-md"
        >
          <span className="flex items-center gap-2">
            <span aria-hidden>{link.icon}</span>
            {link.label}
          </span>
          <span className="text-xs text-slate-400">
            {counts[link.id] ?? 0}회
          </span>
        </a>
      ))}
    </div>
  );
}

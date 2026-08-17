// TODO: 프로필/링크 데이터는 추후 실제 값(DB 등)으로 교체 예정
const profile = {
  name: "김재광",
  bio: "하루하루 열심히",
};

const links = [
  { label: "GitHub", href: "#", icon: "🐙" },
  { label: "LinkedIn", href: "#", icon: "💼" },
  { label: "Blog", href: "#", icon: "✍️" },
];

export default function Home() {
  return (
    <div className="flex min-h-screen flex-1 items-center justify-center bg-zinc-50 px-4 py-12 dark:bg-black">
      <main className="flex w-full max-w-sm flex-col items-center gap-6 rounded-3xl bg-white p-8 shadow-sm dark:bg-zinc-900">
        <div className="flex h-28 w-28 items-center justify-center rounded-full bg-zinc-200 text-3xl font-semibold text-zinc-500 dark:bg-zinc-700 dark:text-zinc-300">
          {profile.name[0]}
        </div>

        <div className="flex flex-col items-center gap-1 text-center">
          <h1 className="text-xl font-bold text-zinc-900 dark:text-zinc-50">
            {profile.name}
          </h1>
          <p className="text-sm text-zinc-500 dark:text-zinc-400">
            {profile.bio}
          </p>
        </div>

        <div className="flex w-full flex-col gap-3">
          {links.map((link) => (
            <a
              key={link.label}
              href={link.href}
              className="flex w-full items-center justify-center gap-2 rounded-xl border border-zinc-200 bg-white px-4 py-3 text-sm font-medium text-zinc-800 transition-colors hover:bg-zinc-50 dark:border-zinc-700 dark:bg-zinc-800 dark:text-zinc-100 dark:hover:bg-zinc-700"
            >
              <span aria-hidden>{link.icon}</span>
              {link.label}
            </a>
          ))}
        </div>
      </main>
    </div>
  );
}

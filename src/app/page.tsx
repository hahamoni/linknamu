// TODO: 프로필/링크 데이터는 추후 실제 값(DB 등)으로 교체 예정
const profile = {
  name: "김재광",
  bio: "배터리 소재 연구원 | 요즘에는 AI를 배우고 있어요",
  photoUrl: "/profile.jpg",
};

const links = [
  { label: "GitHub", href: "https://github.com/hahamoni", icon: "🐙" },
  { label: "LinkedIn", href: "#", icon: "💼" },
  { label: "Email", href: "mailto:rlaworhkd000@gmail.com", icon: "📧" },
];

export default function Home() {
  return (
    <div className="flex min-h-screen flex-1 items-center justify-center bg-gradient-to-b from-[#F3FAFF] via-[#E4F3FD] to-[#CDEAFB] px-6 py-16">
      <main className="flex w-full max-w-sm flex-col items-center gap-8 rounded-[2rem] border border-white/60 bg-white/40 p-10 shadow-[0_8px_32px_-8px_rgba(84,150,196,0.25)] backdrop-blur-xl">
        <img
          src={profile.photoUrl}
          alt={profile.name}
          className="h-32 w-32 rounded-full object-cover shadow-[0_6px_20px_-4px_rgba(84,150,196,0.45)] ring-4 ring-white/80"
        />

        <div className="flex flex-col items-center gap-1.5 text-center">
          <h1 className="text-xl font-bold tracking-tight text-slate-800">
            {profile.name}
          </h1>
          <p className="text-sm text-slate-500">{profile.bio}</p>
        </div>

        <div className="flex w-full flex-col gap-3.5">
          {links.map((link) => (
            <a
              key={link.label}
              href={link.href}
              className="flex w-full items-center justify-center gap-2 rounded-2xl border border-white/70 bg-white/50 px-4 py-3.5 text-sm font-medium text-slate-700 shadow-sm backdrop-blur-md transition-all duration-200 hover:-translate-y-0.5 hover:bg-white/70 hover:shadow-md"
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

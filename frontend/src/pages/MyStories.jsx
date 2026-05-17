import { Link } from "react-router-dom";
import { LibraryBig, Sparkles } from "lucide-react";

export default function MyStories() {
  return (
    <div className="min-h-screen bg-[#fff5cf] px-6 py-8 text-slate-900">
      <Link to="/" className="inline-flex items-center gap-3">
        <div className="flex h-12 w-12 items-center justify-center rounded-2xl border-4 border-slate-900 bg-orange-400 shadow-[5px_5px_0_#111827]">
          <Sparkles className="h-6 w-6" />
        </div>
        <span className="text-xl font-black tracking-tight">StoryBook Agent</span>
      </Link>

      <main className="mx-auto mt-20 max-w-3xl">
        <div className="inline-flex items-center gap-2 rounded-2xl border-4 border-slate-900 bg-cyan-300 px-4 py-2 font-black shadow-[4px_4px_0_#111827]">
          <LibraryBig className="h-5 w-5" />
          Mis historias
        </div>
        <h1 className="mt-6 text-5xl font-black leading-none tracking-tight">
          Tus cuentos guardados apareceran aqui.
        </h1>
      </main>
    </div>
  );
}

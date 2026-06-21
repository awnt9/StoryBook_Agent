import { LibraryBig } from "lucide-react";
import Navbar from "../components/Navbar";

export default function MyStories() {
  return (
    <div className="min-h-screen bg-[#fff5cf] text-slate-900">
      <Navbar />

      <main className="mx-auto mt-20 max-w-3xl px-6 pb-8">
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

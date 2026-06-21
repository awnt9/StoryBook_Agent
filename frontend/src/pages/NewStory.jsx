import { BookOpen } from "lucide-react";
import { StoryBookPreview } from "../components/book";
import Navbar from "../components/Navbar";

export default function NewStory() {
  return (
    <div className="min-h-screen bg-[#fff5cf] text-slate-900">
      <Navbar />

      <main className="mx-auto mt-12 max-w-6xl px-6 pb-8">
        <div className="inline-flex items-center gap-2 rounded-2xl border-4 border-slate-900 bg-pink-400 px-4 py-2 font-black shadow-[4px_4px_0_#111827]">
          <BookOpen className="h-5 w-5" />
          Nueva historia
        </div>
        <h1 className="mt-6 text-5xl font-black leading-none tracking-tight md:text-6xl">
          Aqui empieza la proxima aventura.
        </h1>
        <div className="mt-10">
          <StoryBookPreview />
        </div>
      </main>
    </div>
  );
}

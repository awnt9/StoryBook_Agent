import { motion } from "framer-motion";
import { Sparkles, Palette, Zap, Wand2, Search } from "lucide-react";
import { useNavigate } from "react-router-dom";

const fadeInUp = {
  initial: { opacity: 0, y: 20 },
  animate: { opacity: 1, y: 0 },
};

export default function Home() {
  const navigate = useNavigate();

  const goToProtectedPage = (path) => {
    const accessToken = localStorage.getItem("access_token");

    if (accessToken) {
      navigate(path);
      return;
    }

    navigate("/login", { state: { redirectTo: path } });
  };

  return (
    <div className="min-h-screen overflow-x-hidden bg-[#fff5cf] text-slate-900">
      <div className="absolute inset-0 pointer-events-none overflow-hidden">
        <motion.div
          initial={{ opacity: 0, scale: 0.7 }}
          animate={{ opacity: 0.7, scale: 1 }}
          transition={{ duration: 0.9, delay: 0.05 }}
          className="absolute -top-24 -left-24 h-72 w-72 rounded-full bg-pink-300 blur-3xl"
        />
        <motion.div
          initial={{ opacity: 0, scale: 0.7 }}
          animate={{ opacity: 0.7, scale: 1 }}
          transition={{ duration: 0.9, delay: 0.15 }}
          className="absolute top-32 -right-20 h-80 w-80 rounded-full bg-cyan-300 blur-3xl"
        />
        <motion.div
          initial={{ opacity: 0, scale: 0.7 }}
          animate={{ opacity: 0.6, scale: 1 }}
          transition={{ duration: 0.9, delay: 0.25 }}
          className="absolute bottom-10 left-1/3 h-80 w-80 rounded-full bg-yellow-300 blur-3xl"
        />
      </div>

      <motion.header
        {...fadeInUp}
        transition={{ duration: 0.5 }}
        className="relative z-10 mx-auto flex max-w-7xl items-center px-6 py-6"
      >
        <motion.div
          initial={{ opacity: 0, x: -18 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5, delay: 0.05 }}
          className="flex items-center gap-6"
        >
          <motion.div
            initial={{ opacity: 0, scale: 0.7, rotate: -12 }}
            animate={{ opacity: 1, scale: 1, rotate: 0 }}
            transition={{ duration: 0.55, delay: 0.12 }}
            className="flex h-12 w-12 items-center justify-center rounded-2xl border-4 border-slate-900 bg-orange-400 shadow-[5px_5px_0_#111827]"
          >
            <Sparkles className="h-6 w-6" />
          </motion.div>

          <motion.span
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.45, delay: 0.2 }}
            className="text-xl font-black tracking-tight"
          >
            StoryBook Agent
          </motion.span>

          <nav className="flex items-center gap-4">
            <motion.button
              {...fadeInUp}
              transition={{ duration: 0.6, delay: 0.22 }}
              onClick={() => navigate("/login")}
              className="text-lg font-semibold leading-relaxed text-slate-700 hover:text-slate-900 cursor-pointer"
            >
              Iniciar sesión/Registrarse
            </motion.button>

            <motion.a
              {...fadeInUp}
              transition={{ duration: 0.6, delay: 0.28 }}
              href="https://github.com/awnt9/StoryBook_Agent"
              target="_blank"
              rel="noopener noreferrer"
              className="text-lg font-semibold leading-relaxed text-slate-700 hover:text-slate-900 cursor-pointer"
            >
              Repositorio de GitHub
            </motion.a>
          </nav>
        </motion.div>
      </motion.header>

      <main className="relative z-10">
        <section className="mx-auto grid max-w-7xl items-center gap-12 px-6 py-16 md:grid-cols-2 md:py-24">
          <div>
            <motion.h1
              {...fadeInUp}
              transition={{ duration: 0.6, delay: 0.1 }}
              className="max-w-xl text-5xl font-black leading-[0.95] tracking-tight md:text-7xl"
            >
              Storybook Agent.
            </motion.h1>

            <motion.p
              {...fadeInUp}
              transition={{ duration: 0.6, delay: 0.22 }}
              className="mt-6 max-w-lg text-lg font-semibold leading-relaxed text-slate-700"
            >
              Cuento infantil e interactivo que se escribe delante de tus ojos con la ayuda de un agente de inteligencia artificial.
            </motion.p>

            <motion.div
              {...fadeInUp}
              transition={{ duration: 0.6, delay: 0.34 }}
              className="mt-8 flex flex-wrap gap-4"
            >
              <motion.button
                initial={{ opacity: 0, y: 18, scale: 0.96 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                transition={{ duration: 0.45, delay: 0.42 }}
                whileHover={{ y: -4 }}
                whileTap={{ y: 0, scale: 0.98 }}
                onClick={() => goToProtectedPage("/nueva-historia")}
                className="rounded-3xl border-4 border-slate-900 bg-pink-400 px-7 py-4 text-lg font-black shadow-[6px_6px_0_#111827]"
              >
                Nueva historia
              </motion.button>
              <motion.button
                initial={{ opacity: 0, y: 18, scale: 0.96 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                transition={{ duration: 0.45, delay: 0.5 }}
                whileHover={{ y: -4 }}
                whileTap={{ y: 0, scale: 0.98 }}
                onClick={() => goToProtectedPage("/mis-historias")}
                className="rounded-3xl border-4 border-slate-900 bg-cyan-300 px-7 py-4 text-lg font-black shadow-[6px_6px_0_#111827]"
              >
                Mis historias
              </motion.button>
            </motion.div>
          </div>

          <motion.div
            initial={{ opacity: 0, scale: 0.92, rotate: -3 }}
            animate={{ opacity: 1, scale: 1, rotate: 0 }}
            transition={{ duration: 0.7, delay: 0.15 }}
            className="relative -translate-y-8"
          >
            <motion.div
              initial={{ opacity: 0, y: 18 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.55, delay: 0.3 }}
              className="rounded-[2rem] border-4 border-slate-900 bg-white p-5 shadow-[12px_12px_0_#111827]"
            >
              <motion.div
                initial={{ opacity: 0, scale: 0.97 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.55, delay: 0.42 }}
                className="rounded-[1.5rem] border-4 border-slate-900 bg-gradient-to-br from-yellow-200 via-pink-200 to-cyan-200 p-6"
              >
                <motion.div
                  initial={{ opacity: 0, y: 14 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.45, delay: 0.55 }}
                  className="mb-5 flex items-center justify-between"
                >
                  <motion.div
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ duration: 0.4, delay: 0.62 }}
                    className="rounded-2xl border-4 border-slate-900 bg-orange-400 px-4 py-2 font-black shadow-[3px_3px_0_#111827]"
                  >
                    Tools del agente
                  </motion.div>
                </motion.div>

                <div className="grid grid-cols-3 gap-4">
                  {[
                    { color: "bg-red-400", icon: Search, label: "Analisis de imagen" },
                    { color: "bg-blue-400", icon: Palette, label: "Generacion de imagen" },
                    { color: "bg-lime-400", icon: Wand2, label: "Generacion de texto" },
                    { color: "bg-purple-400", icon: Zap, label: "Opciones dinamicas" },
                  ].map((feature, index) => {
                    const Icon = feature.icon;
                    return (
                      <motion.div
                        key={index}
                        initial={{ opacity: 0, y: 18, scale: 0.9 }}
                        animate={{ opacity: 1, scale: 1, y: [0, -8, 0] }}
                        transition={{
                          opacity: { duration: 0.35, delay: 0.72 + index * 0.08 },
                          scale: { duration: 0.35, delay: 0.72 + index * 0.08 },
                          y: {
                            duration: 2,
                            repeat: Infinity,
                            delay: 0.9 + index * 0.12,
                          },
                        }}
                        className={`h-24 rounded-3xl border-4 border-slate-900 ${feature.color} shadow-[5px_5px_0_#111827] flex flex-col items-center justify-center gap-1`}
                      >
                        <motion.div
                          initial={{ opacity: 0, scale: 0.7 }}
                          animate={{ opacity: 1, scale: 1 }}
                          transition={{ duration: 0.3, delay: 0.85 + index * 0.08 }}
                        >
                          <Icon className="h-6 w-6" />
                        </motion.div>
                        <motion.span
                          initial={{ opacity: 0, y: 6 }}
                          animate={{ opacity: 1, y: 0 }}
                          transition={{ duration: 0.3, delay: 0.92 + index * 0.08 }}
                          className="text-xs font-bold"
                        >
                          {feature.label}
                        </motion.span>
                      </motion.div>
                    );
                  })}
                </div>
              </motion.div>
            </motion.div>
          </motion.div>
        </section>
      </main>
    </div>
  );
}

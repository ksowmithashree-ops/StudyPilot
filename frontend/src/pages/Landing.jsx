import { useNavigate } from "react-router-dom";
import { CalendarCheck, Bot, RefreshCcw, Sparkles, Timer, TrendingUp } from "lucide-react";
import { api } from "../api/client.js";
import { Button } from "../components/ui/Button.jsx";
import { useToasts } from "../hooks/useToasts.js";

const features = [
  { icon: Sparkles, title: "AI Study Planner", body: "Builds a realistic daily plan from deadlines, difficulty, progress and available time." },
  { icon: RefreshCcw, title: "Adaptive rescheduling", body: "Miss a session and StudyPilot finds the next suitable slot automatically." },
  { icon: Timer, title: "Overload detection", body: "Plans never exceed your available study hours. Extra work is deferred or shortened." },
  { icon: TrendingUp, title: "Exam readiness", body: "See how prepared you are from topic mastery, revision and time left." },
  { icon: CalendarCheck, title: "Calendar + progress", body: "Exams, deadlines and study sessions in one calendar, with charts for hours and tasks." },
  { icon: Bot, title: "AI Study Assistant", body: "Ask what to study today. Gemini when a key is set, otherwise a local coach." },
];

export default function Landing() {
  const navigate = useNavigate();
  const { pushToast } = useToasts();

  async function startDemo() {
    try {
      await api.post("/demo/reset", {});
      pushToast("Demo data loaded for Alex’s DBMS week", "success");
      navigate("/app");
    } catch (err) {
      pushToast(err.message, "error");
    }
  }

  return (
    <div className="min-h-screen bg-[radial-gradient(circle_at_20%_20%,#c7d2fe,transparent_32%),radial-gradient(circle_at_80%_0%,#ddd6fe,transparent_30%),#f8fafc]">
      <header className="mx-auto flex max-w-6xl items-center justify-between px-5 py-5">
        <p className="text-lg font-extrabold text-slate-900">StudyPilot</p>
        <Button variant="secondary" onClick={startDemo}>
          Try Demo
        </Button>
      </header>
      <section className="mx-auto grid max-w-6xl items-center gap-10 px-5 py-10 lg:grid-cols-2 lg:py-16">
        <div className="fade-in">
          <p className="mb-3 inline-flex rounded-full bg-indigo-50 px-3 py-1 text-xs font-semibold text-indigo-700">
            AI-powered adaptive study planner
          </p>
          <h1 className="text-4xl font-extrabold leading-tight text-slate-900 sm:text-5xl">
            Plan smarter. Reschedule automatically. Walk into exams ready.
          </h1>
          <p className="mt-4 max-w-xl text-slate-600">
            StudyPilot builds a personalized timetable from your subjects, topics, deadlines and available hours — then
            adapts when life gets in the way.
          </p>
          <div className="mt-6 flex flex-wrap gap-3">
            <Button onClick={startDemo}>Get Started</Button>
            <Button variant="secondary" onClick={() => navigate("/app")}>
              Open dashboard
            </Button>
          </div>
        </div>
        <div className="rounded-3xl border border-white/70 bg-white/80 p-6 shadow-card fade-in">
          <p className="text-sm font-semibold text-indigo-700">Hackathon demo</p>
          <h2 className="mt-1 text-xl font-bold">DBMS exam in 5 days</h2>
          <p className="mt-2 text-sm text-slate-500">
            Normalization is only at 18%. Generate an AI plan, mark it missed, and watch it reschedule with a
            notification — readiness updates live.
          </p>
          <div className="mt-4 grid grid-cols-3 gap-3 text-center">
            {[
              ["18%", "Normalization"],
              ["5d", "Until exam"],
              ["3h", "Daily budget"],
            ].map(([value, label]) => (
              <div key={label} className="rounded-2xl bg-slate-50 p-3">
                <p className="text-xl font-bold text-slate-900">{value}</p>
                <p className="text-xs text-slate-500">{label}</p>
              </div>
            ))}
          </div>
        </div>
      </section>
      <section className="mx-auto grid max-w-6xl gap-4 px-5 pb-16 sm:grid-cols-2 lg:grid-cols-3">
        {features.map((feature) => (
          <div key={feature.title} className="rounded-2xl border border-white bg-white/80 p-5 shadow-card">
            <feature.icon className="mb-3 h-5 w-5 text-indigo-600" />
            <h3 className="font-semibold">{feature.title}</h3>
            <p className="mt-1 text-sm text-slate-500">{feature.body}</p>
          </div>
        ))}
      </section>
    </div>
  );
}

import { useState } from "react";
import { api } from "../api/client.js";
import { Button } from "../components/ui/Button.jsx";
import { Card } from "../components/ui/Card.jsx";
import { Topbar } from "../components/layout/Topbar.jsx";
import { useToasts } from "../hooks/useToasts.js";

const prompts = ["What should I study today?", "Am I ready for DBMS?", "What’s overdue?"];

export default function Assistant() {
  const [message, setMessage] = useState("");
  const [busy, setBusy] = useState(false);
  const [chat, setChat] = useState([
    {
      role: "assistant",
      text: "Ask me what to study today, how ready you are for DBMS, or what got missed.",
    },
  ]);
  const { pushToast } = useToasts();

  async function send(text) {
    const content = (text || message).trim();
    if (!content) return;
    setChat((c) => [...c, { role: "user", text: content }]);
    setMessage("");
    setBusy(true);
    try {
      const result = await api.post("/chat", { message: content });
      setChat((c) => [...c, { role: "assistant", text: result.reply, gemini: result.used_gemini }]);
    } catch (err) {
      pushToast(err.message, "error");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="fade-in">
      <Topbar title="AI Assistant" subtitle="Gemini when configured, otherwise a local study coach." />
      <Card className="flex min-h-[480px] flex-col">
        <div className="mb-3 flex flex-wrap gap-2">
          {prompts.map((p) => (
            <button
              key={p}
              onClick={() => send(p)}
              className="rounded-full bg-indigo-50 px-3 py-1 text-xs font-medium text-indigo-700"
            >
              {p}
            </button>
          ))}
        </div>
        <div className="flex-1 space-y-3 overflow-y-auto">
          {chat.map((item, idx) => (
            <div
              key={idx}
              className={`max-w-[85%] rounded-2xl px-4 py-3 text-sm ${
                item.role === "user" ? "ml-auto bg-indigo-600 text-white" : "bg-slate-50 text-slate-700"
              }`}
            >
              {item.text}
            </div>
          ))}
        </div>
        <form
          className="mt-4 flex gap-2"
          onSubmit={(e) => {
            e.preventDefault();
            send();
          }}
        >
          <input
            className="flex-1 rounded-xl border px-3 py-2"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            placeholder="Ask StudyPilot…"
          />
          <Button disabled={busy}>{busy ? "…" : "Send"}</Button>
        </form>
      </Card>
    </div>
  );
}

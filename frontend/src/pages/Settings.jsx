import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../api/client.js";
import { Button } from "../components/ui/Button.jsx";
import { Card } from "../components/ui/Card.jsx";
import { Topbar } from "../components/layout/Topbar.jsx";
import { useToasts } from "../hooks/useToasts.js";

export default function Settings() {
  const [settings, setSettings] = useState(null);
  const { pushToast } = useToasts();
  const navigate = useNavigate();

  useEffect(() => {
    api.get("/settings").then(setSettings).catch((err) => pushToast(err.message, "error"));
  }, []);

  async function save() {
    try {
      const updated = await api.patch("/settings", {
        name: settings.name,
        daily_available_minutes: Number(settings.daily_available_minutes),
      });
      setSettings(updated);
      pushToast("Settings saved", "success");
    } catch (err) {
      pushToast(err.message, "error");
    }
  }

  async function resetDemo() {
    try {
      await api.post("/api/demo/reset", {});
      pushToast("Demo data reset — DBMS exam in 5 days", "success");
      navigate("/app");
    } catch (err) {
      pushToast(err.message, "error");
    }
  }

  if (!settings) return null;

  return (
    <div className="fade-in">
      <Topbar title="Settings" subtitle="Study hours, demo data, and AI status." />
      <Card className="max-w-xl space-y-4">
        <label className="block text-sm">
          Name
          <input
            className="mt-1 w-full rounded-xl border px-3 py-2"
            value={settings.name}
            onChange={(e) => setSettings({ ...settings, name: e.target.value })}
          />
        </label>
        <label className="block text-sm">
          Daily available minutes
          <input
            className="mt-1 w-full rounded-xl border px-3 py-2"
            type="number"
            min="30"
            value={settings.daily_available_minutes}
            onChange={(e) => setSettings({ ...settings, daily_available_minutes: e.target.value })}
          />
        </label>
        <p className="text-sm text-slate-500">
          Gemini: {settings.gemini_enabled ? "connected" : "not configured — using local fallback"}
        </p>
        <div className="flex flex-wrap gap-2">
          <Button onClick={save}>Save</Button>
          <Button variant="secondary" onClick={resetDemo}>
            Reset demo data
          </Button>
        </div>
      </Card>
    </div>
  );
}

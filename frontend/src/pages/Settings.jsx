import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../api/client.js";
import { Button } from "../components/ui/Button.jsx";
import { Card } from "../components/ui/Card.jsx";
import { Topbar } from "../components/layout/Topbar.jsx";
import { useToasts } from "../hooks/useToasts.js";

export default function Settings() {
  const [settings, setSettings] = useState(null);
  const [showNameSetup, setShowNameSetup] = useState(false);
  const [nameInput, setNameInput] = useState("");

  const { pushToast } = useToasts();
  const navigate = useNavigate();

  useEffect(() => {
    api
      .get("/settings")
      .then((data) => {
        setSettings(data);

        // Ask for name only if the default name is still being used
        if (!data.name || data.name === "Alex") {
          setShowNameSetup(true);
          setNameInput("");
        }
      })
      .catch((err) => pushToast(err.message, "error"));
  }, []);

  async function save() {
    try {
      const name = settings.name.trim();

      if (!name) {
        pushToast("Please enter your name", "error");
        return;
      }

      const updated = await api.patch("/settings", {
        name,
        daily_available_minutes: Number(settings.daily_available_minutes),
      });

      setSettings(updated);
      pushToast("Profile updated successfully", "success");
    } catch (err) {
      pushToast(err.message, "error");
    }
  }

  async function saveFirstName() {
    const name = nameInput.trim();

    if (!name) {
      pushToast("Please enter your name", "error");
      return;
    }

    try {
      const updated = await api.patch("/settings", {
        name,
        daily_available_minutes: Number(settings.daily_available_minutes),
      });

      setSettings(updated);
      setShowNameSetup(false);
      pushToast(`Welcome, ${updated.name}!`, "success");
    } catch (err) {
      pushToast(err.message, "error");
    }
  }

  async function resetDemo() {
    try {
      // client.js already adds /api
      await api.post("/demo/reset", {});

      pushToast("Demo data reset — DBMS exam in 5 days", "success");
      navigate("/app");
    } catch (err) {
      pushToast(err.message, "error");
    }
  }

  if (!settings) return null;

  return (
    <div className="fade-in">
      <Topbar
        title="Profile & Settings"
        subtitle="Manage your profile and study preferences."
      />

      {/* First-time name setup */}
      {showNameSetup && (
        <Card className="max-w-xl mb-4 space-y-4">
          <div>
            <h2 className="text-lg font-semibold">
              Welcome to StudyPilot 👋
            </h2>

            <p className="text-sm text-slate-500 mt-1">
              Enter your name to personalize your study dashboard.
            </p>
          </div>

          <label className="block text-sm">
            Your name

            <input
              autoFocus
              className="mt-1 w-full rounded-xl border px-3 py-2"
              placeholder="Enter your name"
              value={nameInput}
              onChange={(e) => setNameInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter") {
                  saveFirstName();
                }
              }}
            />
          </label>

          <Button onClick={saveFirstName}>
            Continue
          </Button>
        </Card>
      )}

      {/* Profile settings */}
      <Card className="max-w-xl space-y-4">
        <h2 className="text-lg font-semibold">
          Profile
        </h2>

        <label className="block text-sm">
          Name

          <input
            className="mt-1 w-full rounded-xl border px-3 py-2"
            value={settings.name}
            onChange={(e) =>
              setSettings({
                ...settings,
                name: e.target.value,
              })
            }
          />
        </label>

        <label className="block text-sm">
          Daily available minutes

          <input
            className="mt-1 w-full rounded-xl border px-3 py-2"
            type="number"
            min="30"
            value={settings.daily_available_minutes}
            onChange={(e) =>
              setSettings({
                ...settings,
                daily_available_minutes: e.target.value,
              })
            }
          />
        </label>

        <p className="text-sm text-slate-500">
          Gemini:{" "}
          {settings.gemini_enabled
            ? "connected"
            : "not configured — using local fallback"}
        </p>

        <div className="flex flex-wrap gap-2">
          <Button onClick={save}>
            Save Profile
          </Button>

          <Button
            variant="secondary"
            onClick={resetDemo}
          >
            Reset demo data
          </Button>
        </div>
      </Card>
    </div>
  );
}
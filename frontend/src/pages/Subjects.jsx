import { useEffect, useState } from "react";
import { api } from "../api/client.js";
import { Button } from "../components/ui/Button.jsx";
import { Card } from "../components/ui/Card.jsx";
import { EmptyState } from "../components/ui/EmptyState.jsx";
import { Modal } from "../components/ui/Modal.jsx";
import { ProgressBar } from "../components/ui/ProgressBar.jsx";
import { Topbar } from "../components/layout/Topbar.jsx";
import { useToasts } from "../hooks/useToasts.js";

const emptySubject = { name: "", color: "#6366f1", importance: 5 };
const emptyTopic = { name: "", difficulty: 3, progress_pct: 0, estimated_minutes: 120 };
const emptyDeadline = { title: "", type: "exam", due_date: "", subject_id: "", priority: 3 };

export default function Subjects() {
  const [subjects, setSubjects] = useState([]);
  const [topics, setTopics] = useState([]);
  const [deadlines, setDeadlines] = useState([]);
  const [subjectForm, setSubjectForm] = useState(null);
  const [topicForm, setTopicForm] = useState(null);
  const [deadlineForm, setDeadlineForm] = useState(null);
  const { pushToast } = useToasts();

  async function load() {
    try {
      const [s, t, d] = await Promise.all([api.get("/subjects"), api.get("/topics"), api.get("/deadlines")]);
      setSubjects(s);
      setTopics(t);
      setDeadlines(d);
    } catch (err) {
      pushToast(err.message, "error");
    }
  }

  useEffect(() => {
    load();
  }, []);

  async function saveSubject() {
    try {
      if (subjectForm.id) await api.patch(`/subjects/${subjectForm.id}`, subjectForm);
      else await api.post("/subjects", subjectForm);
      setSubjectForm(null);
      load();
    } catch (err) {
      pushToast(err.message, "error");
    }
  }

  async function saveTopic() {
    try {
      if (topicForm.id) await api.patch(`/topics/${topicForm.id}`, topicForm);
      else await api.post(`/subjects/${topicForm.subject_id}/topics`, topicForm);
      setTopicForm(null);
      load();
    } catch (err) {
      pushToast(err.message, "error");
    }
  }

  async function saveDeadline() {
    try {
      const payload = { ...deadlineForm, subject_id: Number(deadlineForm.subject_id) };
      if (deadlineForm.id) await api.patch(`/deadlines/${deadlineForm.id}`, payload);
      else await api.post("/deadlines", payload);
      setDeadlineForm(null);
      load();
    } catch (err) {
      pushToast(err.message, "error");
    }
  }

  return (
    <div className="fade-in">
      <Topbar title="My Subjects" subtitle="Manage subjects, topics, exams, assignments and quizzes." />
      <div className="mb-4 flex flex-wrap gap-2">
        <Button onClick={() => setSubjectForm({ ...emptySubject })}>Add subject</Button>
        <Button variant="secondary" onClick={() => setDeadlineForm({ ...emptyDeadline, subject_id: subjects[0]?.id || "" })}>
          Add deadline
        </Button>
      </div>
      {subjects.length === 0 ? (
        <EmptyState title="No subjects yet" body="Add DBMS, OS or any course to start planning." />
      ) : (
        <div className="grid gap-4 lg:grid-cols-2">
          {subjects.map((subject) => {
            const subjectTopics = topics.filter((t) => t.subject_id === subject.id);
            return (
              <Card key={subject.id}>
                <div className="mb-3 flex items-start justify-between">
                  <div>
                    <h2 className="text-lg font-semibold" style={{ color: subject.color }}>
                      {subject.name}
                    </h2>
                    <p className="text-xs text-slate-400">Importance {subject.importance}/5</p>
                  </div>
                  <div className="flex gap-2 text-xs">
                    <button onClick={() => setSubjectForm(subject)} className="text-indigo-600">
                      Edit
                    </button>
                    <button
                      onClick={async () => {
                        await api.del(`/subjects/${subject.id}`);
                        load();
                      }}
                      className="text-rose-600"
                    >
                      Delete
                    </button>
                  </div>
                </div>
                <div className="space-y-3">
                  {subjectTopics.map((topic) => (
                    <div key={topic.id} className="rounded-xl bg-slate-50 p-3">
                      <div className="flex items-center justify-between text-sm">
                        <span className="font-medium">{topic.name}</span>
                        <span className="text-slate-400">{topic.progress_pct}%</span>
                      </div>
                      <ProgressBar value={topic.progress_pct} />
                      <p className="mt-1 text-xs text-slate-400">
                        Difficulty {topic.difficulty}/5 · {topic.estimated_minutes} min estimated
                      </p>
                      <div className="mt-2 flex gap-2 text-xs">
                        <button onClick={() => setTopicForm(topic)} className="text-indigo-600">
                          Edit
                        </button>
                        <button
                          onClick={async () => {
                            await api.del(`/topics/${topic.id}`);
                            load();
                          }}
                          className="text-rose-600"
                        >
                          Delete
                        </button>
                      </div>
                    </div>
                  ))}
                  <Button variant="ghost" onClick={() => setTopicForm({ ...emptyTopic, subject_id: subject.id })}>
                    Add topic
                  </Button>
                </div>
              </Card>
            );
          })}
        </div>
      )}
      <Card className="mt-6">
        <h2 className="mb-3 font-semibold">Deadlines</h2>
        {deadlines.length === 0 ? (
          <EmptyState title="No deadlines" body="Add exams, assignments, projects or quizzes." />
        ) : (
          <div className="space-y-2">
            {deadlines.map((d) => (
              <div key={d.id} className="flex flex-wrap items-center justify-between gap-2 rounded-xl bg-slate-50 p-3 text-sm">
                <div>
                  <p className="font-medium">{d.title}</p>
                  <p className="text-xs text-slate-400">
                    {d.type} · {d.subject_name} · {d.due_date}
                  </p>
                </div>
                <div className="flex gap-2 text-xs">
                  <button onClick={() => setDeadlineForm(d)} className="text-indigo-600">
                    Edit
                  </button>
                  <button
                    onClick={async () => {
                      await api.del(`/deadlines/${d.id}`);
                      load();
                    }}
                    className="text-rose-600"
                  >
                    Delete
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </Card>

      <Modal open={!!subjectForm} title="Subject" onClose={() => setSubjectForm(null)}>
        {subjectForm ? (
          <div className="space-y-3">
            <input
              className="w-full rounded-xl border px-3 py-2"
              value={subjectForm.name}
              onChange={(e) => setSubjectForm({ ...subjectForm, name: e.target.value })}
              placeholder="Name"
            />
            <input
              className="w-full rounded-xl border px-3 py-2"
              type="number"
              min="1"
              max="5"
              value={subjectForm.importance}
              onChange={(e) => setSubjectForm({ ...subjectForm, importance: Number(e.target.value) })}
            />
            <Button onClick={saveSubject}>Save</Button>
          </div>
        ) : null}
      </Modal>
      <Modal open={!!topicForm} title="Topic" onClose={() => setTopicForm(null)}>
        {topicForm ? (
          <div className="space-y-3">
            <input
              className="w-full rounded-xl border px-3 py-2"
              value={topicForm.name}
              onChange={(e) => setTopicForm({ ...topicForm, name: e.target.value })}
              placeholder="Name"
            />
            {["difficulty", "progress_pct", "estimated_minutes"].map((field) => (
              <label key={field} className="block text-sm">
                {field}
                <input
                  className="mt-1 w-full rounded-xl border px-3 py-2"
                  type="number"
                  value={topicForm[field]}
                  onChange={(e) => setTopicForm({ ...topicForm, [field]: Number(e.target.value) })}
                />
              </label>
            ))}
            <Button onClick={saveTopic}>Save</Button>
          </div>
        ) : null}
      </Modal>
      <Modal open={!!deadlineForm} title="Deadline" onClose={() => setDeadlineForm(null)}>
        {deadlineForm ? (
          <div className="space-y-3">
            <input
              className="w-full rounded-xl border px-3 py-2"
              value={deadlineForm.title}
              onChange={(e) => setDeadlineForm({ ...deadlineForm, title: e.target.value })}
              placeholder="Title"
            />
            <select
              className="w-full rounded-xl border px-3 py-2"
              value={deadlineForm.type}
              onChange={(e) => setDeadlineForm({ ...deadlineForm, type: e.target.value })}
            >
              {["exam", "assignment", "project", "quiz"].map((t) => (
                <option key={t}>{t}</option>
              ))}
            </select>
            <select
              className="w-full rounded-xl border px-3 py-2"
              value={deadlineForm.subject_id}
              onChange={(e) => setDeadlineForm({ ...deadlineForm, subject_id: e.target.value })}
            >
              {subjects.map((s) => (
                <option key={s.id} value={s.id}>
                  {s.name}
                </option>
              ))}
            </select>
            <input
              className="w-full rounded-xl border px-3 py-2"
              type="date"
              value={(deadlineForm.due_date || "").slice(0, 10)}
              onChange={(e) => setDeadlineForm({ ...deadlineForm, due_date: e.target.value })}
            />
            <Button onClick={saveDeadline}>Save</Button>
          </div>
        ) : null}
      </Modal>
    </div>
  );
}

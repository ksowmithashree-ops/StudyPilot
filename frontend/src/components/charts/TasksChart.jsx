import { CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

export function TasksChart({ data }) {
  return (
    <div className="h-64">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
          <XAxis dataKey="date" tick={{ fontSize: 11 }} tickFormatter={(v) => v.slice(5)} />
          <YAxis allowDecimals={false} />
          <Tooltip />
          <Line type="monotone" dataKey="completed" stroke="#06b6d4" strokeWidth={3} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

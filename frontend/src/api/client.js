const API = import.meta.env.VITE_API_URL || "/api";

async function request(path, options = {}) {
  const url = `${API}${path}`;

  const response = await fetch(url, {
    method: options.method || "GET",
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
    body: options.body ? JSON.stringify(options.body) : undefined,
  });

  const text = await response.text();

  let data = {};

  try {
    data = text ? JSON.parse(text) : {};
  } catch {
    data = {};
  }

  if (!response.ok) {
    throw new Error(
      `API Error ${response.status} at ${url}: ${
        data.error || text || "Unknown error"
      }`
    );
  }

  return data;
}

export const api = {
  get: (path) => request(path),

  post: (path, body) =>
    request(path, {
      method: "POST",
      body,
    }),

  patch: (path, body) =>
    request(path, {
      method: "PATCH",
      body,
    }),

  del: (path) =>
    request(path, {
      method: "DELETE",
    }),
};
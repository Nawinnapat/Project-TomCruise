import { readFileSync } from "node:fs";

const input = JSON.parse(readFileSync(0, "utf8"));
const url = new URL(input.url);

if (input.params) {
  for (const [key, value] of Object.entries(input.params)) {
    if (value !== null && value !== undefined) url.searchParams.set(key, String(value));
  }
}

const headers = input.headers || {};
const options = {
  method: input.method,
  headers,
};

if (input.json !== undefined) {
  options.body = JSON.stringify(input.json);
}

try {
  const response = await fetch(url, options);
  const body = await response.text();
  console.log(
    JSON.stringify({
      status: response.status,
      ok: response.ok,
      headers: Object.fromEntries(response.headers.entries()),
      body,
    })
  );
} catch (error) {
  console.log(
    JSON.stringify({
      status: 0,
      ok: false,
      headers: {},
      body: String(error?.stack || error?.message || error),
    })
  );
  process.exitCode = 1;
}

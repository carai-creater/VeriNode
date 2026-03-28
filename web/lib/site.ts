/** Public API / docs base (e.g. FastAPI origin). Trailing slash stripped. */
export function getApiOrigin(): string {
  const raw = process.env.NEXT_PUBLIC_API_BASE_URL?.trim();
  if (!raw) return "";
  return raw.replace(/\/$/, "");
}

export function docsUrl(): string {
  const o = getApiOrigin();
  if (o) return `${o}/docs`;
  return process.env.NEXT_PUBLIC_DOCS_PATH?.trim() || "/docs";
}

export function verifyEndpoint(): string {
  const o = getApiOrigin();
  if (o) return `${o}/verify`;
  return "https://YOUR_API_DOMAIN/verify";
}

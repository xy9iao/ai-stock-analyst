// Client-side file export helpers. The backend already stores reports as
// Markdown and hands the frontend everything it needs, so "export" is just a
// browser download — no server round-trip required.

/** Trigger a browser download of `text` as a file named `filename`. */
export function downloadText(filename: string, text: string, type = "text/markdown"): void {
  const blob = new Blob([text], { type });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = filename;
  anchor.click();
  URL.revokeObjectURL(url);
}

/** Turn a human title into a safe `<slug>.<ext>` filename. */
export function slugFilename(title: string, ext = "md"): string {
  const slug = title
    .trim()
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "");
  return `${slug || "export"}.${ext}`;
}

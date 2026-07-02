# Screenshot slots

The root `README.md` references four screenshots by these exact filenames. Capture each page at ~1280px browser width and drop the PNGs in this folder:

| Filename | Page | What to show |
| --- | --- | --- |
| `holdings.png` | `/holdings` | Portfolio table with live prices + gain/loss |
| `stock-detail.png` | `/stocks/<ticker>` | Price chart (pick a range with a nice curve) |
| `reports.png` | `/reports` | An open generated report (Markdown rendered) |
| `chat.png` | `/chat` | A short conversation with context toggles visible |

Tip: `docker compose up --build`, add a holding or two, generate one report, exchange a couple of chat messages — then screenshot. Avoid capturing anything you don't want public (e.g. real position sizes).

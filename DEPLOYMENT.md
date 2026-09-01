# Deploying Personal Knowledge Base MCP (free tier)

This guide deploys the whole stack for $0/month using free tiers:
- **Qdrant Cloud** — vector database (1GB free cluster)
- **Render** — backend (FastAPI), free web service
- **Vercel** — frontend (React/Vite), free hosting

## Known free-tier limitations (read this first)

- **Render free tier sleeps** after 15 minutes of no traffic. The first request after sleeping takes 30-60 seconds to wake up. Fine for a demo/portfolio; annoying for real daily use.
- **SQLite on Render's free tier is ephemeral** — every redeploy wipes `knowledge_base.db` (users, documents metadata). Qdrant Cloud data (the actual vectors) persists independently since it's a separate service. To fix this properly later: move to a free Postgres tier (e.g. Supabase's own free Postgres, or Render's free Postgres) — this is a `DATABASE_URL` change plus removing the SQLite-specific `connect_args` in `database.py`, not a rewrite.
- **No custom domain/email** included — password reset links use whatever `FRONTEND_URL` you configure.

## Step 1 — Qdrant Cloud

1. Sign up at [cloud.qdrant.io](https://cloud.qdrant.io) (free).
2. Create a cluster — note the **cluster URL** and generate an **API key**.
3. From the URL `https://xxxx.us-east.aws.cloud.qdrant.io:6333`, your `QDRANT_HOST` is `xxxx.us-east.aws.cloud.qdrant.io` and `QDRANT_PORT` is `6333`.

## Step 2 — Backend on Render

1. Push this repo to GitHub (public or private — Render's free tier supports both).
2. In the Render dashboard: **New → Blueprint**, point it at your repo. It will read `render.yaml` automatically.
3. Render will prompt for the env vars marked `sync: false` in `render.yaml`:
   - `QDRANT_HOST`, `QDRANT_API_KEY` — from Step 1
   - `FRONTEND_URL` — you can set this after Step 3 once you know your Vercel URL, then redeploy
4. Deploy. First build takes a few minutes (installs `sentence-transformers`, downloads the model on first run).
5. Confirm it's live: visit `https://your-service.onrender.com/health` — should return `{"status": "ok"}`.

## Step 3 — Frontend on Vercel

1. In the Vercel dashboard: **New Project**, import the same repo, set the **root directory** to `frontend/`.
2. Framework preset: Vite. Build command `npm run build`, output directory `dist` (Vercel usually detects this automatically).
3. Edit `frontend/vercel.json` in your repo, replacing `YOUR-RENDER-BACKEND-URL` with your actual Render URL from Step 2. Commit and push — Vercel redeploys automatically.
4. Deploy. Note your Vercel URL (e.g. `https://your-app.vercel.app`).

## Step 4 — Close the loop

1. Go back to Render → your service → Environment → set `FRONTEND_URL` to your Vercel URL from Step 3.
2. In Render → Environment → also update the CORS origins if you're not using the Vercel proxy approach (the `vercel.json` rewrite avoids needing this, since the browser only ever talks to your Vercel domain).
3. Redeploy the backend so the new `FRONTEND_URL` takes effect (used for password reset links).

## Step 5 — Verify end-to-end

1. Visit your Vercel URL.
2. Register a new account.
3. Upload a document (first upload may be slow — Render is waking up + downloading the embedding model on first use if it wasn't cached in the image).
4. Search.
5. Try forgot-password → confirm the reset link shown uses your production `FRONTEND_URL`.

## Running the MCP server against production data

The MCP server (`python -m mcp_server.server`) still runs on your own machine with `stdio` transport — it connects directly to whatever Qdrant/database your `.env` points at. Point your local `.env`'s `QDRANT_HOST`/`QDRANT_API_KEY` at the same Qdrant Cloud cluster your production backend uses, and it'll operate on the same real data.

If you want the MCP server itself remotely reachable (not just your local machine), FastMCP supports `transport="streamable-http"` instead of the default `stdio` — that's a small change to `mcp_server/server.py`'s `mcp.run()` call, deployable as its own Render web service. Not done here since it's a separate concern from getting the main app live; ask if you want this added.

## Scaling beyond free tier (when it's time)

| Limitation hit | Fix |
|---|---|
| Backend sleeping/cold starts annoying | Render paid tier (~$7/mo), always-on |
| Need real DB persistence | Migrate `DATABASE_URL` to Postgres (Render free Postgres, or Supabase) |
| High upload volume, embedding blocking | Real task queue (Celery/RQ + Redis) instead of `BackgroundTasks` — see Phase 4 notes in project history |
| Many concurrent users | Multiple Render instances behind their load balancer, Redis-backed rate limiting instead of in-memory `slowapi` |
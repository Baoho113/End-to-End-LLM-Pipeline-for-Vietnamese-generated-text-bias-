# BiasLens

A full-stack BiasLens application with a Next.js frontend and an Express/Prisma backend.

> **Current home page (`/`)** is the bias-analysis tool (Input → Detect → Mitigate → Evaluate), wired
> to the 14-category LoRA-fine-tuned Qwen2.5 severity model in `../src/training/` via a local FastAPI
> service — not the chat/auth flow described below, which is still present under `/auth`, `/dashboard`
> etc. but unlinked from the home page. Start the detection service before `npm run dev`, from the repo root:
>
> ```bash
> python -m uvicorn serve:app --reload --port 8000 --app-dir src/training
> ```
>
> Use `python -m uvicorn` rather than a bare `uvicorn` if this machine has more than one Python
> installation (e.g. Anaconda) -- a bare `uvicorn` on PATH can resolve to one that's missing
> `torch`/`transformers`/`peft`.
>
> See the root `README.md`'s "Getting Started: Bias Detection Module" for training/setup. Without it
> running, the Detect/Evaluate stages will show a "service unreachable" error.

## Project Structure

- `app/` — Next.js application pages and layouts
- `backend/` — Express API server with Prisma and PostgreSQL
- `components/` — Reusable React UI components
- `hooks/` — Custom React hooks
- `lib/` — Shared utilities and API client
- `styles/` — Global CSS and Tailwind configuration
- `types/` — TypeScript types

## Requirements

- Node.js 18+
- npm 10+
- PostgreSQL 14+ (backend)

## Setup

### 1. Install frontend dependencies

```bash
npm install
```

### 2. Install backend dependencies

```bash
cd backend
npm install
cd ..
```

### 3. Configure backend environment

Copy the example env file and update values as needed:

```bash
cd backend
copy .env.example .env
```

Then edit `backend/.env` to configure your database and JWT secret.

### 4. Run Prisma migrations

```bash
cd backend
npx prisma generate
npx prisma migrate dev --name init
cd ..
```

## Running the project

### Start the backend API

```bash
cd backend
npm run dev
```

The backend server should start on `http://localhost:3001`.

### Start the frontend

From the root project folder:

```bash
npm run dev
```

The frontend should start on `http://localhost:3000`.

## Useful commands

### Frontend

- `npm run dev` — start Next.js in development mode
- `npm run build` — build the frontend for production
- `npm run start` — start the production build
- `npm run lint` — run lint checks
- `npm run type-check` — run TypeScript type checking

### Backend

From `backend/`:

- `npm run dev` — start the backend API in development mode
- `npx prisma generate` — generate Prisma client
- `npx prisma migrate dev --name <name>` — create a new migration
- `npx prisma migrate deploy` — deploy migrations in production

## Notes

- Keep secrets out of source control by using `.env` and not committing it.
- The root `.gitignore` already excludes build output, environment files, and editor settings.

## Additional documentation

Check `docs/` for more implementation notes and setup guides.

# Staff Allocation Frontend (`reactapp`)

This package contains the React + Vite frontend for the Staff Allocation project. The app provides project planning views, staffing assignments, and timeline visualizations while proxying API traffic to the backend service.

## Prerequisites

- Node.js 18.x or newer (LTS recommended)
- npm 9.x or newer (bundled with Node.js)
- Access to the backend API (default proxy target: `http://localhost:8000`)

> **Tip:** Run `node -v` and `npm -v` to confirm the installed versions.

## Installation

1. Open a terminal at the repository root (`220372-AG-AISOFTDEV-Team-1-AINavigators`).
2. Change into the frontend directory:
   ```bash
   cd reactapp
   ```
3. Install dependencies:
   ```bash
   npm install
   ```

The command reads `package.json` and installs all runtime and development dependencies, including React, Vite, Tailwind, and form utilities.

## Running the App Locally

1. Start the backend API (if applicable) so the frontend proxy can forward `/api` requests.
2. In the `reactapp` directory, run:
   ```bash
   npm run dev
   ```
3. Open the URL shown in the terminal (defaults to `http://localhost:5173`). Vite provides hot module reloading, so changes in `src/` are reflected immediately.

### Environment Variables

Vite loads variables prefixed with `VITE_`. To override the API proxy target or provide additional configuration, create a `.env` file in `reactapp`:

```bash
cp .env.example .env    # if an example file exists
```

Add entries such as:

```bash
VITE_API_BASE_URL=http://localhost:8000
```

When `VITE_API_BASE_URL` is unset, the proxy falls back to `http://localhost:8000`.

## Other Scripts

- **Build production bundle:**
  ```bash
  npm run build
  ```
  Output goes to `dist/` and can be served by any static host.

- **Preview production build:**
  ```bash
  npm run preview
  ```
  Serves the `dist/` bundle locally at `http://localhost:4173`.

- **Run lint checks:**
  ```bash
  npm run lint
  ```
  Executes ESLint across `.ts` and `.tsx` files.

## Troubleshooting

- **Port already in use:** Pass `--port <number>` to `npm run dev` or terminate the conflicting process.
- **API calls fail:** Verify the backend is running, and confirm `VITE_API_BASE_URL` matches the backend URL.
- **Dependency errors:** Ensure `npm install` completes without errors, then restart the dev server.

For additional backend setup instructions, refer to the documentation in `Artifacts/backend/`.



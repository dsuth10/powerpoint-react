# TanStack Router + Vite Integration Troubleshooting Report

## Problem Summary (Historical)

### Symptoms
- Vite dev server outputs for every route file:
  - `Route file "... does not export any route piece. This is likely a mistake."`
- Internal server errors:
  - `The split value for the virtual route ".../main.tsx" was not found.`
  - 500 errors for `main.tsx`, `@vite/client`, `@react-refresh` in the browser.
- Browser shows a blank white page and 500 errors for main app files.

---

## What Was Tried

1. **Renamed all route files** to use the `.route.tsx` extension as required by TanStack Router v1.
2. **Updated all imports** in route files to use the new `.route.tsx` extension.
3. **Cleaned up all node_modules and lockfiles** in both the project root and `frontend/`.
4. **Reinstalled dependencies** in the `frontend/` directory.
5. **Restarted the Vite dev server** after all changes.

---

## Analysis: Why the Problem Persists

### 1. Plugin Still Not Recognizing Route Files
- The error message shows the *contents* of the file, not the filename, which means the plugin is reading the files but not parsing them as valid route pieces.
- The plugin expects each route file to:
  - End with `.route.tsx`
  - Export a default `Route` (or `RootRoute`) instance

### 2. Possible Causes
- **File naming or structure issue:**
  - There may still be a mismatch in file names, extensions, or directory structure.
- **File content issue:**
  - The plugin may require a specific export pattern or file structure.
- **Dependency or version mismatch:**
  - The versions of `@tanstack/react-router` and `@tanstack/router-plugin` may not be compatible, or there may be a corrupted install.
- **Vite/Plugin cache:**
  - Vite or the plugin may be caching old state, especially if there are hidden files or folders.

---

## Step-by-Step Plan to Fix (if using the Vite plugin)

### Step 1: Verify Route File Structure and Exports
- **Action:** List all files in `frontend/src/routes/` and subfolders.
  - Confirm every route file ends with `.route.tsx` (no `.tsx` or `.js` left).
  - Confirm there are no duplicate or backup files.
- **Action:** Open each route file and ensure it ends with:
  ```ts
  export default route
  ```
  or for the root:
  ```ts
  export default rootRoute
  ```
- **Action:** Ensure there are no syntax errors or typos in the route files.

### Step 2: Verify Dependency Versions
- **Action:** Check `frontend/package.json` for:
  - `@tanstack/react-router`
  - `@tanstack/router-plugin`
- **Action:** Ensure both are at the latest v1 versions and match your `versions.md` planning document.
- **Action:** If not, update them and run `npm install` again.

### Step 3: Clean All Caches and Artifacts
- **Action:** In the `frontend/` directory, delete:
  - `node_modules`
  - `.vite` (if present)
  - `dist` (if present)
  - `package-lock.json`
- **Action:** In the project root, delete:
  - `node_modules`
  - `package-lock.json`
- **Action:** Reinstall dependencies in `frontend/` only.

### Step 4: Restart Dev Server
- **Action:** In `frontend/`, run:
  ```sh
  npm run dev
  ```
- **Action:** Observe the terminal and browser for errors.

### Step 5: If Errors Persist
- **Action:** Double-check for:
  - Any stray or misnamed files in `src/routes/`
  - Any import paths that do not match the new file names
- **Action:** If all else fails, create a minimal new route file (e.g., `test.route.tsx`) with a simple default export and see if the plugin recognizes it.

---

## If You Need to Escalate

- **Provide:**
  - The full list of files in `frontend/src/routes/` and subfolders (with extensions)
  - The exact contents of one or two route files
  - The versions of `@tanstack/react-router` and `@tanstack/router-plugin` in `frontend/package.json`
  - Any new error messages after following the above steps

---

## Summary Table

| Area                | What to Check/Do                                    |
|---------------------|-----------------------------------------------------|
| File extensions     | All route files: `.route.tsx` only                  |
| File exports        | `export default route` (or `rootRoute`)             |
| Dependency versions | Latest v1, match `versions.md`                      |
| Clean install       | Remove all node_modules, lockfiles, caches          |
| Dev server output   | Should show no route export or code-split errors    |

---

## Current Project Note

The project has migrated away from the TanStack Router Vite plugin. We compose the route tree manually in `src/router.ts`. If you are not using the plugin, this troubleshooting guide does not apply.
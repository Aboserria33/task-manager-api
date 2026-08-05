# Task Manager API

A production-ready RESTful API for managing tasks, built with **Node.js**, **Express**, and **SQLite** (via `better-sqlite3`). All task data is persisted to a real SQLite database file on disk (`tasks.db`) — there is no in-memory storage, so data survives server restarts.

## Features

- Full CRUD operations for tasks (Create, Read, Update, Delete)
- Persistent SQLite storage (data survives restarts)
- Input validation (title required, non-empty, non-whitespace; status restricted to `pending`/`completed`)
- Consistent JSON error responses
- Global error handler for unexpected server errors
- Request logging for debugging

## Prerequisites

- **Node.js** version 14 or higher (developed/tested on Node.js v22)
- npm (comes bundled with Node.js)

## Installation

```bash
cd task-manager-api
npm install
```

This installs `express` (web framework) and `better-sqlite3` (synchronous, fast SQLite driver), plus `nodemon` as a dev dependency for auto-reload during development.

## Running the Server

Start in normal mode:

```bash
npm start
```

Start in development mode (auto-restarts on file changes via nodemon):

```bash
npm run dev
```

By default the server listens on **port 3000**. You can override this with the `PORT` environment variable:

```bash
PORT=4000 npm start
```

On startup, the server automatically:
1. Connects to (or creates) `tasks.db` in the project root.
2. Creates the `tasks` table if it doesn't already exist.
3. Starts listening for HTTP requests.

## Database Schema

Table: `tasks`

| Column        | Type    | Constraints                                              |
|---------------|---------|-----------------------------------------------------------|
| `id`          | INTEGER | PRIMARY KEY, AUTOINCREMENT                                 |
| `title`       | TEXT    | NOT NULL                                                    |
| `description` | TEXT    | Nullable                                                    |
| `status`      | TEXT    | NOT NULL, CHECK (`pending` or `completed`), default `pending` |
| `created_at`  | TEXT    | NOT NULL, default current timestamp                         |

## Project Structure

```
task-manager-api/
├── src/
│   ├── index.js                  # Entry point — sets up Express app, DB init, error handling
│   ├── db/
│   │   └── database.js           # SQLite connection + table initialization
│   ├── models/
│   │   └── taskModel.js          # Prepared SQL statements / data access layer
│   ├── controllers/
│   │   └── taskController.js     # Request handlers + validation logic
│   └── routes/
│       └── taskRoutes.js         # Express router mapping endpoints to controllers
├── package.json
├── .gitignore
├── tasks.db                       # SQLite database file (auto-created on first run)
└── README.md
```

## API Endpoints

### 1. Create a Task

`POST /tasks`

**Request body:**
```json
{
  "title": "Buy milk",
  "description": "Get 2% milk"
}
```

`description` and `status` are optional (`status` defaults to `"pending"`).

**Success response — `201 Created`:**
```json
{
  "id": 1,
  "title": "Buy milk",
  "description": "Get 2% milk",
  "status": "pending",
  "created_at": "2026-08-05 19:13:44"
}
```

**Validation error — `400 Bad Request`** (missing, empty, or whitespace-only title):
```json
{ "error": "Title is required and cannot be empty or only whitespace" }
```

**Validation error — `400 Bad Request`** (invalid status value):
```json
{ "error": "Status must be either 'pending' or 'completed'" }
```

---

### 2. Get All Tasks

`GET /tasks`

**Success response — `200 OK`:**
```json
[
  {
    "id": 1,
    "title": "Buy milk",
    "description": "Get 2% milk",
    "status": "pending",
    "created_at": "2026-08-05 19:13:44"
  }
]
```

---

### 3. Get a Single Task

`GET /tasks/:id`

**Success response — `200 OK`:**
```json
{
  "id": 1,
  "title": "Buy milk",
  "description": "Get 2% milk",
  "status": "pending",
  "created_at": "2026-08-05 19:13:44"
}
```

**Not found — `404 Not Found`:**
```json
{ "error": "Task not found" }
```

---

### 4. Update a Task (Partial Update)

`PUT /tasks/:id`

**Request body (any subset of fields):**
```json
{
  "status": "completed"
}
```

**Success response — `200 OK`:**
```json
{
  "id": 1,
  "title": "Buy milk",
  "description": "Get 2% milk",
  "status": "completed",
  "created_at": "2026-08-05 19:13:44"
}
```

**Validation error — `400 Bad Request`** (empty/whitespace title, or invalid status), same shapes as the create endpoint.

**Not found — `404 Not Found`:**
```json
{ "error": "Task not found" }
```

---

### 5. Delete a Task

`DELETE /tasks/:id`

**Success response — `204 No Content`** (empty body).

**Not found — `404 Not Found`:**
```json
{ "error": "Task not found" }
```

---

### Malformed Requests / Unexpected Errors

Any request body that isn't valid JSON returns:

**`400 Bad Request`:**
```json
{ "error": "Malformed JSON in request body" }
```

Any unhandled server-side failure returns:

**`500 Internal Server Error`:**
```json
{ "error": "Internal server error" }
```

All errors from unmatched routes:

**`404 Not Found`:**
```json
{ "error": "Route not found" }
```

## Testing with curl

Start the server first (`npm start`), then run these from another terminal.

**Create a task:**
```bash
curl -X POST http://localhost:3000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title":"Buy milk","description":"Get 2% milk"}'
```
Expected output: HTTP status `201`, and a JSON body containing the new task with an auto-generated `id`, the `title`/`description` you sent, `status` set to `"pending"`, and a `created_at` timestamp.

**Get all tasks:**
```bash
curl http://localhost:3000/tasks
```
Expected output: HTTP status `200` and a JSON array containing every task currently in the database.

**Get one task:**
```bash
curl http://localhost:3000/tasks/1
```
Expected output: HTTP status `200` with that task's JSON object, or status `404` with an `error` message if no task with that id exists.

**Update a task:**
```bash
curl -X PUT http://localhost:3000/tasks/1 \
  -H "Content-Type: application/json" \
  -d '{"status":"completed"}'
```
Expected output: HTTP status `200` with the full task object reflecting the updated `status` (other fields unchanged).

**Delete a task:**
```bash
curl -X DELETE http://localhost:3000/tasks/1
```
Expected output: HTTP status `204` with no response body. A subsequent `GET` on the same id returns `404`.

**Trigger a validation error:**
```bash
curl -X POST http://localhost:3000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title":"   "}'
```
Expected output: HTTP status `400` with `{"error":"Title is required and cannot be empty or only whitespace"}`.

## Testing with Postman

1. Create a new Collection named "Task Manager API".
2. Add a request for each endpoint above, using the same method, URL (`http://localhost:3000/tasks` or `http://localhost:3000/tasks/:id`), and JSON body where applicable.
3. In the **Headers** tab of POST/PUT requests, set `Content-Type: application/json`.
4. In the **Body** tab, select **raw** and **JSON**, then paste the example request bodies shown above.
5. Send each request and confirm the **status code** and **response body** match the expected values documented above.
6. For a quick end-to-end check, run the requests in this order: `POST` (create) → `GET all` → `GET by id` → `PUT` (update) → `GET by id` (confirm update) → `DELETE` → `GET by id` (confirm `404`).

## Notes and Assumptions

- SQLite is run in WAL (Write-Ahead Logging) mode for better concurrent read/write reliability; this produces auxiliary `tasks.db-wal` and `tasks.db-shm` files alongside `tasks.db`, which are normal and safe to ignore (they're excluded via `.gitignore` is not strictly required but the main `.db` file's journal siblings are transient).
- `title` values are trimmed of leading/trailing whitespace before being stored.
- On `PUT`, only the fields provided in the request body are updated; omitted fields keep their existing values.
- Malformed JSON request bodies are caught by the global error handler and return `400` rather than crashing the server or returning a generic `500`.
- The git repository was initialized locally only; nothing was pushed to any remote, per the task requirements.

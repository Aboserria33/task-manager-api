# Task Manager API

A production-ready RESTful API for managing daily tasks, built with **Python**, **Flask**, and **SQLite** (using Python's built-in `sqlite3` module — no native compilation required). Task data is persisted to a real SQLite database file (`tasks.db`) on disk, so data survives server restarts.

## Features

- Full CRUD operations for tasks (Create, Read, Update, Delete)
- Persistent SQLite storage (data survives restarts)
- Input validation (title required, non-empty, non-whitespace; status restricted to `pending`/`completed`)
- Consistent JSON error responses (400 / 404 / 500)
- Supports both `PUT` and `PATCH` for updates
- Global error handling for malformed JSON and unexpected errors

## Prerequisites

- **Python 3.8+** (tested on Python 3.12)
- **pip** (comes bundled with Python)

This project uses a virtual environment to keep dependencies isolated.

## Installation

### 1. Create a virtual environment

On Windows:
```bash
python -m venv venv
```

On macOS/Linux:
```bash
python3 -m venv venv
```

### 2. Activate the virtual environment

On Windows (Command Prompt):
```bash
venv\Scripts\activate
```

On Windows (PowerShell):
```powershell
venv\Scripts\Activate.ps1
```

On macOS/Linux:
```bash
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

This installs `Flask` (the web framework).

## Running the Server

```bash
python app.py
```

By default the server listens on **port 5000**. You can change this by editing the `app.run(host="0.0.0.0", port=5000)` line in `app.py`, or by setting the `PORT` environment variable.

On startup, the server automatically:
1. Connects to (or creates) `tasks.db` in the project root.
2. Creates the `tasks` table if it doesn't already exist.
3. Starts listening for HTTP requests.

## Database Schema

Table: `tasks`

| Column        | Type   | Constraints                                                            |
|---------------|--------|------------------------------------------------------------------------|
| `id`          | INTEGER | PRIMARY KEY, AUTOINCREMENT                                            |
| `title`       | TEXT   | NOT NULL                                                               |
| `description` | TEXT   | Nullable                                                               |
| `status`      | TEXT   | NOT NULL, CHECK (`pending`/`completed`), default `pending`             |
| `created_at`  | TEXT   | NOT NULL, default current timestamp                                    |

## Project Structure

```
task-manager-api/
├── app.py                  # Flask app — routes, validation, error handlers
├── database.py             # SQLite connection + data access layer
├── test_app.py             # End-to-end tests (Flask test client)
├── requirements.txt        # Python dependencies
├── .gitignore
├── tasks.db                # SQLite database file (auto-created on first run)
└── README.md
```

## API Endpoints

### 0. API Overview (Root)

`GET /`

Returns a helpful overview of the API and its endpoints. This is what you see when you open the base URL in a browser (instead of a 404).

**Success response — `200 OK`:**
```json
{
  "name": "Task Manager API",
  "message": "Welcome to the Task Manager API",
  "endpoints": {
    "POST /tasks": "Create a new task",
    "GET /tasks": "Retrieve all tasks",
    "GET /tasks/<id>": "Retrieve a task by id",
    "PUT /tasks/<id>": "Update a task",
    "DELETE /tasks/<id>": "Delete a task"
  }
}
```

---

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

**Validation error — `400 Bad Request`:**
```json
{ "error": "Title is required and cannot be empty or only whitespace" }
```

**Validation error — `400 Bad Request`** (invalid status):
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

`GET /tasks/<id>`

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

`PUT /tasks/<id>` or `PATCH /tasks/<id>`

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

**Validation error — `400 Bad Request`** (blank title or invalid status), same shapes as the create endpoint.

**Not found — `404 Not Found`:**
```json
{ "error": "Task not found" }
```

---

### 5. Delete a Task

`DELETE /tasks/<id>`

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

## Running the Tests

The project includes end-to-end tests using Flask's built-in test client. To run them:

```bash
python test_app.py
```

Expected output:
```
All tests passed!
```

The tests cover:
- Create → Get all → Get by id → Update (PUT & PATCH) → Delete → confirm 404
- Validation errors (missing/blank title, invalid status, malformed JSON)
- 404 responses for missing tasks and unknown routes

## Testing with curl

Start the server first (`python app.py`), then run these from another terminal.

**API overview (root):**
```bash
curl http://localhost:5000/
```
Expected output: HTTP status `200` and a JSON object listing the API name and all available endpoints.

**Create a task:**
```bash
curl -X POST http://localhost:5000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title":"Buy milk","description":"Get 2% milk"}'
```

**Get all tasks:**
```bash
curl http://localhost:5000/tasks
```

**Get one task:**
```bash
curl http://localhost:5000/tasks/1
```

**Update a task:**
```bash
curl -X PUT http://localhost:5000/tasks/1 \
  -H "Content-Type: application/json" \
  -d '{"status":"completed"}'
```

**Delete a task:**
```bash
curl -X DELETE http://localhost:5000/tasks/1
```

**Trigger a validation error:**
```bash
curl -X POST http://localhost:5000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title":"   "}'
```

## Testing with Postman

1. Create a new Collection named "Task Manager API".
2. Add a request for each endpoint above, using the same method, URL (`http://localhost:5000/tasks` or `http://localhost:5000/tasks/:id`), and JSON body where applicable.
3. In the **Headers** tab of POST/PUT requests, set `Content-Type: application/json`.
4. In the **Body** tab, select **raw** and **JSON**, then paste the example request bodies shown above.
5. Send each request and confirm the **status code** and **response body** match the expected values documented above.
6. For a quick end-to-end check, run the requests in this order: `POST` (create) → `GET all` → `GET by id` → `PUT` (update) → `GET by id` (confirm update) → `DELETE` → `GET by id` (confirm `404`).

## Notes and Assumptions

- `title` values are trimmed of leading/trailing whitespace before being stored.
- On `PUT`/`PATCH`, only the fields provided in the request body are updated; omitted fields keep their existing values.
- Malformed JSON request bodies return `400` rather than crashing the server.
- The SQLite database file is auto-created on first run and is ignored by git (via `.gitignore`).

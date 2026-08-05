"""
Task Manager API - Flask application.

Provides full CRUD operations for tasks with input validation
and consistent error handling.
"""

from flask import Flask, jsonify, request

import database

VALID_STATUSES = ("pending", "completed")


def is_blank(value):
    """Return True if value is not a string or is empty/whitespace-only."""
    return not isinstance(value, str) or value.strip() == ""


app = Flask(__name__)


@app.errorhandler(400)
def bad_request(error):
    return jsonify({"error": "Bad request"}), 400


@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Route not found"}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500


@app.route("/", methods=["GET"])
def index():
    """Return API overview so the root URL is informative."""
    return (
        jsonify(
            {
                "name": "Task Manager API",
                "message": "Welcome to the Task Manager API",
                "endpoints": {
                    "POST /tasks": "Create a new task",
                    "GET /tasks": "Retrieve all tasks",
                    "GET /tasks/<id>": "Retrieve a task by id",
                    "PUT /tasks/<id>": "Update a task",
                    "DELETE /tasks/<id>": "Delete a task",
                },
            }
        ),
        200,
    )


@app.route("/tasks", methods=["POST"])
def create_task():
    data = request.get_json(silent=True)
    if data is None:
        return jsonify({"error": "Malformed JSON in request body"}), 400

    title = data.get("title")
    if title is None or is_blank(title):
        return (
            jsonify(
                {"error": "Title is required and cannot be empty or only whitespace"}
            ),
            400,
        )

    status = data.get("status", "pending")
    if status not in VALID_STATUSES:
        return (
            jsonify({"error": "Status must be either 'pending' or 'completed'"}),
            400,
        )

    description = data.get("description")
    task = database.create_task(title.strip(), description, status)
    return jsonify(task), 201


@app.route("/tasks", methods=["GET"])
def get_all_tasks():
    tasks = database.get_all_tasks()
    return jsonify(tasks), 200


@app.route("/tasks/<int:task_id>", methods=["GET"])
def get_task(task_id):
    task = database.get_task_by_id(task_id)
    if task is None:
        return jsonify({"error": "Task not found"}), 404
    return jsonify(task), 200


@app.route("/tasks/<int:task_id>", methods=["PUT", "PATCH"])
def update_task(task_id):
    data = request.get_json(silent=True)
    if data is None:
        return jsonify({"error": "Malformed JSON in request body"}), 400

    task = database.get_task_by_id(task_id)
    if task is None:
        return jsonify({"error": "Task not found"}), 404

    fields = {}

    if "title" in data:
        title = data.get("title")
        if is_blank(title):
            return (
                jsonify(
                    {
                        "error": "Title is required and cannot be empty or only whitespace"
                    }
                ),
                400,
            )
        fields["title"] = title.strip()

    if "description" in data:
        fields["description"] = data.get("description")

    if "status" in data:
        status = data.get("status")
        if status not in VALID_STATUSES:
            return (
                jsonify({"error": "Status must be either 'pending' or 'completed'"}),
                400,
            )
        fields["status"] = status

    updated = database.update_task(task_id, fields)
    return jsonify(updated), 200


@app.route("/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    deleted = database.delete_task(task_id)
    if not deleted:
        return jsonify({"error": "Task not found"}), 404
    return "", 204


if __name__ == "__main__":
    database.init_db()
    # debug=True enables auto-reload during development.
    app.run(host="0.0.0.0", port=5000)

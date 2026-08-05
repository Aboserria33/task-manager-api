const { db } = require('../db/database');

// Prepared statements (compiled once, reused for performance).
const stmts = {
  insert: db.prepare(
    `INSERT INTO tasks (title, description, status) VALUES (?, ?, ?)`
  ),
  findAll: db.prepare(`SELECT * FROM tasks ORDER BY id ASC`),
  findById: db.prepare(`SELECT * FROM tasks WHERE id = ?`),
  deleteById: db.prepare(`DELETE FROM tasks WHERE id = ?`),
};

function createTask({ title, description, status }) {
  const info = stmts.insert.run(
    title,
    description ?? null,
    status || 'pending'
  );
  return stmts.findById.get(info.lastInsertRowid);
}

function getAllTasks() {
  return stmts.findAll.all();
}

function getTaskById(id) {
  return stmts.findById.get(id);
}

function updateTask(id, fields) {
  const existing = stmts.findById.get(id);
  if (!existing) return null;

  const title = fields.title !== undefined ? fields.title : existing.title;
  const description =
    fields.description !== undefined ? fields.description : existing.description;
  const status = fields.status !== undefined ? fields.status : existing.status;

  db.prepare(
    `UPDATE tasks SET title = ?, description = ?, status = ? WHERE id = ?`
  ).run(title, description, status, id);

  return stmts.findById.get(id);
}

function deleteTask(id) {
  const existing = stmts.findById.get(id);
  if (!existing) return false;
  stmts.deleteById.run(id);
  return true;
}

module.exports = {
  createTask,
  getAllTasks,
  getTaskById,
  updateTask,
  deleteTask,
};

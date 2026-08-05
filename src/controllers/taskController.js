const taskModel = require('../models/taskModel');

const VALID_STATUSES = ['pending', 'completed'];

function isBlank(value) {
  return typeof value !== 'string' || value.trim().length === 0;
}

function createTask(req, res, next) {
  try {
    const { title, description, status } = req.body || {};

    if (title === undefined || isBlank(title)) {
      return res
        .status(400)
        .json({ error: 'Title is required and cannot be empty or only whitespace' });
    }

    if (status !== undefined && !VALID_STATUSES.includes(status)) {
      return res
        .status(400)
        .json({ error: "Status must be either 'pending' or 'completed'" });
    }

    const task = taskModel.createTask({
      title: title.trim(),
      description: description !== undefined ? description : null,
      status: status || 'pending',
    });

    return res.status(201).json(task);
  } catch (err) {
    next(err);
  }
}

function getAllTasks(req, res, next) {
  try {
    const tasks = taskModel.getAllTasks();
    return res.status(200).json(tasks);
  } catch (err) {
    next(err);
  }
}

function getTaskById(req, res, next) {
  try {
    const id = Number(req.params.id);
    const task = taskModel.getTaskById(id);

    if (!task) {
      return res.status(404).json({ error: 'Task not found' });
    }

    return res.status(200).json(task);
  } catch (err) {
    next(err);
  }
}

function updateTask(req, res, next) {
  try {
    const id = Number(req.params.id);
    const { title, description, status } = req.body || {};

    const existing = taskModel.getTaskById(id);
    if (!existing) {
      return res.status(404).json({ error: 'Task not found' });
    }

    if (title !== undefined && isBlank(title)) {
      return res
        .status(400)
        .json({ error: 'Title is required and cannot be empty or only whitespace' });
    }

    if (status !== undefined && !VALID_STATUSES.includes(status)) {
      return res
        .status(400)
        .json({ error: "Status must be either 'pending' or 'completed'" });
    }

    const fields = {};
    if (title !== undefined) fields.title = title.trim();
    if (description !== undefined) fields.description = description;
    if (status !== undefined) fields.status = status;

    const updated = taskModel.updateTask(id, fields);
    return res.status(200).json(updated);
  } catch (err) {
    next(err);
  }
}

function deleteTask(req, res, next) {
  try {
    const id = Number(req.params.id);
    const deleted = taskModel.deleteTask(id);

    if (!deleted) {
      return res.status(404).json({ error: 'Task not found' });
    }

    return res.status(204).send();
  } catch (err) {
    next(err);
  }
}

module.exports = {
  createTask,
  getAllTasks,
  getTaskById,
  updateTask,
  deleteTask,
};

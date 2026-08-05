const express = require('express');
const { initDb } = require('./db/database');

// Initialize the database (creates tasks.db and the tasks table if needed)
// BEFORE requiring routes/controllers/models, since the model layer prepares
// SQL statements against the tasks table as soon as it is required.
initDb();

const taskRoutes = require('./routes/taskRoutes');

const app = express();
const PORT = process.env.PORT || 3000;

app.use(express.json());

// Basic request logging for debugging purposes.
app.use((req, res, next) => {
  console.log(`[${new Date().toISOString()}] ${req.method} ${req.url}`);
  next();
});

app.use('/tasks', taskRoutes);

// 404 handler for unknown routes.
app.use((req, res) => {
  res.status(404).json({ error: 'Route not found' });
});

// Global error handler — catches anything passed to next(err).
// eslint-disable-next-line no-unused-vars
app.use((err, req, res, next) => {
  // express.json() throws a SyntaxError on malformed JSON bodies —
  // that's a client error (400), not a server error (500).
  if (err.type === 'entity.parse.failed' || err instanceof SyntaxError) {
    console.error('Malformed JSON body:', err.message);
    return res.status(400).json({ error: 'Malformed JSON in request body' });
  }

  console.error('Unexpected error:', err);
  res.status(500).json({ error: 'Internal server error' });
});

app.listen(PORT, () => {
  console.log(`Task Manager API listening on http://localhost:${PORT}`);
});

module.exports = app;

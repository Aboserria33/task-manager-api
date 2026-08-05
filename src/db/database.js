const path = require('path');
const Database = require('better-sqlite3');

// The database file will be created automatically on disk in the project root.
const DB_PATH = path.join(__dirname, '..', '..', 'tasks.db');

const db = new Database(DB_PATH);

// Recommended pragmas for reliability/performance on a single-file SQLite DB.
db.pragma('journal_mode = WAL');
db.pragma('foreign_keys = ON');

function initDb() {
  db.exec(`
    CREATE TABLE IF NOT EXISTS tasks (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      title TEXT NOT NULL,
      description TEXT,
      status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'completed')),
      created_at TEXT NOT NULL DEFAULT (datetime('now'))
    );
  `);
}

module.exports = { db, initDb, DB_PATH };

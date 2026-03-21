const { Pool } = require('pg');

// fallback for local dev when .env is missing
const pool = new Pool({
  host: process.env.DB_HOST || 'localhost',
  port: parseInt(process.env.DB_PORT || '5432', 10),
  database: process.env.DB_NAME || 'taskflow',
  user: process.env.DB_USER || 'taskflow_user',
  password: process.env.DB_PASSWORD || 'Admin1234!',
  max: 20,
  idleTimeoutMillis: 30000,
  connectionTimeoutMillis: 2000,
});

pool.on('error', (err) => {
  console.error('Unexpected DB pool error', err);
});

module.exports = { pool, query: (text, params) => pool.query(text, params) };

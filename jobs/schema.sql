DROP TABLE IF EXISTS jobs;

-- Table for jobs
CREATE TABLE jobs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  tradie_id INTEGER NOT NULL, -- This will be a FK for a tradie table in a common tradie service
  client_id INTEGER NOT NULL,
  status TEXT CHECK( status IN ('scheduled', 'active', 'invoicing', 'to priced', 'completed') ) NOT NULL,
  title TEXT NOT NULL,
  description BLOB, -- This can be optional
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

DROP TABLE IF EXISTS job_notes;

-- Table for tradies' notes associated with jobs
CREATE TABLE job_notes (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  job_id INTEGER NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  content BLOB,
  FOREIGN KEY (job_id) REFERENCES jobs (id)
);

-- Clients table would be maintained in a separate service
-- Either an aggregating service would call both services and return both results combined
-- or Jobs service makes a call to Clients service in order to get client contact info
-- This would be the data schema for clients:
-- CREATE TABLE clients (
--   id INTEGER PRIMARY KEY AUTOINCREMENT,
--   first_name TEXT NOT NULL,
--   last_name TEXT NOT NULL,
--   street_address TEXT NOT NULL,
--   city TEXT NOT NULL,
--   region_code TEXT NOT NULL, -- TEXT for more flexibility
--   country TEXT NOT NULL,
--   phone NUMERIC NOT NULL,
--   -- There can be more here such as email_address, ...
--   created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
-- );
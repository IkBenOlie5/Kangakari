create EXTENSION IF NOT EXISTS "uuid-ossp";
create TABLE IF NOT EXISTS errors (
  error_id UUID DEFAULT uuid_generate_v4(),
  message TEXT NOT NULL,
  timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

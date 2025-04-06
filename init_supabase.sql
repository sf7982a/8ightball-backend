// /backend/init_supabase.sql
CREATE TABLE accounts (
  id UUID PRIMARY KEY,
  name TEXT,
  subscription_plan TEXT DEFAULT 'free',
  created_at TIMESTAMP DEFAULT now()
);

CREATE TABLE users (
  id UUID PRIMARY KEY,
  account_id UUID REFERENCES accounts(id),
  email TEXT UNIQUE,
  role TEXT,
  password_hash TEXT
);

CREATE TABLE inventory_items (
  id UUID PRIMARY KEY,
  account_id UUID REFERENCES accounts(id),
  rfid_tag TEXT UNIQUE,
  name TEXT,
  volume_ml INTEGER,
  added_by UUID REFERENCES users(id),
  added_at TIMESTAMP DEFAULT now()
);

CREATE TABLE rfid_scans (
  id UUID PRIMARY KEY,
  rfid_tag TEXT,
  scanned_at TIMESTAMP DEFAULT now(),
  scanned_by UUID REFERENCES users(id)
);

ALTER TABLE accounts ADD COLUMN stripe_customer_id TEXT;
ALTER TABLE accounts ADD COLUMN subscription_plan TEXT DEFAULT 'free';
-- 1) create uuid extension (if not yet)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 2) admins, users, downloads (replicated tables)
CREATE TABLE IF NOT EXISTS admins (
    admin_id SERIAL PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    password_hash TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS users (
    institute_id VARCHAR(64) PRIMARY KEY,
    institute_mail VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    nature VARCHAR(32) NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- downloads will reference user and refer to book by UUID (global id)
CREATE TABLE IF NOT EXISTS downloads (
    download_id SERIAL PRIMARY KEY,
    institute_id VARCHAR(64) REFERENCES users(institute_id) ON DELETE CASCADE,
    book_uuid UUID NOT NULL,
    downloaded_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- 3) Fragment tables (present on both sites; owner site will insert into its fragment)
-- Both fragments have same structure and include a global uuid column
CREATE TABLE IF NOT EXISTS books_cse (
    id SERIAL PRIMARY KEY,
    book_uuid UUID NOT NULL DEFAULT uuid_generate_v4(),
    book_name TEXT NOT NULL,
    authors TEXT,
    genre TEXT,
    branch VARCHAR(64) DEFAULT 'CSE',
    pdf_data BYTEA,
    uploaded_by VARCHAR(255),
    uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

CREATE TABLE IF NOT EXISTS books_eee (
    id SERIAL PRIMARY KEY,
    book_uuid UUID NOT NULL DEFAULT uuid_generate_v4(),
    book_name TEXT NOT NULL,
    authors TEXT,
    genre TEXT,
    branch VARCHAR(64) DEFAULT 'EEE',
    pdf_data BYTEA,
    uploaded_by VARCHAR(255),
    uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- 4) Useful indexes
CREATE INDEX IF NOT EXISTS idx_books_cse_name ON books_cse (lower(book_name));
CREATE INDEX IF NOT EXISTS idx_books_eee_name ON books_eee (lower(book_name));
CREATE INDEX IF NOT EXISTS idx_users_mail ON users (lower(institute_mail));
CREATE INDEX IF NOT EXISTS idx_downloads_book_uuid ON downloads (book_uuid);

-- 5) Make replica identity FULL for safe replication of updates/deletes
ALTER TABLE users REPLICA IDENTITY FULL;
ALTER TABLE admins REPLICA IDENTITY FULL;
ALTER TABLE downloads REPLICA IDENTITY FULL;
ALTER TABLE books_cse REPLICA IDENTITY FULL;
ALTER TABLE books_eee REPLICA IDENTITY FULL;

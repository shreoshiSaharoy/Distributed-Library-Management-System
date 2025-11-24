# Distributed-Library-Management-System

This is project is a prototype of a real-time large scale open web library
It mainly demonstrates the concepts of distributed databaes namely, replication and fragmentation.

This Library portal mainly has the following features:
1. User Registration and Login
2. Serach option for users to search for the book they would like to refer
3. Download option to save it in local system
4. Admin Login
5. Users added only by the Admin
6. Book PDFs uploaded only by the Admin
7. User-friendly and easy to read web pages.

## System Requirements 
1. Frameworks used: Postgresql (version 14), Djaango
2. Operating System: Linux-Ubuntu (2 systems)
3. Python packages: django, pycopgy2-binary

## Postgres Configurations

Make necessary changes in the following files so that the 2 systems can access each other's DBs.

* sudo nano /etc/postgresql/14/main/postgresql.conf
* sudo nano /etc/postgresql/14/main/pg_hba.conf

## Project specific DB commands (in both systems)

Enter into the psotgres shell using the command:
* sudo -u postgres psql

In the postgres shell, run the following:
1. CREATE ROLE replica WITH REPLICATION LOGIN PASSWORD '<your replica user password>';
2. CREATE DATABASE librarydb;
3. exit the shell

Now run the command:
* sudo -u postgres psql -d librarydb -f schema.sql

Then connect to the librarydb databse and execute the following commands:

### At Site 1:

1. CREATE PUBLICATION replicated_pub FOR TABLE admins, users, downloads;

2. CREATE PUBLICATION books_cse_pub FOR TABLE books_cse;

3. CREATE SUBSCRIPTION sub_from_site2
    CONNECTION 'host=<site2_IP> port=5432 dbname=librarydb user=replica password=<your replica user password>'
    PUBLICATION replicated_pub, books_eee_pub;

4. CREATE OR REPLACE VIEW books AS
    SELECT id AS local_id, book_uuid, book_name, authors, genre, branch, pdf_data, uploaded_by, uploaded_at, 'CSE' AS fragment
    FROM books_cse
    UNION ALL
    SELECT id AS local_id, book_uuid, book_name, authors, genre, branch, pdf_data, uploaded_by, uploaded_at, 'EEE' AS fragment
    FROM books_eee;

5.  CREATE OR REPLACE FUNCTION books_view_insert()
    RETURNS trigger LANGUAGE plpgsql AS $$
    BEGIN
        IF NEW.branch = 'CSE' THEN
            INSERT INTO books_cse (book_name, authors, genre, branch, pdf_data, uploaded_by, uploaded_at)
            VALUES (NEW.book_name, NEW.authors, NEW.genre, NEW.branch, NEW.pdf_data, NEW.uploaded_by, COALESCE(NEW.uploaded_at, now()));
            RETURN NEW;
        ELSIF NEW.branch = 'EEE' THEN
            INSERT INTO books_eee (book_name, authors, genre, branch, pdf_data, uploaded_by, uploaded_at)
            VALUES (NEW.book_name, NEW.authors, NEW.genre, NEW.branch, NEW.pdf_data, NEW.uploaded_by, COALESCE(NEW.uploaded_at, now()));
            RETURN NEW;
        ELSE
            -- If branch unknown, insert into a default fragment or raise
            RAISE EXCEPTION 'Unknown branch "%"', NEW.branch;
        END IF;
    END;
    $$;
6. CREATE TRIGGER trg_books_view_insert
    INSTEAD OF INSERT ON books
    FOR EACH ROW EXECUTE FUNCTION books_view_insert();

7. SELECT pg_get_serial_sequence('books_cse','book_id') AS seq_name;
[Find the sequence name for books_cse.book_id, suppose it returns: public.books_cse_book_id_seq]

8. GRANT USAGE, SELECT ON SEQUENCE public.books_cse_book_id_seq TO "replica";

9. GRANT INSERT ON TABLE public.books_cse TO "replica";

10. GRANT UPDATE, DELETE ON TABLE public.books_cse TO "replica";

11. SELECT pg_get_serial_sequence('downloads','download_id') AS seq_name;
[if sequence is public.downloads_download_id_seq]

12. GRANT USAGE, SELECT ON SEQUENCE public.downloads_download_id_seq TO "replica";

13. GRANT INSERT ON TABLE public.downloads TO "replica";

14. GRANT UPDATE, DELETE ON TABLE public.downloads TO "replica";

### At Site 2:

1. CREATE PUBLICATION replicated_pub FOR TABLE admins, users, downloads;

2. CREATE PUBLICATION books_eee_pub FOR TABLE books_eee;

3. CREATE SUBSCRIPTION sub_from_site1
   CONNECTION 'host=<site1_IP> port=5432 dbname=librarydb user=replica password=YourReplicaPass'
   PUBLICATION replicated_pub, books_cse_pub;

4.  CREATE OR REPLACE VIEW books AS
    SELECT id AS local_id, book_uuid, book_name, authors, genre, branch, pdf_data, uploaded_by, uploaded_at, 'CSE' AS fragment
    FROM books_cse
    UNION ALL
    SELECT id AS local_id, book_uuid, book_name, authors, genre, branch, pdf_data, uploaded_by, uploaded_at, 'EEE' AS fragment
    FROM books_eee;

5.  CREATE OR REPLACE FUNCTION books_view_insert()
    RETURNS trigger LANGUAGE plpgsql AS $$
    BEGIN
        IF NEW.branch = 'CSE' THEN
            INSERT INTO books_cse (book_name, authors, genre, branch, pdf_data, uploaded_by, uploaded_at)
            VALUES (NEW.book_name, NEW.authors, NEW.genre, NEW.branch, NEW.pdf_data, NEW.uploaded_by, COALESCE(NEW.uploaded_at, now()));
            RETURN NEW;
        ELSIF NEW.branch = 'EEE' THEN
            INSERT INTO books_eee (book_name, authors, genre, branch, pdf_data, uploaded_by, uploaded_at)
            VALUES (NEW.book_name, NEW.authors, NEW.genre, NEW.branch, NEW.pdf_data, NEW.uploaded_by, COALESCE(NEW.uploaded_at, now()));
            RETURN NEW;
        ELSE
            -- If branch unknown, insert into a default fragment or raise
            RAISE EXCEPTION 'Unknown branch "%"', NEW.branch;
        END IF;
    END;
    $$;

6. CREATE TRIGGER trg_books_view_insert
    INSTEAD OF INSERT ON books
    FOR EACH ROW EXECUTE FUNCTION books_view_insert();

7. SELECT pg_get_serial_sequence('books_eee','book_id') AS seq_name; 
[Find the sequence name for books_eee.book_id, Suppose it returns: public.books_eee_book_id_seq]

8. GRANT USAGE, SELECT ON SEQUENCE public.books_eee_book_id_seq TO "replica";

9. GRANT INSERT ON TABLE public.books_eee TO "replica";

10. GRANT UPDATE, DELETE ON TABLE public.books_eee TO "replica";

11. SELECT pg_get_serial_sequence('downloads','download_id') AS seq_name;
[if sequence is public.downloads_download_id_seq]

12. GRANT USAGE, SELECT ON SEQUENCE public.downloads_download_id_seq TO "replica";

13. GRANT INSERT ON TABLE public.downloads TO "replica";

14. GRANT UPDATE, DELETE ON TABLE public.downloads TO "replica";


#### * Either at site1 or site2(only 1) run the sql query - INSERT INTO admins (email, name, password_hash) VALUES ('<your admin email>', 'Admin', crypt('<your admin password>', gen_salt('bf'))) ON CONFLICT (email) DO NOTHING;









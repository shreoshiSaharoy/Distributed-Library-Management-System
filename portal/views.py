from django.shortcuts import render, redirect
from django.http import HttpResponse, Http404
from django.db import connection
from .models import *
from .forms import RegisterForm, LoginForm, AdminLoginForm, UploadBookForm
from django.contrib import messages
import psycopg2
from functools import wraps
from django.db import connection
import uuid

def home(request):
    return render(request, 'home.html')

# Helper: check password against postgres crypt hash
def check_pg_crypt(password, stored_hash):
    with connection.cursor() as cur:
        cur.execute("SELECT (crypt(%s, %s) = %s) AS ok", [password, stored_hash, stored_hash])
        return cur.fetchone()[0]

def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            # hash using pgcrypto on DB
            with connection.cursor() as cur:
                cur.execute(
                    "INSERT INTO users (institute_id, institute_mail, name, nature, password_hash) VALUES (%s,%s,%s,%s,crypt(%s, gen_salt('bf')))",
                    [data['institute_id'], data['institute_mail'], data['name'], data['nature'], data['password']]
                )
            return redirect('login')
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})

def login_view(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            mail = form.cleaned_data['institute_mail']
            pwd = form.cleaned_data['password']
            with connection.cursor() as cur:
                cur.execute("SELECT institute_id, password_hash FROM users WHERE institute_mail = %s", [mail])
                row = cur.fetchone()
                if row and row[0] and row[1]:
                    ok = False
                    cur.execute("SELECT (crypt(%s, %s) = %s) AS ok", [pwd, row[1], row[1]])
                    ok = cur.fetchone()[0]
                    if ok:
                        request.session['user_id'] = row[0]
                        return redirect('search')
            messages.error(request, "Invalid credentials")
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})

def admin_login(request):
    if request.method == "POST":
        form = AdminLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            pwd = form.cleaned_data['password']
            with connection.cursor() as cur:
                cur.execute("SELECT admin_id, password_hash FROM admins WHERE email = %s", [email])
                row = cur.fetchone()
                if row:
                    cur.execute("SELECT (crypt(%s, %s) = %s) AS ok", [pwd, row[1], row[1]])
                    if cur.fetchone()[0]:
                        request.session['admin_email'] = email
                        return redirect('admin_dashboard')
            messages.error(request, "Invalid admin credentials")
    else:
        form = AdminLoginForm()
    return render(request, 'admin_login.html', {'form': form})

def admin_dashboard(request):
    if not request.session.get('admin_email'):
        return redirect('admin_login')
    # Admin can view users
    with connection.cursor() as cur:
        cur.execute("SELECT institute_id, institute_mail, name, nature, created_at FROM users ORDER BY created_at DESC")
        users = cur.fetchall()
    return render(request, 'admin_dashboard.html', {'users': users, 'admin': request.session['admin_email']})

def admin_add_user(request):
    if not request.session.get('admin_email'):
        return redirect('admin_login')
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            d = form.cleaned_data
            with connection.cursor() as cur:
                cur.execute("INSERT INTO users (institute_id, institute_mail, name, nature, password_hash) VALUES (%s,%s,%s,%s,crypt(%s, gen_salt('bf')))",
                            [d['institute_id'], d['institute_mail'], d['name'], d['nature'], d['password']])
            return redirect('admin_dashboard')
    else:
        form = RegisterForm()
    return render(request, 'admin_add_user.html', {'form': form})

def admin_remove_user(request, institute_id):
    if not request.session.get('admin_email'):
        return redirect('admin_login')
    with connection.cursor() as cur:
        cur.execute("DELETE FROM users WHERE institute_id = %s", [institute_id])
    return redirect('admin_dashboard')

def admin_required(view_func):
    """
    Decorator: only allow access if admin session present.
    If not present, redirect to admin login page.
    """
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not request.session.get('admin_email'):
            return redirect('admin_login')
        return view_func(request, *args, **kwargs)
    return _wrapped


@admin_required
def upload_book(request):
    """
    Admin-only: upload a book PDF into books table.
    Always returns an HttpResponse (render or redirect).
    """
    if request.method == "POST":
        form = UploadBookForm(request.POST, request.FILES)
        if not form.is_valid():
            # Render same page with errors
            messages.error(request, "Please fix the errors below.")
            return render(request, 'upload_book.html', {'form': form})

        # Ensure file field exists
        uploaded_file = request.FILES.get('pdf')
        if not uploaded_file:
            messages.error(request, "No PDF file was uploaded. Please attach a PDF.")
            return render(request, 'upload_book.html', {'form': form})

        # Read bytes safely
        try:
            pdf_bytes = uploaded_file.read()
        except Exception as e:
            messages.error(request, f"Failed to read uploaded file: {e}")
            return render(request, 'upload_book.html', {'form': form})

        # Insert into DB using parameterized query; psycopg2.Binary to handle bytea
        try:
            with connection.cursor() as cur:
                cur.execute("""
                    INSERT INTO books (book_name, authors, genre, branch, pdf_data, uploaded_by)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, [
                    form.cleaned_data['book_name'],
                    form.cleaned_data.get('authors') or None,
                    form.cleaned_data.get('genre') or None,
                    form.cleaned_data['branch'],
                    psycopg2.Binary(pdf_bytes),
                    request.session.get('admin_email')
                ])
        except Exception as e:
            # DB error: display message and render page again
            messages.error(request, f"Database error while saving book: {e}")
            return render(request, 'upload_book.html', {'form': form})

        # Success: show success page or redirect
        messages.success(request, "Book uploaded successfully.")
        return render(request, 'upload_success.html')

    # GET -> show form
    form = UploadBookForm()
    return render(request, 'upload_book.html', {'form': form})

# ---- search view: query both fragments and return rows with book_uuid as first column ----
def search(request):
    q = (request.GET.get('book_name') or '').strip()
    branch = (request.GET.get('branch') or '').strip()

    # Build SQL parts
    where_clauses = []
    params = []

    # Book name is compulsory on frontend but still handle empty safely
    if q:
        where_clauses.append("lower(book_name) LIKE %s")
        params.append(f"%{q.lower()}%")
    else:
        # if no query provided, return empty results (you can change to show recent uploads)
        return render(request, 'search.html', {'books': [], 'query': q})

    if branch:
        where_clauses.append("branch = %s")
        params.append(branch)

    # Build WHERE clause
    where_sql = " AND ".join(where_clauses) if where_clauses else "TRUE"

    # Query both fragment tables (UNION ALL)
    sql = f"""
        SELECT book_uuid, book_name, authors, genre, branch, uploaded_by, uploaded_at
        FROM books_cse
        WHERE {where_sql}
        UNION ALL
        SELECT book_uuid, book_name, authors, genre, branch, uploaded_by, uploaded_at
        FROM books_eee
        WHERE {where_sql}
        ORDER BY uploaded_at DESC
        LIMIT 200
    """

    # The params must be duplicated for the UNION (first SELECT then second SELECT)
    params_union = params + params

    with connection.cursor() as cur:
        cur.execute(sql, params_union)
        rows = cur.fetchall()

    # rows are tuples: (book_uuid (uuid.UUID), book_name, authors, genre, branch, uploaded_by, uploaded_at)
    return render(request, 'search.html', {'books': rows, 'query': q})


# ---- download view: accept UUID and use it to fetch pdf_data and log download ----
def download_book(request, book_uuid):
    """
    book_uuid is provided by the URL as uuid.UUID (Django does this for <uuid:...>).
    This view:
     - ensures the user is logged in (session 'user_id')
     - fetches pdf_data, book_name by book_uuid (parameterized)
     - logs the download by inserting into downloads(institute_id, book_uuid)
     - returns PDF attachment
    """
    # require user session
    user_id = request.session.get('user_id')
    if not user_id:
        messages.error(request, "Please log in to download books.")
        return redirect('login')

    # ensure book_uuid is a uuid.UUID instance (it should be), else try to parse
    if not isinstance(book_uuid, uuid.UUID):
        try:
            book_uuid = uuid.UUID(str(book_uuid))
        except Exception:
            raise Http404("Invalid book identifier.")

    try:
        with connection.cursor() as cur:
            # fetch pdf and title by UUID
            cur.execute(
                "SELECT pdf_data, book_name FROM books_cse WHERE book_uuid = %s UNION ALL "
                "SELECT pdf_data, book_name FROM books_eee WHERE book_uuid = %s",
                [str(book_uuid), str(book_uuid)]
            )
            row = cur.fetchone()
            if not row:
                raise Http404("Book not found.")

            pdf_data, book_name = row[0], row[1]

            # Log download into downloads table (store the UUID)
            cur.execute(
                "INSERT INTO downloads (institute_id, book_uuid) VALUES (%s, %s)",
                [user_id, str(book_uuid)]
            )

    except Http404:
        raise
    except Exception as e:
        # DB error: show friendly message and redirect back
        messages.error(request, f"Database error while recording download: {e}")
        return redirect('search')

    # return the pdf attachment
    response = HttpResponse(bytes(pdf_data), content_type='application/pdf')
    safe_name = (book_name or "book").replace('"', "'").strip()
    response['Content-Disposition'] = f'attachment; filename="{safe_name}.pdf"'
    return response

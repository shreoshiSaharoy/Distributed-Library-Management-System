from django.db import models

class Admin(models.Model):
    admin_id = models.AutoField(primary_key=True)
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255)
    password_hash = models.TextField()
    class Meta:
        db_table = 'admins'
        managed = False

class User(models.Model):
    institute_id = models.CharField(max_length=64, primary_key=True)
    institute_mail = models.EmailField(unique=True)
    name = models.CharField(max_length=255)
    nature = models.CharField(max_length=32)
    password_hash = models.TextField()
    created_at = models.DateTimeField()
    class Meta:
        db_table = 'users'
        managed = False

class BookCSE(models.Model):
    id = models.AutoField(primary_key=True)
    book_uuid = models.UUIDField()
    book_name = models.TextField()
    authors = models.TextField(null=True)
    genre = models.TextField(null=True)
    branch = models.CharField(max_length=64)
    pdf_data = models.BinaryField()
    uploaded_by = models.CharField(max_length=255, null=True)
    uploaded_at = models.DateTimeField()
    class Meta:
        db_table = 'books_cse'
        managed = False

class BookEEE(models.Model):
    id = models.AutoField(primary_key=True)
    book_uuid = models.UUIDField()
    book_name = models.TextField()
    authors = models.TextField(null=True)
    genre = models.TextField(null=True)
    branch = models.CharField(max_length=64)
    pdf_data = models.BinaryField()
    uploaded_by = models.CharField(max_length=255, null=True)
    uploaded_at = models.DateTimeField()
    class Meta:
        db_table = 'books_eee'
        managed = False

class BookView(models.Model):
    local_id = models.IntegerField()
    book_uuid = models.UUIDField(primary_key=True)
    book_name = models.TextField()
    authors = models.TextField(null=True)
    genre = models.TextField(null=True)
    branch = models.CharField(max_length=64)
    pdf_data = models.BinaryField()
    uploaded_by = models.CharField(max_length=255, null=True)
    uploaded_at = models.DateTimeField()
    fragment = models.CharField(max_length=16)
    class Meta:
        db_table = 'books'   # maps to the view
        managed = False

import time
from django.db import connection

class SQLLogMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Clear previous queries
        connection.queries_log.clear() if hasattr(connection, 'queries_log') else None
        response = self.get_response(request)
        # Print all SQL executed during the request
        for q in connection.queries:
            print("SQL EXECUTED:", q.get('sql'))
        return response

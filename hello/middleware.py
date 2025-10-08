# hello/middleware.py
import logging
import time

logger = logging.getLogger("django.server")

class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start = time.perf_counter()
        response = self.get_response(request)
        duration_ms = (time.perf_counter() - start) * 1000

        logger.info(
            "%s %s -> %s %d %.2fms",
            request.method,
            request.get_full_path(),
            request.META.get("REMOTE_ADDR", "-"),
            response.status_code,
            duration_ms,
        )
        return response

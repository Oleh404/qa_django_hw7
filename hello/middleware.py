import logging

class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.logger = logging.getLogger("http")

    def __call__(self, request):
        response = self.get_response(request)
        status = getattr(response, "status_code", 500)
        self.logger.info("%s %s -> %s", request.method, request.get_full_path(), status)
        return response

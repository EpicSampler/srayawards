from django.shortcuts import render

class CustomErrorMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_exception(self, request, exception):
        return None

    def process_template_response(self, request, response):
        if response.status_code == 404:
            response = render(request, '404.html', status=404)
        elif response.status_code == 500:
            response = render(request, '500.html', status=500)
        return response

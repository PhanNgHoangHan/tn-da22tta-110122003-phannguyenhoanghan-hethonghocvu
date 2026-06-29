from django.utils.cache import add_never_cache_headers

class PreventBackCacheMiddleware:
    """
    Middleware to prevent the browser from caching pages for authenticated users.
    When a logged-out user clicks the back button on the browser, they will be
    forced to request the page from the server, which redirects them to the login page.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if request.user.is_authenticated:
            add_never_cache_headers(response)
        return response

from rest_framework.throttling import SimpleRateThrottle


class PhloxUserRateThrottle(SimpleRateThrottle):
    """
    Limits the rate of API calls that may be made by a given user.

    The user id will be used as a unique cache key if the user is
    authenticated.  For anonymous requests, the IP address of the request will
    be used.
    """

    scope = "user"

    def get_cache_key(self, request, view):
        if request.user and request.user.is_authenticated:
            ident = request.user.id
        else:
            ident = self.get_ident(request)

        return self.cache_format % {"scope": self.scope, "ident": ident}


class OneSecondUserRateThrottle(PhloxUserRateThrottle):
    rate = "1/second"  # Set rate limit to 1 request per 2 second

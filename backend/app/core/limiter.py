try:
    from slowapi import Limiter
    from app.api.middlewares.security import user_or_ip_key_func
    limiter = Limiter(key_func=user_or_ip_key_func)
except ImportError:
    class DummyLimiter:
        def limit(self, *args, **kwargs):
            def decorator(func):
                return func
            return decorator
    limiter = DummyLimiter()

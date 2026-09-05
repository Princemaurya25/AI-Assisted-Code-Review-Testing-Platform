try:
    from slowapi import Limiter
    from slowapi.util import get_remote_address
    from app.core.config import settings

    limiter = Limiter(key_func=get_remote_address, default_limits=[f"{settings.RATE_LIMIT_PER_MINUTE}/minute"])
except ImportError:
    class DummyLimiter:
        def limit(self, limit_value):
            def decorator(func):
                return func
            return decorator

    limiter = DummyLimiter()

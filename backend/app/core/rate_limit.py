from slowapi import Limiter
from slowapi.util import get_remote_address

# In-memory storage — fine for a single dev/staging process. A
# multi-worker or multi-instance production deployment needs a shared
# backing store (e.g. Redis) instead, since in-memory limits are
# per-process and wouldn't be enforced consistently across workers.
limiter = Limiter(key_func=get_remote_address)
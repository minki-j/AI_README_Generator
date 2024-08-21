from fasthtml.common import *

from .authentication import app as auth_app, route as auth_route
from .initialization import app as init_app, route as init_route

mounts_for_routes = [
    Mount(init_route, init_app),
    Mount(auth_route, auth_app),
]

from mayan.settings.development import *
# Debug Toolbar
# from mayan.settings.development.ddt import *

INSTALLED_APPS += (
    'botech.edms',
)

if DEBUG:
    # See https://django-debug-toolbar.readthedocs.io/en/latest/installation.html#configure-internal-ips
    # Set internal ips so that they work inside of a container as intended.
    import socket  # only if you haven't already imported this
    hostname, _, ips = socket.gethostbyname_ex(socket.gethostname())
    INTERNAL_IPS = [ip[: ip.rfind(".")] + ".1" for ip in ips] + ["127.0.0.1", "10.0.2.2"]

# Debug toolbar configuration
#
# So far the only working way is to use the toolbar in one of the admin views
# and find the requests via the history panel.
RENDER_PANELS = False
RESULTS_CACHE_SIZE = 300
SHOW_COLLAPSED = True

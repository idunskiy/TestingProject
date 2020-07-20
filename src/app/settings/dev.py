from app.settings.base import * # noqa
from app.settings.components.database import * # noqa
from app.settings.components.dev_tools import * # noqa

DEBUG = True

STATIC_ROOT = os.path.join(BASE_DIR, 'cdn/static')

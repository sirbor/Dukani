import os

import environ
import oscar
from django.utils.translation import gettext_lazy as _dashboard_label

env = environ.Env()

# Path helper
location = lambda x: os.path.join(
    os.path.dirname(os.path.realpath(__file__)), x)

# Optional local secrets: create sandbox/.env (never commit) — KEY=value per line
environ.Env.read_env(location(".env"))

DEBUG = env.bool('DEBUG', default=True)

# Include 0.0.0.0 so opening http://0.0.0.0:8000/ in a browser does not trigger
# DisallowedHost (Host header is literally "0.0.0.0"). Prefer http://127.0.0.1:8000/ for local use.
ALLOWED_HOSTS = env.list(
    'ALLOWED_HOSTS',
    default=['localhost', '127.0.0.1', '0.0.0.0', '[::1]', 'sirbor11.pythonanywhere.com', '.herokuapp.com'],
)

# HTTPS sites must list trusted origins for CSRF (e.g. https://sirbor11.pythonanywhere.com).
CSRF_TRUSTED_ORIGINS = env.list(
    'CSRF_TRUSTED_ORIGINS',
    default=['https://sirbor11.pythonanywhere.com', 'https://dukani-1250ed216a09.herokuapp.com'],
)

EMAIL_SUBJECT_PREFIX = '[Dukani Bookstore] '
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Use a Sqlite database by default; Heroku / Postgres use DATABASE_URL.
DATABASES = {
    'default': {
        'ENGINE': os.environ.get('DATABASE_ENGINE', 'django.db.backends.sqlite3'),
        'NAME': os.environ.get('DATABASE_NAME', location('db.sqlite')),
        'USER': os.environ.get('DATABASE_USER', None),
        'PASSWORD': os.environ.get('DATABASE_PASSWORD', None),
        'HOST': os.environ.get('DATABASE_HOST', None),
        'PORT': os.environ.get('DATABASE_PORT', None),
        'ATOMIC_REQUESTS': True
    }
}
if os.environ.get('DATABASE_URL'):
    import dj_database_url

    DATABASES['default'] = dj_database_url.config(
        conn_max_age=600,
        conn_health_checks=True,
        ssl_require=True,
    )

CACHES = {
    'default': env.cache(default='locmemcache://'),
}


# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
USE_TZ = True
TIME_ZONE = 'Africa/Nairobi'

TEST_RUNNER = 'django.test.runner.DiscoverRunner'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-gb'

# Includes all languages that have >50% coverage in Transifex
# Taken from Django's default setting for LANGUAGES
gettext_noop = lambda s: s
LANGUAGES = (
    ('ar', gettext_noop('Arabic')),
    ('ca', gettext_noop('Catalan')),
    ('cs', gettext_noop('Czech')),
    ('da', gettext_noop('Danish')),
    ('de', gettext_noop('German')),
    ('en-gb', gettext_noop('British English')),
    ('el', gettext_noop('Greek')),
    ('es', gettext_noop('Spanish')),
    ('fi', gettext_noop('Finnish')),
    ('fr', gettext_noop('French')),
    ('it', gettext_noop('Italian')),
    ('ko', gettext_noop('Korean')),
    ('nl', gettext_noop('Dutch')),
    ('pl', gettext_noop('Polish')),
    ('pt', gettext_noop('Portuguese')),
    ('pt-br', gettext_noop('Brazilian Portuguese')),
    ('ro', gettext_noop('Romanian')),
    ('ru', gettext_noop('Russian')),
    ('sk', gettext_noop('Slovak')),
    ('uk', gettext_noop('Ukrainian')),
    ('zh-cn', gettext_noop('Simplified Chinese')),
)

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = location("public/media")

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/media/'

STATIC_URL = '/static/'
STATIC_ROOT = location('public/static')
STATICFILES_DIRS = (
    location('static/'),
)
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": 'whitenoise.storage.CompressedManifestStaticFilesStorage',
    },
}

# whitenoise will not raise an error if a static file is missing from the manifest
# and will instead fall back to the original file name.
WHITENOISE_MANIFEST_STRICT = False

# With DEBUG=True, use non-manifest storage so /static/... paths work without
# running collectstatic (manifest mismatch otherwise looks like "missing CSS"
# and can make pages look blank). Production should set DEBUG=False and run
# collectstatic so Whitenoise manifest storage applies.
if DEBUG:
    STORAGES["staticfiles"] = {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    }

# Default primary key field type
# https://docs.djangoproject.com/en/dev/ref/settings/#default-auto-field
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Make this unique, and don't share it with anybody.
SECRET_KEY = env.str('SECRET_KEY', default='UajFCuyjDKmWHe29neauXzHi9eZoRXr6RMbT5JyAdPiACBP6Cra2')

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            location('templates'),
        ],
        'OPTIONS': {
            'loaders': [
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',
            ],
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.request',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.contrib.messages.context_processors.messages',

                # Oscar specific
                'oscar.apps.search.context_processors.search_form',
                'oscar.apps.communication.notifications.context_processors.notifications',
                'oscar.apps.checkout.context_processors.checkout',
                'oscar.core.context_processors.metadata',
                'apps.storefront_settings.context_processors.storefront_branding',
            ],
            'debug': DEBUG,
        }
    }
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',

    'django.contrib.sessions.middleware.SessionMiddleware',
    # After SessionMiddleware, before CommonMiddleware (Django i18n URL patterns)
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',

    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    'django.middleware.http.ConditionalGetMiddleware',

    # Ensure a valid basket is added to the request instance for every request
    'oscar.apps.basket.middleware.BasketMiddleware',

    # Run after other middleware; only reacts to 404 responses
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
]

ROOT_URLCONF = 'urls'


# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(message)s',
        },
        'simple': {
            'format': '[%(asctime)s] %(message)s'
        },
    },
    'root': {
        'level': 'DEBUG',
        'handlers': ['console'],
    },
    'handlers': {
        'null': {
            'level': 'DEBUG',
            'class': 'logging.NullHandler',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
    },
    'loggers': {
        'oscar': {
            'level': 'DEBUG',
            'propagate': True,
        },
        'oscar.catalogue.import': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'oscar.alerts': {
            'handlers': ['null'],
            'level': 'INFO',
            'propagate': False,
        },

        # Django loggers
        'django': {
            'handlers': ['null'],
            'propagate': True,
            'level': 'INFO',
        },
        'django.request': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': True,
        },
        'django.db.backends': {
            'level': 'WARNING',
            'propagate': True,
        },
        'django.security.DisallowedHost': {
            'handlers': ['null'],
            'propagate': False,
        },

        # Third party
        'raven': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': False,
        },
        'sorl.thumbnail': {
            'handlers': ['console'],
            'propagate': True,
            'level': 'INFO',
        },
    }
}


INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django.contrib.flatpages',

    'oscar.config.Shop',
    'oscar.apps.analytics.apps.AnalyticsConfig',
    'apps.checkout.apps.CheckoutConfig',
    'oscar.apps.address.apps.AddressConfig',
    'oscar.apps.shipping.apps.ShippingConfig',
    'oscar.apps.catalogue.apps.CatalogueConfig',
    'oscar.apps.catalogue.reviews.apps.CatalogueReviewsConfig',
    'oscar.apps.communication.apps.CommunicationConfig',
    'oscar.apps.partner.apps.PartnerConfig',
    'oscar.apps.basket.apps.BasketConfig',
    'oscar.apps.payment.apps.PaymentConfig',
    'oscar.apps.offer.apps.OfferConfig',
    'oscar.apps.order.apps.OrderConfig',
    'oscar.apps.customer.apps.CustomerConfig',
    'oscar.apps.search.apps.SearchConfig',
    'oscar.apps.voucher.apps.VoucherConfig',
    'oscar.apps.wishlists.apps.WishlistsConfig',
    'apps.dashboard_ext.apps.DashboardConfig',
    'oscar.apps.dashboard.reports.apps.ReportsDashboardConfig',
    'oscar.apps.dashboard.users.apps.UsersDashboardConfig',
    'oscar.apps.dashboard.orders.apps.OrdersDashboardConfig',
    'oscar.apps.dashboard.catalogue.apps.CatalogueDashboardConfig',
    'oscar.apps.dashboard.offers.apps.OffersDashboardConfig',
    'oscar.apps.dashboard.partners.apps.PartnersDashboardConfig',
    'oscar.apps.dashboard.pages.apps.PagesDashboardConfig',
    'oscar.apps.dashboard.ranges.apps.RangesDashboardConfig',
    'oscar.apps.dashboard.reviews.apps.ReviewsDashboardConfig',
    'oscar.apps.dashboard.vouchers.apps.VouchersDashboardConfig',
    'oscar.apps.dashboard.communications.apps.CommunicationsDashboardConfig',
    'oscar.apps.dashboard.shipping.apps.ShippingDashboardConfig',

    # 3rd-party apps that Oscar depends on
    'widget_tweaks',
    'haystack',
    'treebeard',
    'sorl.thumbnail',
    'django_tables2',

    # Django apps that the sandbox depends on
    'django.contrib.sitemaps',

    # M-Pesa (Daraja) + PayPal checkout integration
    'apps.gateway_payments.apps.GatewayPaymentsConfig',

    'apps.bookstore.apps.BookstoreConfig',
    'apps.storefront_settings.apps.StorefrontSettingsConfig',
]

# Safaricom Daraja (Lipa na M-Pesa / STK Push) — use environment in production
DARAJA_CONSUMER_KEY = env.str("DARAJA_CONSUMER_KEY", default="")
DARAJA_CONSUMER_SECRET = env.str("DARAJA_CONSUMER_SECRET", default="")
DARAJA_SHORTCODE = env.str("DARAJA_SHORTCODE", default="")
DARAJA_PASSKEY = env.str("DARAJA_PASSKEY", default="")
DARAJA_ENV = env.str("DARAJA_ENV", default="sandbox")

# Manual M-Pesa Paybill (customer pays in SIM, then enters confirmation on site)
MANUAL_MPESA_PAYBILL = env.str("MANUAL_MPESA_PAYBILL", default="247247")
MANUAL_MPESA_ACCOUNT = env.str("MANUAL_MPESA_ACCOUNT", default="0530162645020")

# PayPal REST (Orders v2)
PAYPAL_CLIENT_ID = env.str("PAYPAL_CLIENT_ID", default="")
PAYPAL_CLIENT_SECRET = env.str("PAYPAL_CLIENT_SECRET", default="")
PAYPAL_MODE = env.str("PAYPAL_MODE", default="sandbox")

# Public site origin for payment return / webhook URLs (no trailing slash).
# If you browse via http://127.0.0.1:8000 but runserver binds 0.0.0.0, set
# PUBLIC_BASE_URL=http://127.0.0.1:8000 so PayPal redirects back to a real host.
# In production use your HTTPS canonical domain, e.g. https://yoursite.pythonanywhere.com
PUBLIC_BASE_URL = env.str("PUBLIC_BASE_URL", default="")

# Add Oscar's custom auth backend so users can sign in using their email
# address.
AUTHENTICATION_BACKENDS = (
    'oscar.apps.customer.auth_backends.EmailBackend',
    'django.contrib.auth.backends.ModelBackend',
)

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 9,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
]

LOGIN_REDIRECT_URL = '/'
APPEND_SLASH = True

# ====================
# Messages contrib app
# ====================

from django.contrib.messages import constants as messages
MESSAGE_TAGS = {
    messages.ERROR: 'danger'
}

HAYSTACK_SIGNAL_PROCESSOR = 'haystack.signals.RealtimeSignalProcessor'

# Woosh settings
HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.whoosh_backend.WhooshEngine',
        'PATH': location('whoosh_index'),
        'INCLUDE_SPELLING': True,
    },
}

# Here's a sample Haystack config for Solr 6.x (which is recommended)
# HAYSTACK_CONNECTIONS = {
#     'default': {
#         'ENGINE': 'haystack.backends.solr_backend.SolrEngine',
#         'URL': 'http://127.0.0.1:8983/solr/sandbox',
#         'ADMIN_URL': 'http://127.0.0.1:8983/solr/admin/cores',
#         'INCLUDE_SPELLING': True,
#     }
# }

# =============
# Debug Toolbar
# =============

INTERNAL_IPS = ['127.0.0.1', '::1']

# ==============
# Oscar settings
# ==============

from oscar.defaults import *

# Meta
# ====

OSCAR_SHOP_NAME = 'Dukani Bookstore'
OSCAR_SHOP_TAGLINE = 'Books online'

OSCAR_RECENTLY_VIEWED_PRODUCTS = 20
OSCAR_ALLOW_ANON_CHECKOUT = True

# Prices throughout the storefront (basket, checkout, M-Pesa, PayPal)
OSCAR_DEFAULT_CURRENCY = "KES"
# Use Kenyan locale so Babel shows KSh (symbol may vary by browser/font)
OSCAR_CURRENCY_FORMAT = {
    "KES": {
        "currency_digits": True,
        "locale": "en_KE",
    },
}

# Order processing
# ================

# Sample order/line status settings. This is quite simplistic. It's like you'll
# want to override the set_status method on the order object to do more
# sophisticated things.
OSCAR_INITIAL_ORDER_STATUS = 'Pending'
OSCAR_INITIAL_LINE_STATUS = 'Pending'

# This dict defines the new order statuses than an order can move to
OSCAR_ORDER_STATUS_PIPELINE = {
    'Pending': ('Being processed', 'Cancelled',),
    'Being processed': ('Complete', 'Cancelled',),
    'Cancelled': (),
    'Complete': (),
}

# This dict defines the line statuses that will be set when an order's status
# is changed
OSCAR_ORDER_STATUS_CASCADE = {
    'Being processed': 'Being processed',
    'Cancelled': 'Cancelled',
    'Complete': 'Shipped',
}

# Sorl
# ====

THUMBNAIL_DEBUG = DEBUG
THUMBNAIL_KEY_PREFIX = 'oscar-sandbox'
THUMBNAIL_KVSTORE = env(
    'THUMBNAIL_KVSTORE',
    default='sorl.thumbnail.kvstores.cached_db_kvstore.KVStore')
THUMBNAIL_REDIS_URL = env('THUMBNAIL_REDIS_URL', default=None)

# easy-thumbnail. See https://github.com/SmileyChris/easy-thumbnails/issues/641#issuecomment-2291098096
THUMBNAIL_DEFAULT_STORAGE_ALIAS = "default"

# Django 1.6 has switched to JSON serializing for security reasons, but it does not
# serialize Models. We should resolve this by extending the
# django/core/serializers/json.Serializer to have the `dumps` function. Also
# in tests/config.py
SESSION_SERIALIZER = 'django.contrib.sessions.serializers.JSONSerializer'

# Security
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = env.bool('SECURE_SSL_REDIRECT', default=False)
SECURE_HSTS_SECONDS = env.int('SECURE_HSTS_SECONDS', default=0)
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True

# Try and import local settings which can be used to override any of the above.
try:
    from settings_local import *
except ImportError:
    pass

# Dashboard: add storefront branding editor (URLs wired in apps.dashboard_ext).
OSCAR_DASHBOARD_NAVIGATION = [
    *OSCAR_DASHBOARD_NAVIGATION,
    {
        'label': _dashboard_label('Storefront appearance'),
        'icon': 'fas fa-store',
        'url_name': 'dashboard:storefront-branding',
    },
]

"""
Show dates in NetBox's web UI in each user's own format (default dd.mm.yyyy).

Only the display changes: stored data, CSV exports, the REST and GraphQL
APIs stay ISO 8601, and the plugin adds no tables or migrations. See
DEVELOPER.md for what is patched and why.
"""
from netbox.plugins import PluginConfig


class LocalDateFormatConfig(PluginConfig):
    name = 'netbox_local_dateformat'
    verbose_name = 'Local date format'
    description = 'Show dates in the web UI in each user\'s own format.'
    version = '0.1.0'
    author = 'Matti'
    base_url = 'local-dateformat'
    # Only claim what CI tests (.github/workflows/test.yml).
    min_version = '4.7.0'
    default_settings = {'date_format': 'd.m.Y'}
    # Loaded from preferences.preferences (NetBox's default resource path).
    user_preferences = 'preferences.preferences'

    def ready(self):
        super().ready()
        from . import patches
        patches.apply()


config = LocalDateFormatConfig

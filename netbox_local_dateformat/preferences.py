from django.utils.translation import gettext_lazy as _

from users.preferences import UserPreference

from .formats import DATE_FORMATS

# Loaded by NetBox from PluginConfig.user_preferences and shown on each user's
# Preferences page. Stored in NetBox's own UserConfig data, so no tables or
# migrations are needed.
preferences = {
    'date_format': UserPreference(
        label=_('Date format'),
        choices=(('', _('System default')), *DATE_FORMATS),
        default='',
        description=_('How dates are shown to you. Stored data, exports and the API stay ISO 8601.'),
    ),
}

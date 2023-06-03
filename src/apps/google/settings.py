from django.conf import settings

DRIVE = 'drive'
DRIVE_VERSION = 'v3'
PERMISSIONS_BODY = {
    'type': 'user',
    'role': 'writer',
    'emailAddress': settings.EMAIL,
}
PERMISSIONS_FIELDS = 'id'

SHEETS = 'sheets'
SHEETS_VERSION = 'v4'

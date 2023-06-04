from django.conf import settings

GOOGLE_ENV_VARS = {
    "funds_spreadsheet_id": settings.FUNDS_SPREADSHEET_ID,
    "mentors_spreadsheet_id": settings.MENTORS_SPREADSHEET_ID,
    **settings.ENV_INFO,
}
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
RANGE = 'A1:E30'
INPUT_OPTION = 'USER_ENTERED'
INSERT_OPTION = 'INSERT_ROWS'
MAJOR_DIMENSION = 'ROWS'

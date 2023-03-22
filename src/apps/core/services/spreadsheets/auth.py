from aiogoogle.auth.creds import ServiceAccountCreds
from django.conf import settings

service_account_keys = {
    "type": "service_account",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    **settings.ENV_INFO,
}

creds = ServiceAccountCreds(scopes=settings.SCOPES, **service_account_keys)


'''    SCOPES = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive',
    ]
    INFO = {
        'type': settings.type,
        'project_id': settings.project_id,
        'private_key_id': settings.private_key_id,
        'private_key': settings.private_key,
        'client_email': settings.client_email,
        'client_id': settings.client_id,
        'auth_uri': settings.auth_uri,
        'token_uri': settings.token_uri,
        'auth_provider_x509_cert_url': settings.auth_provider_x509_cert_url,
        'client_x509_cert_url': settings.client_x509_cert_url,
        'scopes': SCOPES,
    }'''

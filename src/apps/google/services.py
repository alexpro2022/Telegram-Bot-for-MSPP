import logging

from aiogoogle import Aiogoogle
from aiogoogle.auth.creds import ServiceAccountCreds
from django.conf import settings

from . import settings as s

logger = logging.getLogger(__name__)
cred = ServiceAccountCreds(**settings.INFO)


async def set_user_permissions(
        spreadsheet_id: str,
        aiogoogle: Aiogoogle,
) -> None:
    service = await aiogoogle.discover(s.DRIVE, s.DRIVE_VERSION)
    await aiogoogle.as_service_account(
        service.permissions.create(
            fileId=spreadsheet_id,
            json=s.PERMISSIONS_BODY,
            fields=s.PERMISSIONS_FIELDS,
        ))


async def spreadsheet_append(
        spreadsheet_id: str,
        table_values: list,
        aiogoogle: Aiogoogle,
) -> None:
    value_range_body = {
        'majorDimension': s.MAJOR_DIMENSION,
        'values': [table_values],
    }
    service = await aiogoogle.discover(s.SHEETS, s.SHEETS_VERSION)
    await aiogoogle.as_service_account(
        service.spreadsheets.values.append(
            spreadsheetId=spreadsheet_id,
            range=s.RANGE,
            valueInputOption=s.INPUT_OPTION,
            insertDataOption=s.INSERT_OPTION,
            json=value_range_body,
        )
    )


async def send_to_google(spreadsheet_id: str, table_values: list):
    async with Aiogoogle(service_account_creds=cred) as aiogoogle:
        await set_user_permissions(spreadsheet_id, aiogoogle)
        await spreadsheet_append(spreadsheet_id, table_values, aiogoogle)

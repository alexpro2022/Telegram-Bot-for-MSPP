import asyncio

from aiogoogle import Aiogoogle, HTTPError

# from django.conf import settings
from config import settings

from .auth import creds
from .logger import logger

PERMISSIONS_FIELDS = 'id'
PERMISSIONS_BODY = {
    'type': 'user',
    'role': 'writer',
    'emailAddress': settings.EMAIL_USER,
}


async def send(
    spreadsheetid: str,
    table_values: list[list],
) -> None:

    async with Aiogoogle(service_account_creds=creds) as aiogoogle:
        range = f"1:{len(table_values)}"
        update_body = {"majorDimension": "ROWS", "values": table_values}

        service = await aiogoogle.discover("drive", "v3")
        await aiogoogle.as_service_account(
            service.permissions.create(
                fileId=spreadsheetid,
                json=PERMISSIONS_BODY,
                fields=PERMISSIONS_FIELDS,
            ))
        try:
            service = await aiogoogle.discover("sheets", "v4")
            await aiogoogle.as_service_account(
                service.spreadsheets.values.update(
                    spreadsheetId=spreadsheetid,
                    range=range, valueInputOption="USER_ENTERED",
                    json=update_body
                )
            )
        except HTTPError:
            msg = "Не удалось отправить сроку в таблицу!"
            # logger.critical(msg, e)
            logger.exception(msg)
            raise HTTPError(msg)
        logger.info(settings.SPREADSHEETS_URL.format(spreadsheetid))


def sender(
    values: list[list],
    spreadsheetid: str,
) -> None:
    """Отправляет переданные данные в Google таблицы.

    Args:
        table_values (list[list[Any]]): Значения колонок
        spreadsheetid (str): ID Google таблицы. Defaults to settings.SPREADSHEET_ID.

    Raises:
        HTTPError: Не удалось отправить сроку в таблицу
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    asyncio.get_event_loop().run_until_complete(send(spreadsheetid, values))

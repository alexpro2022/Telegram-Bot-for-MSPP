from django.conf import settings

from .spreadsheets import sender


def send_to_google_sheets(
    values: list[list],
    spreadsheetid: str = settings.SPREADSHEET_ID,
) -> None:
    """Отправляет переданные данные в Google таблицы.

    Args:
        table_values (list[list[Any]]): Значения колонок
        spreadsheetid (str): ID Google таблицы. Defaults to settings.SPREADSHEET_ID.

    Raises:
        HTTPError: Не удалось отправить сроку в таблицу
    """
    sender(values, spreadsheetid)

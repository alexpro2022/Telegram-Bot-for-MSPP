"""
To customize the class please inherit it and override the two methods:
----------------------------------
    async def _get_spreadsheet_create_body(
        self, session: Optional[AsyncSession] = None,
    ):
----------------------------------
    async def _get_spreadsheet_update_body(
        self, session: Optional[AsyncSession] = None,
    ):
----------------------------------

and at least following constants:
    UPLOAD_SUMMARY: str = 'must be implemented'
    UPLOAD_DESCRIPTION: str = 'must be implemented'
    GETALL_SUMMARY: str = 'must be implemented'
    GETALL_DESCRIPTION: str = 'must be implemented'
    DELETE_SUMMARY: str = 'must be implemented'
    DELETE_DESCRIPTION: str = 'must be implemented'
    CLEARDISK_SUMMARY: str = 'must be implemented'
    CLEARDISK_DESCRIPTION: str = 'must be implemented'
"""
from typing import Dict

from app.core import settings
from app.crud import charity_crud

from .base import GoogleBaseClient


class GoogleClient(GoogleBaseClient):
    UPLOAD_SUMMARY: str = 'Формирование отчёта в гугл-таблице.'
    UPLOAD_DESCRIPTION: str = (
        f'{settings.SUPER_ONLY}' +
        'В таблице будут закрытые проекты, отсортированные по скорости '
        'сбора средств — от тех, что закрылись быстрее всего, до тех, '
        'что долго собирали нужную сумму.'
    )
    GETALL_SUMMARY: str = 'Вывод всех таблиц.'
    GETALL_DESCRIPTION: str = (
        f'{settings.SUPER_ONLY}' +
        'Будет выведен список всех таблиц, хранящихся на диске, '
        'либо пустой список.'
    )
    DELETE_SUMMARY: str = 'Удаление таблицы.'
    DELETE_DESCRIPTION: str = (
        f'{settings.SUPER_ONLY}' +
        '**__Введите id таблицы, которую хотите удалить.__**'
    )
    CLEARDISK_SUMMARY: str = 'Очистка диска.'
    CLEARDISK_DESCRIPTION: str = (
        f'{settings.SUPER_ONLY}' +
        '**__ВНИМАНИЕ: с диска будут удалены все таблицы!__**'
    )

    async def get_spreadsheet_create_body(self, session) -> Dict[str, str]:
        return {
            'properties': {
                'title': f'Отчет от: {self._get_datetime()}',
                'locale': self.LOCALE,
            },
            'sheets': self.SHEETS_PROPERTIES,
        }

    async def get_spreadsheet_update_body(self, session) -> Dict[str, str]:
        table = [
            ['Отчет от', self._get_datetime()],
            ['Топ проектов по скорости закрытия'],
            ['Название проекта', 'Время сбора', 'Описание'],
        ]
        projects = await charity_crud.get_projects_by_completion_rate(session)
        if projects:
            for project in projects:
                table.append([
                    project.name,
                    str(project.close_date - project.create_date),
                    project.description,
                ])
        return {
            'majorDimension': self.DIMENSIONS,
            'values': table,
        }


google_client = GoogleClient()

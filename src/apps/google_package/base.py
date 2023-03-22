"""
The below class is a base class for Google clients.
It allows the following operations:
  * upload_spreadsheet - creates the speadsheet, fills it with data and
                         returns the full path to the created spreadsheet;
  * get_all_spreadsheets - returns the list of dictionaries with
                           the info of each spreadsheet on the disk;
  * delete_spreadsheet - allows to delete the desired spreadsheet;
  * clear_disk - allows to delete all the spreadsheets from the disk;

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

from datetime import datetime as dt
from http import HTTPStatus
from typing import AsyncGenerator, Dict, List, Optional

from aiogoogle import Aiogoogle, GoogleAPI, HTTPError
from aiogoogle.auth.creds import ServiceAccountCreds
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import settings


class GoogleBaseClient:
    """Base class for Google client."""
    FORMAT = "%Y/%m/%d %H:%M:%S"
    LOCALE = 'ru_RU'
    DRIVE_API_NAME = 'drive'
    DRIVE_API_VERSION = 'v3'
    SHEETS_API_NAME = 'sheets'
    SHEETS_API_VERSION = 'v4'
    SHEET_TYPE = 'GRID'
    SHEET_ID = 0
    SHEET_TITLE = 'Лист1'
    SHEET_ROW_COUNT = 100
    SHEET_COLUMN_COUNT = 11
    SHEETS_PROPERTIES = [{
        'properties': {
            'sheetType': SHEET_TYPE,
            'sheetId': SHEET_ID,
            'title': SHEET_TITLE,
            'gridProperties': {
                'rowCount': SHEET_ROW_COUNT,
                'columnCount': SHEET_COLUMN_COUNT,
            }}
    }]
    SCOPES = [
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
    }
    DIMENSIONS = 'ROWS'
    RANGE = 'A1:E30'
    INPUT_OPTION = 'USER_ENTERED'
    PERMISSIONS_FIELDS = 'id'
    PERMISSIONS_BODY = {
        'type': 'user',
        'role': 'writer',
        'emailAddress': settings.email,
    }
    UPLOAD_SUMMARY: str = 'must be implemented'
    UPLOAD_DESCRIPTION: str = 'must be implemented'
    GETALL_SUMMARY: str = 'must be implemented'
    GETALL_DESCRIPTION: str = 'must be implemented'
    DELETE_SUMMARY: str = 'must be implemented'
    DELETE_DESCRIPTION: str = 'must be implemented'
    CLEARDISK_SUMMARY: str = 'must be implemented'
    CLEARDISK_DESCRIPTION: str = 'must be implemented'

    def _get_datetime(self) -> str:
        return dt.now().strftime(self.FORMAT)

    async def get_spreadsheet_create_body(
        self, session: Optional[AsyncSession] = None,
    ) -> Dict[str, str]:
        raise NotImplementedError(
            'method _get_spreadsheet_create_body()` must be implemented.')

    async def get_spreadsheet_update_body(
        self, session: Optional[AsyncSession] = None,
    ) -> Dict[str, str]:
        raise NotImplementedError(
            'method _get_spreadsheet_update_body()` must be implemented.')

    async def _get_api_service(
        self,
        wrapper_services: Aiogoogle,
        drive: bool = False,
    ) -> GoogleAPI:
        if drive:
            return await wrapper_services.discover(
                self.DRIVE_API_NAME,
                self.DRIVE_API_VERSION,
            )
        return await wrapper_services.discover(
            self.SHEETS_API_NAME,
            self.SHEETS_API_VERSION,
        )

    async def set_user_permissions(
        self,
        wrapper_services: Aiogoogle,
        spreadsheet_id: str,
    ) -> None:
        service = await self._get_api_service(wrapper_services, drive=True)
        await wrapper_services.as_service_account(
            service.permissions.create(
                fileId=spreadsheet_id,
                json=self.PERMISSIONS_BODY,
                fields=self.PERMISSIONS_FIELDS,
            ))

    async def spreadsheets_create(
        self,
        wrapper_services: Aiogoogle,
        session: Optional[AsyncSession] = None,
    ) -> str:
        service = await self._get_api_service(wrapper_services)
        create_body = await self.get_spreadsheet_create_body(session)
        response = await wrapper_services.as_service_account(
            service.spreadsheets.create(
                json=create_body,
            ))
        return response['spreadsheetId']

    async def spreadsheets_update(
        self,
        wrapper_services: Aiogoogle,
        spreadsheet_id: str,
        session: Optional[AsyncSession] = None
    ) -> None:
        service = await self._get_api_service(wrapper_services)
        update_body = await self.get_spreadsheet_update_body(session)
        await wrapper_services.as_service_account(
            service.spreadsheets.values.update(
                spreadsheetId=spreadsheet_id,
                range=self.RANGE,
                valueInputOption=self.INPUT_OPTION,
                json=update_body,
            ))

    async def upload(
        self,
        wrapper_services: Aiogoogle,
        session: Optional[AsyncSession] = None,
    ) -> str:
        spreadsheet_id = await self.spreadsheets_create(
            wrapper_services, session)
        await self.set_user_permissions(
            wrapper_services, spreadsheet_id)
        await self.spreadsheets_update(
            wrapper_services, spreadsheet_id, session)
        return (
            f'Создан новый документ: '
            f'https://docs.google.com/spreadsheets/d/{spreadsheet_id} ')

    async def get_all_spreadsheets(
        self,
        wrapper_services: Aiogoogle,
    ) -> List[Dict[str, str]]:
        service = await self._get_api_service(wrapper_services, drive=True)
        response = await wrapper_services.as_service_account(
            service.files.list(
                q='mimeType="application/vnd.google-apps.spreadsheet"'))
        return response['files']

    async def delete_spreadsheet(
        self,
        wrapper_services: Aiogoogle,
        spreadsheet_id: str,
    ) -> str:
        service = await self._get_api_service(wrapper_services, drive=True)
        try:
            await wrapper_services.as_service_account(
                service.files.delete(fileId=spreadsheet_id))
        except HTTPError:
            raise HTTPException(
                HTTPStatus.NOT_FOUND,
                f'Документ с id = {spreadsheet_id} не найден.')
        return f'Документ с id = {spreadsheet_id} удален.'

    async def clear_disk(
        self,
        wrapper_services: Aiogoogle
    ) -> str:
        spreadsheets = await self.get_all_spreadsheets(wrapper_services)
        if spreadsheets:
            for spreadsheet in spreadsheets:
                await self.delete_spreadsheet(
                    wrapper_services, spreadsheet['id'])
            return 'Документы удалены, диск пуст.'
        return 'На диске нет документов для удаления.'

    async def get_google_service(self) -> AsyncGenerator[Aiogoogle, None]:
        async with Aiogoogle(
            service_account_creds=ServiceAccountCreds(**self.INFO)
        ) as aiogoogle:
            yield aiogoogle
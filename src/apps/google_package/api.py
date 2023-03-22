"""
Endpoints for the following operations:
  * upload_spreadsheet - creates the speadsheet, fills it with data and
                         returns the full path to the created spreadsheet;
  * get_all_spreadsheets - returns the list of dictionaries with
                           the info of each spreadsheet on the disk;
  * delete_spreadsheet - allows to delete the desired spreadsheet;
  * clear_disk - allows to delete all the spreadsheets from the disk;
"""
from typing import Dict, List

from aiogoogle import Aiogoogle
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import current_superuser, get_async_session

from .client import google_client

router = APIRouter(prefix='/google', tags=['Google'])


@router.post(
    '/',
    dependencies=[Depends(current_superuser)],
    summary=google_client.UPLOAD_SUMMARY,
    description=google_client.UPLOAD_DESCRIPTION,
)
async def upload_spreadsheet_api(
    session: AsyncSession = Depends(get_async_session),
    wrapper_services: Aiogoogle = Depends(google_client.get_google_service),
) -> str:
    return await google_client.upload(wrapper_services, session)


@router.get(
    '/',
    dependencies=[Depends(current_superuser)],
    summary=google_client.GETALL_SUMMARY,
    description=google_client.GETALL_DESCRIPTION,
)
async def get_all_spreadsheets_api(
    wrapper_services: Aiogoogle = Depends(google_client.get_google_service)
) -> List[Dict[str, str]]:
    return await google_client.get_all_spreadsheets(wrapper_services)


@router.delete(
    '/{spreadsheet_id}',
    dependencies=[Depends(current_superuser)],
    summary=google_client.DELETE_SUMMARY,
    description=google_client.DELETE_DESCRIPTION,
)
async def delete_spreadsheet_api(
    spreadsheet_id: str,
    wrapper_services: Aiogoogle = Depends(google_client.get_google_service)
) -> str:
    return await google_client.delete_spreadsheet(
        wrapper_services, spreadsheet_id)


@router.delete(
    '/',
    dependencies=[Depends(current_superuser)],
    summary=google_client.CLEARDISK_SUMMARY,
    description=google_client.CLEARDISK_DESCRIPTION,
)
async def clear_disk_api(
    wrapper_services: Aiogoogle = Depends(google_client.get_google_service)
) -> str:
    return await google_client.clear_disk(wrapper_services)

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from src.api.deps import get_location_service
from src.services.location import LocationService

router = APIRouter(prefix="/web/locations", tags=["web"])

templates = Jinja2Templates(directory="src/templates")


@router.get("", response_class=HTMLResponse)
async def show_locations_list(request: Request) -> HTMLResponse:
    return templates.TemplateResponse("locations_list.html", {"request": request})


@router.get("/new", response_class=HTMLResponse)
async def show_location_form(request: Request) -> HTMLResponse:
    return templates.TemplateResponse("location_form.html", {"request": request})


@router.get("/{location_id}/edit", response_class=HTMLResponse)
async def show_location_edit(
    request: Request, location_id: str, service: LocationService = Depends(get_location_service)
) -> HTMLResponse:
    location = await service.get_location(location_id)
    return templates.TemplateResponse("location_edit.html", {"request": request, "location": location})

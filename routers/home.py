from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates


router = APIRouter(prefix="", tags=["Home"])
templates = Jinja2Templates(directory="templates")


@router.get("/", response_class=HTMLResponse)
async def get_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@router.get("/classes", response_class=HTMLResponse)
async def get_classes(request: Request):
    return templates.TemplateResponse("class.html", {"request": request})

@router.get("/calculator", response_class=HTMLResponse)
async def get_calculator(request: Request):
    return templates.TemplateResponse("calculator.html", {"request": request})



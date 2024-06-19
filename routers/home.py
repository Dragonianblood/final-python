from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from dependencies.auth import verify_jwt_cookie

from models.photo import Gallery, PhotoForm

router = APIRouter(prefix="", tags=["Home"])
templates = Jinja2Templates(directory="templates")


@router.get("/", response_class=HTMLResponse)
async def get_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@router.get("/classes", response_class=HTMLResponse)
async def get_classes(request: Request, payload: dict = Depends(verify_jwt_cookie)):
    return templates.TemplateResponse("class.html", {"request": request})


@router.get("/calculator", response_class=HTMLResponse)
async def get_calculator(request: Request):
    return templates.TemplateResponse("calculator.html", {"request": request})

@router.get("/login_page", response_class=HTMLResponse)
async def get_calculator(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.get("/signup_page", response_class=HTMLResponse)
async def get_calculator(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})


@router.get("/class/{class_id}", response_class=RedirectResponse)
async def go_to_class(request: Request, class_id: str):
    photos = await Gallery.find().to_list()
    print(photos)
    return templates.TemplateResponse("class_gallery.html", {"request": request, "photos": photos, "class_id":class_id})

@router.post("/photo/{class_id}/{photo_id}", response_class=HTMLResponse)
async def photo_details(request: Request, photo_id: str, class_id:str, action: str = Form(...), payload: dict = Depends(verify_jwt_cookie)):
    print("hi")
    photo = await Gallery.get(photo_id)
    photos = await Gallery.find().to_list()
    try:
        if action == "like":
            if payload["sub"] in photo.likes_who:
                photo.likes -= 1
                photo.likes_who.remove(payload["sub"])
            else:
                photo.likes += 1
                photo.likes_who.append(payload["sub"])
        elif action == "dislike":
            if payload["sub"] in photo.dislikes_who:
                photo.dislikes -= 1
                photo.dislikes_who.remove(payload["sub"])
            else:
                photo.dislikes += 1
                photo.dislikes_who.append(payload["sub"])

        await photo.save()
        return templates.TemplateResponse("class_gallery.html", {"request": request, "photos": photos, "class_id":class_id})



    except Exception as err:
        print(err)
        return templates.TemplateResponse("class_gallery.html", {"request": request, "photos": photos, "class_id":class_id})


from fastapi import APIRouter, Request, Form, Depends, File, UploadFile, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from dependencies.auth import verify_jwt_cookie

from models.photo import Gallery, PhotoForm
from models.user import User
from PIL import Image
import os

router = APIRouter(prefix="", tags=["Home"])
templates = Jinja2Templates(directory="templates")


def get_rating(photo):
    return (photo.likes+1) / (photo.dislikes+1)


@router.get("/", response_class=HTMLResponse)
async def get_index(request: Request, payload = Depends(verify_jwt_cookie)):

    photos = sorted(await Gallery.find().to_list(), key=get_rating, reverse=True)[:6]

    user_authenticated = payload is not None

    return templates.TemplateResponse("index.html", {"request": request, "photos": photos,
                                                     "user_authenticated": user_authenticated})

@router.get("/reset")
async def cookie_reset(response: Response):
    response = RedirectResponse(url="/", status_code=303)
    response.set_cookie(key="access_token", value="", httponly=True, max_age=0, expires=0)
    return response

@router.get("/classes", response_class=HTMLResponse)
async def get_classes(request: Request, payload: dict = Depends(verify_jwt_cookie)):
    user_authenticated = payload is not None
    return templates.TemplateResponse("class.html", {"request": request, "user_authenticated": user_authenticated})


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
async def go_to_class(request: Request, class_id: str, payload: dict = Depends(verify_jwt_cookie)):
    photos = sorted(await Gallery.find().to_list(), key=get_rating, reverse=True)
    user_authenticated = payload is not None
    return templates.TemplateResponse("class_gallery.html",
                                      {"request": request, "photos": photos, "class_id": class_id,
                                       "user_authenticated": user_authenticated})


@router.get("/{class_id}/{photo_id}", response_class=RedirectResponse)
async def go_to_photo(request: Request, class_id: str, photo_id: str, payload: dict = Depends(verify_jwt_cookie)):
    photo = await Gallery.get(photo_id)
    user = await User.get(photo.author)
    user_authenticated = payload is not None
    return templates.TemplateResponse("image.html",
                                      {"request": request, "photo": photo, "author": user, "class_id": class_id,
                                       "user_authenticated": user_authenticated})


@router.post("/photo/{class_id}/{photo_id}", response_class=RedirectResponse)
async def photo_details(request: Request, photo_id: str, class_id: str, action: str = Form(...),
                        payload: dict = Depends(verify_jwt_cookie)):
        if payload is not None:
            photo = await Gallery.get(photo_id)

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
            return RedirectResponse(f"/{class_id}/{photo_id}", status_code=303)


        else:
            return RedirectResponse(f"/{class_id}/{photo_id}", status_code=303)


@router.post("/{class_id}/picture/upload", response_class=RedirectResponse)
async def upload_picture(request: Request, class_id: str, payload: dict = Depends(verify_jwt_cookie),
                         file_input: UploadFile = File(...)):
        if payload is not None:
            form = PhotoForm(request=request)
            await form.create_form_data()

            user = await User.get(payload["sub"])

            # Example path calculation assuming user.images is a valid attribute
            new_photo = Gallery(
                accepted=False,
                likes=0,
                dislikes=0,
                author=payload["sub"],
                path=user.images + 1,  # Example path calculation
                program=class_id,
                likes_who=[],
                dislikes_who=[],
                description=form.form_data["file_des"],
                title=form.form_data["file_name"]
            )
            user.images += 1
            photos = await Gallery.find().to_list()

            try:
                directory = f"C:/Users/hp/PycharmProjects/final project/static/images/published/{class_id}/{payload['sub']}"
                os.makedirs(directory, exist_ok=True)
                file_path = os.path.join(directory, f"{user.images}.jpg")
                Image.open(file_input.file).save(file_path)
                await user.save()
                await new_photo.insert()
                return RedirectResponse(f"/class/{class_id}", status_code=303)

            except Exception as err:
                print(err)  # Consider logging the error instead of just printing
                return RedirectResponse(f"/class/{class_id}", status_code=303)
        else:
            return RedirectResponse(f"/class/{class_id}", status_code=303)


@router.get("/{class_id}/delete/{photo_id}", response_class=RedirectResponse)
async def delete_photo(request: Request, class_id: str, photo_id: str, payload: dict = Depends(verify_jwt_cookie)):
    photo = await Gallery.get(photo_id)
    if payload is not None and (payload["sub"] == photo.author):
        try:
            await photo.delete()
            return RedirectResponse(f"/class/{class_id}", status_code=303)
        except Exception as err:
            print(err)
            return RedirectResponse(f"/{class_id}/{photo_id}", status_code=303)
    else:
        return RedirectResponse(f"/{class_id}/{photo_id}", status_code=303)

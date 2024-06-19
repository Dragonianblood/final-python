from fastapi import Request
from beanie import Document


class Gallery(Document):
    accepted: bool
    likes: int
    dislikes: int
    author: str
    path: int
    program: str
    likes_who: list
    dislikes_who: list

    class Settings:
        name = "gallery"


class PhotoForm:
    def __init__(self, request: Request):
        self.request: Request = request
        self.form_data = {}

    async def create_form_data(self):
        form = await self.request.form()
        for key, value in form.items():
            self.form_data[key] = value


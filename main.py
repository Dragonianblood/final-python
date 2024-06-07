from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import uvicorn

from routers import home

app=FastAPI()

app.include_router(home.router)
app.mount("/static", StaticFiles(directory="static"),name="static")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", reload=True)

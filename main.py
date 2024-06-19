from fastapi import FastAPI, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import uvicorn

from dependencies.database import connectToMongodb
from routers import home, auth
from auth.middleware import JWTBearer

app = FastAPI(lifespan=connectToMongodb)

app.include_router(home.router)
app.include_router(auth.router)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/protected", dependencies=[Depends(JWTBearer())], response_class=HTMLResponse)
async def protected_route():
    return "This is a protected route"

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", reload=True)

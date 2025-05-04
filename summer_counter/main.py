import uvicorn
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI()

app.mount(
    path="/static",
    app=StaticFiles(directory="./static", html=True),
    name="static"
)


@app.get("/")
async def send_home_page() -> FileResponse:
    return FileResponse("./static/index.html")


if __name__ == '__main__':
    uvicorn.run('main:app', host="127.0.0.1", port=1201, reload=True)

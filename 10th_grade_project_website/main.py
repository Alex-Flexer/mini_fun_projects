import uvicorn
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from dotenv import dotenv_values

app = FastAPI()

app.mount(
    path="/static",
    app=StaticFiles(directory="10th_grade_project_website/static", html=True),
    name="static"
)


@app.get("/")
async def send_home_page() -> FileResponse:
    return FileResponse("10th_grade_project_website/static/index.html")


if __name__ == '__main__':
    config = dotenv_values("10th_grade_project_website/.env")
    PORT = int(config["PORT"])
    HOST = config["HOST"]

    uvicorn.run('main:app', host=HOST, port=PORT, reload=True)

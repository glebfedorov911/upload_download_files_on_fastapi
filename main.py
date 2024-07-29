from fastapi import FastAPI, Request, File, UploadFile, HTTPException, status
from fastapi.templating import Jinja2Templates
from fastapi.responses import FileResponse

import uvicorn
import os


FILE_DIR = "./upload_file"

if not os.path.exists(FILE_DIR):
    os.makedirs(FILE_DIR)

app = FastAPI()

templates = Jinja2Templates(directory="templates")
files = ""

@app.get("/")
async def get(request: Request):
    return templates.TemplateResponse(
        request=request, name="upload.html"
    )

def get_unique_filename(directory, filename):
    base, extension = os.path.splitext(filename)
    counter = 1
    unique_filename = filename
    while os.path.exists(os.path.join(directory, unique_filename)):
        unique_filename = f"{base}_({counter}){extension}"
        counter += 1

    return unique_filename

@app.post("/uploadfile/")
async def upload_file(file: UploadFile = File(...)):
    global files
    unique_filename = files = get_unique_filename(FILE_DIR, file.filename)
    file_location = os.path.join(FILE_DIR, unique_filename)
    with open(file_location, "wb") as buffer:
        buffer.write(await file.read())

    return {
        "msg": f"{unique_filename} сохранен в {file_location}"
    }

@app.post("/downloadfiles/")
async def download_file():
    global files
    if not files:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Не указано имя, попробуйте найти по названию"
        )
    file_location = os.path.join(FILE_DIR, files)
    return FileResponse(
        path=file_location, filename=files
    )

@app.post("/downloadfiles/{filename}")
async def download_file_by_name(filename: str):
    file_location = os.path.join(FILE_DIR, filename)
    if not os.path.exists(file_location):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Нет такого файла"
        )
    return FileResponse(
        path=file_location, filename=filename
    )

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
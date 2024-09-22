import os
import zipfile
from io import BytesIO
from fastapi import APIRouter
from fastapi.responses import StreamingResponse

router = APIRouter()

async def download_db():
    print("\n>>>> API: download_db")
    directory = "./data/main_database"
    zip_io = BytesIO()
    with zipfile.ZipFile(zip_io, mode='w', compression=zipfile.ZIP_DEFLATED) as zip_file:
        for root, _, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                arc_name = os.path.relpath(file_path, directory)
                zip_file.write(file_path, arc_name)
    zip_io.seek(0)
    print("returning files")
    return StreamingResponse(
        zip_io, 
        media_type="application/zip",
        headers={"Content-Disposition": f"attachment; filename=db.zip"}
    )

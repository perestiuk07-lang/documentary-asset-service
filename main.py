import os
import tempfile

import yt_dlp
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

app = FastAPI()


class DownloadRequest(BaseModel):
    url: str


@app.get("/")
def health():
    return {"status": "ok"}


@app.post("/download")
def download_video(request: DownloadRequest):
    temp_dir = tempfile.mkdtemp()
    output_template = os.path.join(temp_dir, "video.%(ext)s")

    options = {
        "format": "best[ext=mp4]/best",
        "outtmpl": output_template,
        "noplaylist": True,
    }

    try:
        with yt_dlp.YoutubeDL(options) as ydl:
            info = ydl.extract_info(request.url, download=True)
            file_path = ydl.prepare_filename(info)

        if not os.path.exists(file_path):
            raise HTTPException(status_code=500, detail="Downloaded file not found")

        return FileResponse(
            file_path,
            media_type="video/mp4",
            filename="video.mp4",
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

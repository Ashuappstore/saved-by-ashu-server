import os
import uuid
import subprocess
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

COOKIE_PATH = "/tmp/cookies.txt"
if os.environ.get("YT_COOKIES"):
    with open(COOKIE_PATH, "w") as f:
        f.write(os.environ.get("YT_COOKIES"))


def cleanup(path: str):
    if os.path.exists(path):
        os.remove(path)


@app.get("/")
def home():
    return {"status": "alive", "service": "Saved by Ashu API"}


@app.get("/api/download")
@app.get("/download")
def download(
    url: str,
    background_tasks: BackgroundTasks,
    res: str = "720",
    ext: str = "mp4",
):
    if not url:
        raise HTTPException(status_code=400, detail="URL missing")

    fid = str(uuid.uuid4())
    is_audio = (res == "audio" or ext == "mp3")

    if is_audio:
        out = f"/tmp/{fid}.%(ext)s"
        cmd = [
            "yt-dlp",
            "-x",
            "--audio-format",
            "mp3",
            "--audio-quality",
            "0",
            "-o",
            out,
            url,
        ]
        final_file = f"/tmp/{fid}.mp3"
        media_type = "audio/mpeg"
        filename = "Saved_by_Ashu.mp3"
    else:
        height = res if res.isdigit() else "720"
        fmt = f"bestvideo[height<={height}][ext=mp4]+bestaudio[ext=m4a]/best[height<={height}][ext=mp4]/best[height<={height}]/best"
        out = f"/tmp/{fid}.%(ext)s"
        cmd = [
            "yt-dlp",
            "-f",
            fmt,
            "--merge-output-format",
            "mp4",
            "-o",
            out,
            url,
        ]
        final_file = f"/tmp/{fid}.mp4"
        media_type = "video/mp4"
        filename = f"Saved_by_Ashu_{height}p.mp4"

    if os.path.exists(COOKIE_PATH):
        cmd.extend(["--cookies", COOKIE_PATH])

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise HTTPException(status_code=500, detail=result.stderr[-300:])

    if not os.path.exists(final_file):
        raise HTTPException(status_code=500, detail="File processing failed")

    background_tasks.add_task(cleanup, final_file)
    return FileResponse(final_file, media_type=media_type, filename=filename)
    

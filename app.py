import os, uuid, subprocess
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

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

@app.get("/download")
def download(url: str, background_tasks: BackgroundTasks):
    if not url:
        raise HTTPException(status_code=400, detail="URL missing")
    fid = str(uuid.uuid4())
    out = f"/tmp/{fid}.%(ext)s"
    cmd = ["yt-dlp", "-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best", "--merge-output-format", "mp4", "-o", out, url]
    if os.path.exists(COOKIE_PATH):
        cmd.extend(["--cookies", COOKIE_PATH])
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        raise HTTPException(status_code=500, detail=res.stderr[-300:])
    final_file = f"/tmp/{fid}.mp4"
    if not os.path.exists(final_file):
        raise HTTPException(status_code=500, detail="Merge failed")
    background_tasks.add_task(cleanup, final_file)
    return FileResponse(final_file, media_type="video/mp4", filename="Saved_by_Ashu.mp4")
  

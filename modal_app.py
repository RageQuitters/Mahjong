import modal
from pathlib import Path
import sys

# Root directory (where modal_app.py is located)
ROOT_DIR = Path(__file__).resolve().parent

# Build the container image
image = (
    modal.Image.debian_slim()
    .apt_install(
        "libgl1-mesa-glx",  # OpenGL for cv2
        "libglib2.0-0",     # GTK dependencies
        "ffmpeg",           # if you use video reading
        "libsm6",           # additional deps for cv2
        "libxext6",         # additional deps for cv2
        "libxrender1"
    )
    .pip_install([
        "opencv-python",      # Python OpenCV
        "opencv-contrib-python",  # optional if you need extra modules
        "python-multipart"
    ])
    .pip_install_from_requirements(ROOT_DIR / "requirements.txt")
    .add_local_dir("backend", remote_path="/root/backend")
)

# Add container root to sys.path so Python can see backend
sys.path.append("/root")

# Create a Modal App
app = modal.App("mahjong-backend")

# Expose FastAPI app
@app.function(image=image)
@modal.asgi_app()
def fastapi_app():
    # Import FastAPI instance from backend/api/app.py
    from backend.api.app import app
    return app
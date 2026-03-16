import os
import uvicorn

print("Test the API locally at http://127.0.0.1:8000/docs#/default")

if __name__ == "__main__":
    # Render sets the PORT environment variable; default to 8000 for local
    PORT = int(os.environ.get("PORT", 8000))

    # Use reload=True only if running locally (PORT not set by Render)
    reload_flag = False if "PORT" in os.environ else True

    uvicorn.run(
        "api.app:app",  # Your FastAPI app path
        host="0.0.0.0",
        port=PORT,
        reload=reload_flag
    )
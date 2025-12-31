import uvicorn
print("Test the API here: http://127.0.0.1:8000/docs#/default")
if __name__ == "__main__":
    uvicorn.run(
        "api.app:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
    
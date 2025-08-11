import os
import uvicorn

def main():
    host = os.getenv("AGENTS_API_HOST", "0.0.0.0")
    port = int(os.getenv("AGENTS_API_PORT", "8088"))
    uvicorn.run("src.api.app:app", host=host, port=port, reload=os.getenv("RELOAD", "1") == "1")

if __name__ == "__main__":
    main()
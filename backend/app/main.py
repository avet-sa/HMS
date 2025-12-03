from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def read_root():
    return {"msg": "Hello from Hotel Management System Backend!"}

def main():
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

if __name__ == "__main__":
    main()
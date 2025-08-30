import uvicorn

def main():
    uvicorn.run("ucl_engine.api:app", host="127.0.0.1", port=8000, reload=False)

if __name__ == "__main__":
    main()

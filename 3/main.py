from fastapi import FastAPI, HTTPException


app = FastAPI()

@app.get("/get/{id}")
async def getById(id: int):
    id_list = [1, 2, 3, 4, 5]
    if id not in id_list:
        raise HTTPException(status_code=404, detail="您查找的新闻不存在")
    return {"id": id}
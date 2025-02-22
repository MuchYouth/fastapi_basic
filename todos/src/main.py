from fastapi import FastAPI
from api import todo, user

app = FastAPI()
app.include_router(todo.router)
app.include_router(user.router)

@app.get("/")
def heath_check_handler():
    return {"ping": "pong"}






# todo_data = {
#     1: {
#         "id": 1,
#         "contents": "실전 !  FastAPI 섹션 0 수강",
#         "is_done": True,
#     },
#     2: {
#         "id": 2,
#         "contents": "실전 !  FastAPI 섹션 1 수강",
#         "is_done": False,
#     },
#     3: {
#         "id": 3,
#         "contents": "실전 !  FastAPI 섹션 2 수강",
#         "is_done": False,
#     }
# }
from fastapi import FastAPI, Body, Path, Query, HTTPException
from typing import Optional
from pydantic import BaseModel, Field
from starlette import status

app = FastAPI()


class User:
    id: int
    name: str
    surname: str
    job: str
    age: int

    def __init__(self, id: int, name: str, surname: str, job: str, age: int):
        self.id = id
        self.name = name
        self.surname = surname
        self.job = job
        self.age = age


class UserRequest(BaseModel):
    id: Optional[int] = Field(description="The id of the user, optional", default=None)
    name: str = Field(min_length=3)
    surname: str
    job: str
    age: int = Field(gt=15, lt=80)

    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "Serkan",
                "surname": "Ozdemir",
                "job": "Developer",
                "age": 23
            }
        }
    }


user_db = [
    User(id=1, name="Serkan", surname="Özdemir", job="Software Engineer", age=30),
    User(id=2, name="İlyas", surname="İlhan", job="Frontend Developer", age=28),
    User(id=3, name="Emre", surname="Şimşek", job="Backend Developer", age=27),
    User(id=4, name="Ahmet", surname="Demir", job="Data Scientist", age=35),
    User(id=5, name="Mehmet", surname="Yılmaz", job="AI Engineer", age=32)
]


@app.get(path="/users", status_code=status.HTTP_200_OK)
async def get_all_users():
    return user_db


@app.get(path="/users/{user_id}", status_code=status.HTTP_200_OK)
async def get_user_by_id(user_id: int = Path(gt=0)):
    for user in user_db:
        if user.id == user_id:
            return user
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found!")


@app.get(path="/users/")
async def get_user_by_age(user_age: int = Query(gt=0, lt=80)):
    users_to_return = []
    for user in user_db:
        if user.age == user_age:
            users_to_return.append(user)
    return users_to_return


@app.post(path="/create-user", status_code=status.HTTP_201_CREATED)
async def create_user(user_request: UserRequest):
    new_user = User(**user_request.model_dump())
    user_db.append(find_user_id(new_user))


def find_user_id(user: User):
    user.id = 1 if len(user_db) == 0 else user_db[-1].id + 1
    return user


@app.put(path="/users/update-user", status_code=status.HTTP_204_NO_CONTENT)
async def update_user(user_request: UserRequest):
    user_updated = False
    for i in range(len(user_db)):
        if user_db[i].id == user_request.id:
            user_db[i] = user_request
            user_updated = True
    if not user_updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")


@app.delete(path="/users/delete/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int = Path(gt=0)):
    user_deleted = False
    for i in range(len(user_db)):
        if user_db[i].id == user_id:
            user_db.pop(i)
            user_deleted = True
            break
    if not user_deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

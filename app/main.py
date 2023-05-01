#mealapp
from fastapi import FastAPI, WebSocket, Depends
from . import  models
from .database import engine 
from .routers import user,auth,recipe,ingredient
from fastapi.middleware.cors import CORSMiddleware

from sqlalchemy.orm import Session
from . import models, schemas, utils, oauth2
from .database import engine , get_db
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

origins = [
    "http://localhost:3000",
    "http://localhost:8080",
    "http://localhost:8081",
    "http://localhost:8082",
    "http://localhost:8083",
    "http://localhost:81",
    "http://localhost:80",
    "http://127.0.0.1:8000",
    "http://localhost:5173"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*","users","/users"],
    allow_headers=["*"],
)

app.include_router(user.router)
app.include_router(auth.router)
app.include_router(recipe.router)
app.include_router(ingredient.router)



#websocket to get ingredients in user's shopping list
@app.websocket('/ws/shopping')
async def websocket_get_shopping_list(websocket: WebSocket, db: Session = Depends(get_db)):
    await websocket.accept()

    # Retrieve all Shopping objects for the current user
    print('hello')
    shopping_list = db.query(models.Shopping).filter_by(user_id=1).all()

    # Create an empty list to hold the ingredients
    ingredients = []

    # Map the ingredient_id foreign key to the ingredients table
    for item in shopping_list:
        ingredient = db.query(models.Ingredient).get(item.ingredient_id)
        if ingredient:
            # Append the ingredient to the list
            ingredients.append(ingredient)

    # Send the list of ingredients in the shopping list over the websocket
    await websocket.send_json({"ingredients": [schemas.IngredientCreate.from_orm(ing).dict() for ing in ingredients]})

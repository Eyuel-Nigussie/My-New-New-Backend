from .. import models, schemas, utils, oauth2
from fastapi import status, HTTPException, Depends, APIRouter, FastAPI, WebSocket
from sqlalchemy.orm import Session
from fastapi.params import Body
from ..database import engine , get_db
from typing import List
from pydantic import BaseModel


from ..models import Recipe, Recipe_Ingredient, Ingredient, Step, Shopping, Preference, UserPreference
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from celery import Celery
from fastapi import BackgroundTasks
from time import sleep
from ..oauth2 import get_current_user
from ..utils import send_email
# Create a SQLAlchemy engine and sessionmaker
engine = create_engine("postgresql://user:password@localhost/mydatabase")
Session = sessionmaker(bind=engine)
# celery = Celery(__name__)  # 
celery = Celery('myapp', broker='pyamqp://guest@localhost//', backend='redis://localhost:6379/0')
class RecipeCreate(BaseModel):
    name: str
    description: str = None
    picture: str = "https://southernspicesrestaurant.com/img/placeholders/comfort_food_placeholder.png"
    cooking_time: str = None
    collection: str = None
    user_id: int
    ingredient_ids: list[int]
    quantities: list[float]
    units: list[str]



app = FastAPI()

router = APIRouter(
   prefix="/recipes",
    tags=["recipes"]
)

@celery.task 
def send_success_email(sender_email: str, recipient_email: str, recipe_name: str):
    from_email = sender_email
    to_email = recipient_email
    subject = "Success! Your recipe has been added to the database."
    body = f"Congratulations! Your recipe {recipe_name} has been successfully added to the database."
    send_email(from_email, to_email, subject, body)

def send_success_email(user_email: str, recipe_name: str):
    send_email(user_email, f"Success! Your recipe {recipe_name} has been added to the database.")


#get the ingredients of a recipe
@router.get("/ingredients/{id}")
def get_recipes(id: int, db: Session = Depends(get_db), user_id: int = Depends(oauth2.get_current_user) ):
    query = db.query(models.Recipe_Ingredient, models.Recipe, models.Ingredient)\
             .filter(models.Recipe.id == id)\
             .join(models.Recipe, models.Recipe.id == models.Recipe_Ingredient.recipe_id)\
             .join(models.Ingredient, models.Ingredient.id == models.Recipe_Ingredient.ingredients_id)
    
    results = [] # to store the results

    #loop through the query results and add them to the results
    for recipe_ingredient, recipe, ingredient in query:
       results.append({
          'recipe_id': recipe.id,
          'recipe_name': recipe.name,
          'ingredient_id': ingredient.id,
          'ingredient_name': ingredient.name,
          'quantity': recipe_ingredient.quantity,
          'unit': recipe_ingredient.unit
       })

    if not results:
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"ingredients for recipe with id{id} does not exits")
    #return the results as a json object
    return  {'results': results}


# get the steps
@router.get("/steps")
def get_steps(db: Session = Depends(get_db), user_id: int = Depends(oauth2.get_current_user)):
    recipes = db.query(models.Recipe).all()
    if not recipes:
        raise HTTPException(status_code=404, detail="No recipes found")
    #convert to recipe objects to dictionary format
    recipe_list = []
    for recipe in recipes:
         recipe_dict = {'id': recipe.id, 'name': recipe.name, 'description': recipe.description, 'picture': recipe.picture,
                        'cooking_time': recipe.cooking_time, 'collection': recipe.collection, 'user_id': recipe.user_id,
                        'steps': []}
         for step in recipe.steps:
             recipe_dict['steps'].append({'id': step.id, 'step_number': step.step_number, 'description': step.description})
         recipe_list.append(recipe_dict)

    return recipe_list


#post the steps
@router.post("/steps")
async def create_recipe(recipe: dict = Body(...), db: Session = Depends(get_db)):
    # Create a new Recipe object from the incoming data
    new_recipe = models.Recipe(name=recipe['name'], description=recipe['description'], picture=recipe['picture'],
                        cooking_time=recipe['cooking_time'], collection=recipe['collection'], user_id=recipe['user_id'])

    # Create a list of Step objects from the incoming data
    steps = [models.Step(step_number=step['step_number'], description=step['description']) for step in recipe['steps']]

    # Add the steps to the new recipe
    new_recipe.steps = steps

    # Add the new recipe to the database
    db.add(new_recipe)
    db.commit()
    db.refresh(new_recipe)

    # Return the newly created recipe
    return new_recipe

             

#Post Recipe
@router.post("/")
def create_recipe(recipe_data: dict = Body(...), db: Session = Depends(get_db), current_user = Depends(oauth2.get_current_user)):

    # Create a new Recipe object from the incoming data
    new_recipe = Recipe(
        name=recipe_data['name'],
        description=recipe_data['description'],
        picture=recipe_data['picture'],
        cooking_time=recipe_data['cooking_time'],
        collection=recipe_data['collection'],
        user_id=current_user.id,
    )

    # Create a list of Step objects from the incoming data
    steps = [Step(step_number=step['step_number'], description=step['description']) for step in recipe_data['steps']]

    # Add the steps to the new recipe
    new_recipe.steps = steps

    # Create Recipe_Ingredient objects for each ingredient in the request
    for i, ingredient_id in enumerate(recipe_data['ingredient_ids']):
        # Look up the Ingredient object in the database
        ingredient = db.query(Ingredient).get(ingredient_id)

        # If the ingredient doesn't exist, raise an HTTPException
        if not ingredient:
            raise HTTPException(status_code=404, detail=f"Ingredient with id {ingredient_id} not found")

        # Create a new Recipe_Ingredient object
        recipe_ingredient = Recipe_Ingredient(
            recipe=new_recipe,
            ingredient=ingredient,
            quantity=recipe_data['quantities'][i],
            unit=recipe_data['units'][i]
        )

        # Add the new Recipe_Ingredient object to the session
        db.add(recipe_ingredient)

    # Add the new recipe to the database
    db.add(new_recipe)
    db.commit()
    db.refresh(new_recipe)


    # Send success email
    # sender_email = "eyuthedev@gmail.com"
    # recipient_email = current_user.username
    # print(current_user)
    # recipient_email = "eyuelnigussie2@gmail.com"
    # max = send_success_email.delay(sender_email, recipient_email, new_recipe.name)
    # print(max)
    # Return the newly created recipe
    return new_recipe


@router.post("/recipes/")
def create_recipe(recipe_data: dict = Body(...), db: Session = Depends(get_db), current_user = Depends(oauth2.get_current_user)):

    # Create a new Recipe object from the incoming data
    new_recipe = Recipe(
        name=recipe_data['name'],
        description=recipe_data['description'],
        picture=recipe_data['picture'],
        cooking_time=recipe_data['cooking_time'],
        collection=recipe_data['collection'],
        user_id=current_user.id,
    )

    # Create a list of Step objects from the incoming data
    steps = [Step(step_number=step['step_number'], description=step['description']) for step in recipe_data['steps']]

    # Add the steps to the new recipe
    new_recipe.steps = steps

    # Create Recipe_Ingredient objects for each ingredient in the request
    for i, ingredient_id in enumerate(recipe_data['ingredient_ids']):
        # Look up the Ingredient object in the database
        ingredient = db.query(Ingredient).get(ingredient_id)

        # If the ingredient doesn't exist, raise an HTTPException
        if not ingredient:
            raise HTTPException(status_code=404, detail=f"Ingredient with id {ingredient_id} not found")

        # Create a new Recipe_Ingredient object
        recipe_ingredient = Recipe_Ingredient(
            recipe=new_recipe,
            ingredient=ingredient,
            quantity=recipe_data['quantities'][i],
            unit=recipe_data['units'][i],
        )

        # Add the new Recipe_Ingredient object to the session
        db.add(recipe_ingredient)

    # Add the new recipe to the database
    db.add(new_recipe)
    db.commit()
    db.refresh(new_recipe)

    # Add preferences to the new recipe
    for preference_name in recipe_data['preferences']:
        # Look up the Preference object in the database
        preference = db.query(Preference).filter_by(name=preference_name).first()

        # If the preference doesn't exist, create a new one
        if not preference:
            preference = Preference(name=preference_name)
            db.add(preference)
            db.commit()

        # Create a new recipe_preference object
        recipe_preference = recipe_preference(recipe=new_recipe, preference=preference)

        # Add the new recipe_preference object to the session
        db.add(recipe_preference)

    # Commit the session to the database
    db.commit()

    # Send success email
    sender_email = "eyuthedev@gmail.com"
    recipient_email = "eyuelnigussie2@gmail.com"
    max = send_success_email.delay(sender_email, recipient_email, new_recipe.name)
    print(max)
    # Return the newly created recipe
    return new_recipe


#get all recipes
@router.get("/")
async def get_recipes(db: Session = Depends(get_db),current_user = Depends(oauth2.get_current_user)):
    # Retrieve all Recipe objects
    recipes = db.query(Recipe).all()

    # Create a list to hold serialized recipe dictionaries
    recipe_list = []

    # Loop through each recipe
    for recipe in recipes:
        # Retrieve the Recipe_Ingredient objects for the recipe
        recipe_ingredients = recipe.ingredients

        # Retrieve the Step objects for the recipe
        steps = recipe.steps

        # Serialize the Recipe object and its related objects to a dictionary
        recipe_dict = recipe.__dict__
        recipe_dict['ingredients'] = [ri.ingredient.__dict__ for ri in recipe_ingredients]
        recipe_dict['steps'] = [step.__dict__ for step in steps]

        # Remove unwanted attributes from the dictionary
        del recipe_dict['_sa_instance_state']

        # Append the serialized recipe dictionary to the list
        recipe_list.append(recipe_dict)

    # Return the list of serialized recipe dictionaries as a JSON response
    return recipe_list



#get recipe with id 
@router.get("/recipes/{recipe_id}")
async def get_recipe(recipe_id: int, db: Session = Depends(get_db)):
    # Retrieve the Recipe object with the given ID
    recipe = db.query(Recipe).filter_by(id=recipe_id).first()

    # If the recipe doesn't exist, raise an HTTPException
    if not recipe:
        raise HTTPException(status_code=404, detail=f"Recipe with id {recipe_id} not found")

    # Retrieve the Recipe_Ingredient objects for the recipe
    recipe_ingredients = recipe.ingredients

    # Retrieve the Step objects for the recipe
    steps = recipe.steps

    # Serialize the Recipe object and its related objects to a dictionary
    recipe_dict = recipe.__dict__
    recipe_dict['ingredients'] = [ri.ingredient.__dict__ for ri in recipe_ingredients]
    recipe_dict['steps'] = [step.__dict__ for step in steps]

    # Remove unwanted attributes from the dictionary
    del recipe_dict['_sa_instance_state']

    # Return the serialized recipe as a JSON response
    return recipe_dict


@router.delete("/{recipe_id}")
def delete_recipe(recipe_id: int, db: Session = Depends(get_db), current_user = Depends(oauth2.get_current_user)):
    # Retrieve the Recipe object by id
    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()

    # If the Recipe object doesn't exist, raise an HTTPException
    if not recipe:
        raise HTTPException(status_code=404, detail=f"Recipe with id {recipe_id} not found")
    print(repr(recipe.user_id))
    print(repr(current_user.id))
    # If the Recipe object's user_id doesn't match the current user's id, raise an HTTPException
    if recipe.user_id != int(current_user.id):
        raise HTTPException(status_code=403, detail="You do not have permission to delete this recipe")

    # Delete the related Recipe_Ingredient objects
    db.query(Recipe_Ingredient).filter(Recipe_Ingredient.recipe_id == recipe_id).delete()

    # Delete the related Step objects
    db.query(Step).filter(Step.recipe_id == recipe_id).delete()

    # Delete the Recipe object
    db.delete(recipe)

    db.commit()

    # Return a success message
    return {"message": f"Recipe with id {recipe_id}, its corresponding Recipe_Ingredient objects, and Steps have been deleted"}



@router.get("/count")
async def get_recipe_count(db: Session = Depends(get_db)):
    # Retrieve all Recipe objects
    recipes = db.query(Recipe).all()

    # Count the recipes for each collection
    dinner_count = sum(1 for recipe in recipes if recipe.collection == "Dinner")
    supper_count = sum(1 for recipe in recipes if recipe.collection == "Supper")
    lunch_count = sum(1 for recipe in recipes if recipe.collection == "Lunch")
    breakfast_count = sum(1 for recipe in recipes if recipe.collection == "Breakfast")

    # Return the counts for each collection
    return {
        "dinner_count": dinner_count,
        "supper_count": supper_count,
        "lunch_count": lunch_count,
        "breakfast_count": breakfast_count
    }


# POST request to add ingredient to shopping list
@router.post("/shopping/{ingredient_id}")
def add_to_shopping_list(ingredient_id: int, db: Session = Depends(get_db), current_user = Depends(oauth2.get_current_user)):
    # Look up the Ingredient object in the database
    ingredient = db.query(Ingredient).get(ingredient_id)

    # If the ingredient doesn't exist, raise an HTTPException
    if not ingredient:
        raise HTTPException(status_code=404, detail=f"Ingredient with id {ingredient_id} not found")

    # Create a new Shopping object
    new_shopping_item = Shopping(
        ingredient_id=ingredient_id,
        user_id=current_user.id,
    )

    # Add the new Shopping object to the session
    db.add(new_shopping_item)
    db.commit()
    db.refresh(new_shopping_item)

    # Return the newly created Shopping object
    return new_shopping_item


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
    await websocket.send_json({"ingredients": [schemas.Ingredient.from_orm(ing).dict() for ing in ingredients]})




# GET request to get ingredients in user's shopping list
@router.get("/shopping")
def get_shopping_list(db: Session = Depends(get_db), current_user = Depends(oauth2.get_current_user)):
    # Retrieve all Shopping objects for the current user
    shopping_list = db.query(Shopping).filter_by(user_id=current_user.id).all()

    # Create an empty list to hold the ingredients
    ingredients = []

    # Map the ingredient_id foreign key to the ingredients table
    for item in shopping_list:
        ingredient = db.query(Ingredient).get(item.ingredient_id)
        if ingredient:
            # Append the ingredient to the list
            ingredients.append(ingredient)

    # Return the list of ingredients in the shopping list
    return ingredients

@router.post("/preferences")
async def create_preferences(preferences: List[str] = Body(...), db: Session = Depends(get_db), current_user = Depends(oauth2.get_current_user)):
    print(preferences)
    # Retrieve the user from the database
    user = db.query(models.User).filter(models.User.id == current_user.id).first()

    # Create a list of Preference objects from the incoming data
    preference_objects = [models.Preference(name=name) for name in preferences]

    db.add_all(preference_objects)
    db.commit()

    # Create a list of UserPreference objects to link the preferences to the user
    user_preference_objects = [models.UserPreference(user=user, preference=preference) for preference in preference_objects]

    db.add_all(user_preference_objects)
    db.commit()

    return {"success": True}


#get recipes with user preference
# @router.get("/suggestion")
# async def get_recipes(db: Session = Depends(get_db), current_user = Depends(oauth2.get_current_user)):
#     # Retrieve the user's preferences
#     preferences = db.query(UserPreference.preference_id).filter(UserPreference.user_id == current_user.id).all()

#     # Extract the preference IDs into a list
#     preference_ids = [p[0] for p in preferences]

#     # Retrieve the recipes that have category matching with the user's preferences
#     recipes = db.query(Recipe).filter(Recipe.collection.in_(preference_ids)).all()

#     # Create a list to hold serialized recipe dictionaries
#     recipe_list = []

#     # Loop through each recipe
#     for recipe in recipes:
#         # Retrieve the Recipe_Ingredient objects for the recipe
#         recipe_ingredients = recipe.ingredients

#         # Retrieve the Step objects for the recipe
#         steps = recipe.steps

#         # Serialize the Recipe object and its related objects to a dictionary
#         recipe_dict = recipe.__dict__
#         recipe_dict['ingredients'] = [ri.ingredient.__dict__ for ri in recipe_ingredients]
#         recipe_dict['steps'] = [step.__dict__ for step in steps]

#         # Remove unwanted attributes from the dictionary
#         del recipe_dict['_sa_instance_state']

#         # Append the serialized recipe dictionary to the list
#         recipe_list.append(recipe_dict)

#     # Return the list of serialized recipe dictionaries as a JSON response
#     return recipe_list

# @router.get("/suggestion")
# async def get_recipes(db: Session = Depends(get_db), current_user = Depends(oauth2.get_current_user)):
#     # Retrieve the user's preferences
#     preferences = [p.name for p in current_user.preferences]

#     # Retrieve the recipes that match the user's preferences
#     recipes = db.query(Recipe).filter(Recipe.collection.in_(preferences)).all()

#     # Serialize the recipe objects and their related objects to a list of dictionaries
#     recipe_list = []
#     for recipe in recipes:
#         recipe_dict = recipe.__dict__
#         recipe_dict['ingredients'] = [ri.ingredient.__dict__ for ri in recipe.ingredients]
#         recipe_dict['steps'] = [step.__dict__ for step in recipe.steps]
#         del recipe_dict['_sa_instance_state']
#         recipe_list.append(recipe_dict)

#     # Return the list of serialized recipe dictionaries as a JSON response
#     return recipe_list

@router.get("/suggestion")
async def get_recipes_by_preferences(db: Session = Depends(get_db), current_user = Depends(oauth2.get_current_user)):
    # Retrieve the user from the database
    user = db.query(models.User).filter(models.User.id == current_user.id).first()

    # Retrieve the user's preferences
    preferences = [up.preference for up in user.preferences]

    # Retrieve the recipes that match the user's preferences
    recipes = db.query(models.Recipe).filter(models.Recipe.collection.in_([p.name for p in preferences])).all()

    # Create a list to hold serialized recipe dictionaries
    recipe_list = []

   # Loop through each recipe
    for recipe in recipes:
        # Retrieve the Recipe_Ingredient objects for the recipe
        recipe_ingredients = recipe.ingredients

        # Retrieve the Step objects for the recipe
        steps = recipe.steps

        # Serialize the Recipe object and its related objects to a dictionary
        recipe_dict = recipe.__dict__
        recipe_dict['ingredients'] = [ri.ingredient.__dict__ for ri in recipe_ingredients]
        recipe_dict['steps'] = [step.__dict__ for step in steps]

        # Remove unwanted attributes from the dictionary
        del recipe_dict['_sa_instance_state']

        # Append the serialized recipe dictionary to the list
        recipe_list.append(recipe_dict)

    # Return the list of serialized recipe dictionaries as a JSON response
    return recipe_list




    















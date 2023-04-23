from .. import models, schemas, utils, oauth2
from fastapi import status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from fastapi.params import Body
from ..database import engine , get_db
from typing import List
router = APIRouter(
   prefix="/recipes",
    tags=["recipes"]
)


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_recipes(ingredient_ids: schemas.RecipeIngredients, recipe: schemas.RecipeCreate, db: Session = Depends(get_db), user_id: int = Depends(oauth2.get_current_user)):
      new_recipe = models.Recipe(
      user_id = user_id.id,
      **dict(recipe)
      )
      db.add(new_recipe)
      db.commit()
      db.refresh(new_recipe)
   
    #   for ingredient_id in ingredient_ids:
    #       db_ingredient = db.query(models.Ingredient).get(ingredient_id)
    #       if db_ingredient is None:
    #           raise HTTPException(status_code=404, detail=f"Ingredient with id {ingredient_id} not found")
          
    #       db_recipe_ingredient = models.Recipe_Ingredient(
    #           recipe_id = new_recipe.id,
    #           ingredient_id = db_ingredient.id
    #       )
    #       db.add(db_recipe_ingredient)
    #       db.commit()
    #       db.refresh(db_recipe_ingredient)




    #store the ingredients
   # for ingredient in ingredients:
      # db_ingredient = models.Ingredient( **ingredient.dict())
      # db.add(db_ingredient)
      # db.commit()
      # db.refresh(db_ingredient)
      

#get all recipes
@router.get("/", response_model=List[schemas.RecipeCreate])
def get_recipes(db: Session = Depends(get_db), user_id: int = Depends(oauth2.get_current_user)):
    recipes = db.query(models.Recipe).all()
    return recipes


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

             
   
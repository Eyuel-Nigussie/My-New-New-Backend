from .. import models, schemas, utils, oauth2
from fastapi import status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from fastapi.params import Body
from ..database import engine , get_db
from typing import List
from pydantic import BaseModel


from ..models import Recipe, Recipe_Ingredient, Ingredient, Step
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Create a SQLAlchemy engine and sessionmaker
engine = create_engine("postgresql://user:password@localhost/mydatabase")
Session = sessionmaker(bind=engine)

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





router = APIRouter(
   prefix="/recipes",
    tags=["recipes"]
)


# @router.post("/", status_code=status.HTTP_201_CREATED)
# def create_recipes(ingredient_ids: schemas.RecipeIngredients, recipe: schemas.RecipeCreate, db: Session = Depends(get_db), user_id: int = Depends(oauth2.get_current_user)):
#       new_recipe = models.Recipe(
#       user_id = user_id.id,
#       **dict(recipe)
#       )
#       db.add(new_recipe)
#       db.commit()
#       db.refresh(new_recipe)
   
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
# @router.get("/", response_model=List[schemas.RecipeCreate])
# @router.get("/")
# def get_recipes(db: Session = Depends(get_db), user_id: int = Depends(oauth2.get_current_user)):
#     recipes = db.query(models.Recipe).all()
#     return recipes


# @router.post("/")
# async def create_recipe(recipe: schemas.RecipeCreate, ingredients: List[schemas.IngredientCreate], db: Session = Depends(get_db)):
#     # Create the recipe
#     db_recipe = models.Recipe(**recipe.dict())
#     db.add(db_recipe)
#     db.commit()
#     db.refresh(db_recipe)

#     # Create the recipe ingredients
#     for ingredient in ingredients:
#         print(ingredients)
#         db_ingredient = db.query(models.Ingredient).filter(models.Ingredient.name == ingredient.name).first()
#         if not db_ingredient:
#             db_ingredient = models.Ingredient(**ingredient.dict())
#             db.add(db_ingredient)
#             db.commit()
#             db.refresh(db_ingredient)

#         db_recipe_ingredient = schemas.RecipeIngredientCreate(recipe_id=db_recipe.id, ingredient_id=db_ingredient.id, **ingredient.dict())
#         db_recipe_ingredient = models.Recipe_Ingredient(**db_recipe_ingredient.dict())
#         db.add(db_recipe_ingredient)
#         db.commit()
#         db.refresh(db_recipe_ingredient)

# @router.post('/ingredients/')
# def create_ingredient(ingredient: schemas.IngredientCreate, db: Session = Depends(get_db)):
#     db_ingredient = models.Ingredient(**ingredient.dict())
#     db.add(db_ingredient)
#     db.commit()
#     db.refresh(db_ingredient)
#     return db_ingredient


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

    # Return the newly created recipe
    return new_recipe





    # try:
        # Create a new Recipe object from the request body
    #     new_recipe = Recipe(
    #         name=recipe.name,
    #         description=recipe.description,
    #         picture=recipe.picture,
    #         cooking_time=recipe.cooking_time,
    #         collection=recipe.collection,
    #         user_id=recipe.user_id,
    #     )

    #     # Add the new Recipe object to the session
    #     db.add(new_recipe)

    #     # Create Recipe_Ingredient objects for each ingredient in the request
    #     for i, ingredient_id in enumerate(recipe.ingredient_ids):
    #         # Look up the Ingredient object in the database
    #         ingredient = db.query(Ingredient).get(ingredient_id)

    #         # If the ingredient doesn't exist, raise an HTTPException
    #         if not ingredient:
    #             raise HTTPException(status_code=404, detail=f"Ingredient with id {ingredient_id} not found")

    #         # Create a new Recipe_Ingredient object
    #         recipe_ingredient = Recipe_Ingredient(
    #             recipe=new_recipe,
    #             ingredient=ingredient,
    #             quantity=recipe.quantities[i],
    #             unit=recipe.units[i],
    #         )

    #         # Add the new Recipe_Ingredient object to the session
    #         db.add(recipe_ingredient)

    #     # Commit the session to the database
    #     db.commit()

    #     # Return the new recipe as a dictionary
    #     return new_recipe.__dict__

    # # except Exception as e:
    #     # If an error occurs, rollback the session and raise an HTTPException
    #     print(e)
    #     db.rollback()
    #     print(e)
    #     raise HTTPException(status_code=500, detail=str(e))

    # # finally:
    #     # Close the session
    #     db.close()


#get all recipes
@router.get("/")
async def get_recipes(db: Session = Depends(get_db)):
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


@router.get("/dinner")
async def get_dinner_recipes(db: Session = Depends(get_db)):
    # Retrieve all Recipe objects where collection is equal to "dinner"
    recipes = db.query(Recipe).filter(Recipe.collection == "dinner").all()

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


@router.get("/dinner/count")
async def get_dinner_recipes_count(db: Session = Depends(get_db)):
    # Retrieve all Recipe objects where collection is equal to "dinner"
    recipes = db.query(Recipe).filter(Recipe.collection == "dinner").all()

    # Return the count of the recipes where collection is equal to "dinner"
    return len(recipes)


@router.get("/supper")
async def get_dinner_recipes(db: Session = Depends(get_db)):
    # Retrieve all Recipe objects where collection is equal to "dinner"
    recipes = db.query(Recipe).filter(Recipe.collection == "supper").all()

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

@router.get("/supper/count")
async def get_dinner_recipes_count(db: Session = Depends(get_db)):
    # Retrieve all Recipe objects where collection is equal to "dinner"
    recipes = db.query(Recipe).filter(Recipe.collection == "supper").all()

    # Return the count of the recipes where collection is equal to "dinner"
    return len(recipes)


@router.get("/lunch")
async def get_dinner_recipes(db: Session = Depends(get_db)):
    # Retrieve all Recipe objects where collection is equal to "dinner"
    recipes = db.query(Recipe).filter(Recipe.collection == "lunch").all()

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

@router.get("/lunch/count")
async def get_dinner_recipes_count(db: Session = Depends(get_db)):
    # Retrieve all Recipe objects where collection is equal to "dinner"
    recipes = db.query(Recipe).filter(Recipe.collection == "lunch").all()

    # Return the count of the recipes where collection is equal to "dinner"
    return len(recipes)


@router.get("/breakfast")
async def get_dinner_recipes(db: Session = Depends(get_db)):
    # Retrieve all Recipe objects where collection is equal to "dinner"
    recipes = db.query(Recipe).filter(Recipe.collection == "lunch").all()

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

@router.get("/breakfast/count")
async def get_dinner_recipes_count(db: Session = Depends(get_db)):
    # Retrieve all Recipe objects where collection is equal to "dinner"
    recipes = db.query(Recipe).filter(Recipe.collection == "breakfast").all()

    # Return the count of the recipes where collection is equal to "dinner"
    return len(recipes)
from .. import models, schemas, utils, oauth2
from fastapi import status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from ..database import engine , get_db
from typing import List
router = APIRouter(
   prefix="/recipes",
    tags=["recipes"]
)

#RecipeCreate is inbound request validation 
#while UserOut is outbound response validation
#db: Session... is querying the database and give us final user

# to create a post you need to be authenticated, so here are the steps
# add get_current_user from oauth2.py to def method params as dependent
# =>user_id: int = Depends(oauth2.get_current_user)
@router.post("/", status_code=status.HTTP_201_CREATED)
def create_recipes(recipe: schemas.RecipeCreate,db: Session = Depends(get_db), user_id: int = Depends(oauth2.get_current_user)):
   # cursor.execute("""Insert INTO posts (title, content, published) VALUES (%S,%S,%S)""")
   # return {"data": post_dict}

   new_recipe = models.Recipe(
      # title=post.title, content=post.content, published=post.published
      user_id = user_id.id,
      **recipe.dict() 
      )
   db.add(new_recipe)
   db.commit()
   db.refresh(new_recipe)
   return  new_recipe


@router.get("/", response_model=List[schemas.Recipes])
def get_recipes(db: Session = Depends(get_db), user_id: int = Depends(oauth2.get_current_user) ):
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



             
   
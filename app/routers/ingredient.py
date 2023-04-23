from .. import models, schemas, utils, oauth2
from fastapi import status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from ..database import engine , get_db
from typing import List
router = APIRouter(
   prefix="/ingredients",
    tags=["/ingredients"]
)

#RecipeCreate is inbound request validation 
#while UserOut is outbound response validation
#db: Session... is querying the database and give us final user

# to create a post you need to be authenticated, so here are the steps
# add get_current_user from oauth2.py to def method params as dependent
# =>user_id: int = Depends(oauth2.get_current_user)
# @router.post("/", status_code=status.HTTP_201_CREATED)
# def create_posts(recipe: schemas.RecipeCreate,db: Session = Depends(get_db), user_id: int = Depends(oauth2.get_current_user)):
#    # cursor.execute("""Insert INTO posts (title, content, published) VALUES (%S,%S,%S)""")
#    # return {"data": post_dict}

#    new_recipe = models.Recipe(
#       # title=post.title, content=post.content, published=post.published
#       user_id = user_id.id,
#       **recipe.dict() 
#       )
#    db.add(new_recipe)
#    db.commit()
#    db.refresh(new_recipe)
#    return  new_recipe

#get all ingredients

@router.get('/',response_model=List[schemas.IngredientOut])
def get_user(db: Session = Depends(get_db), user_id: int = Depends(oauth2.get_current_user)):
   ingredients = db.query(models.Ingredient).all()
   if not ingredients:
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"ingredients empty")
   return ingredients

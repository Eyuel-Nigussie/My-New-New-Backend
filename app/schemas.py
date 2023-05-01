from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List, Dict

#===========user schema =================
class UserCreate(BaseModel): 
    name: str
    email: EmailStr
    password: str

class UserOut(BaseModel):  #return response
   id: str
   name: Optional[str] = None  
   email: EmailStr
   class Config:
    orm_mode = True

class UserLogin(BaseModel):
   email: EmailStr
   password: str

#schema for token out
class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserOut

#data we embeded into access token
class TokenData(BaseModel):
    id: Optional[str] = None


#=========== recipe schema =================
# class RecipeCreate(BaseModel):
#     name: str
#     description: Optional[str] = None
#     cooking_time: Optional[str] = None
#     collection: str = None
#     picture: Optional[str] = None


#========== Ingredient schema =================================
class IngredientOut(BaseModel):  #return response
   id: int
   name: str 
   carbs: float
   protein: float
   fat: float
   calory: float

   class Config:
    orm_mode = True

class IngredientCreate(BaseModel):
    name: str
    carbs: float
    protein: float
    fat: float
    calory: float
    user_id: int = None

    class Config:
     orm_mode = True
class RecipeIngredientCreate(BaseModel):
    ingredient_id: int
    quantity: float
    unit: str

#recipe create
class RecipeCreate(BaseModel):
    name: str
    description: str = None
    picture: str = None
    cooking_time: str = None
    collection: str = None
    user_id: int

    ingredients: list[RecipeIngredientCreate]
    # name: str
    # description: Optional[str] = None
    # cooking_time: Optional[str] = None
    # collection: str = None
    # picture: Optional[str] = None 
    


# class IngredientCreate(BaseModel):
#    name: str
#    carbs: float
#    protein: float
#    fat: float
#    calorie: float
#    class Config:
#        orm_mode = True


class RecipeCreateWithIngredients(BaseModel):
    ingredient_ids: List[int]
  

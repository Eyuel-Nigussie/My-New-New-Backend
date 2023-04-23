from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

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
class RecipeCreate(BaseModel):
    name: str
    description: Optional[str] = None
    cooking_time: Optional[str] = None
    collection: str = None
    picture: Optional[str] = None


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

class Recipes(BaseModel):
   id: int
   name: str
   description: str
   cooking_time: str
   collection: str
   picture: str
   
   class Config:
    orm_mode = True

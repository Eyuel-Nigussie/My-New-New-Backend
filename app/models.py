from sqlalchemy import Boolean, Column, Integer, String, Float, LargeBinary, ForeignKey # to create column and it's datatypes
from .database import Base
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.orm import relationship
#1
class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, nullable=True, server_default='None')
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    
    preferences = relationship("UserPreference", back_populates="user", cascade="all, delete")
#2
class Recipe(Base):
    __tablename__ ='recipes'

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True, server_default='None')
    picture = Column(String, nullable=True, server_default='https://southernspicesrestaurant.com/img/placeholders/comfort_food_placeholder.png')
    cooking_time = Column(String, nullable=True)
    collection = Column(String, nullable=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    
    steps = relationship("Step", backref="recipes", cascade='all, delete-orphan')
    ingredients = relationship("Recipe_Ingredient", back_populates="recipe", cascade="all, delete")
    preferences = relationship("RecipePreference", back_populates="recipe", cascade="all, delete")
#3  
class Ingredient(Base):
    __tablename__ = 'ingredients'

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, nullable=False)
    carbs = Column(Float)
    protein = Column(Float)
    fat = Column(Float)
    calory = Column(Float)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
        
    recipe_ingredients = relationship("Recipe_Ingredient", back_populates="ingredient", cascade="all, delete")
#4
class Shopping(Base):
    __tablename__ ='shopping'

    id = Column(Integer, primary_key=True, nullable=False)
    ingredient_id = Column(Integer, ForeignKey("ingredients.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
 
#5
class Preference(Base):
    __tablename__ = 'preferences'

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, nullable=False)

    recipes = relationship("RecipePreference", back_populates="preference", cascade="all, delete")
    users = relationship("UserPreference", back_populates="preference", cascade="all, delete")
#6
class Restriction(Base):
    __tablename__ = 'restrictions'

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, nullable=False)

#7 recipe steps junction one-to-many
class Step(Base):
    __tablename__ = 'steps'
    
    id = Column(Integer, primary_key=True, nullable=False)
    recipe_id = Column(Integer, ForeignKey("recipes.id", ondelete="CASCADE"), nullable=False)
    step_number = Column(String, nullable=False) 
    description = Column(String, nullable=False)

#8 J
class Recipe_Ingredient(Base):
    __tablename__ ='recipe_ingredients'

    recipe_id = Column(Integer, ForeignKey("recipes.id", ondelete="CASCADE"),primary_key=True, nullable=False)
    ingredients_id = Column(Integer, ForeignKey("ingredients.id", ondelete="CASCADE"),primary_key=True, nullable=False)
    recipe = relationship("Recipe", back_populates="ingredients") 
    ingredient = relationship("Ingredient", back_populates="recipe_ingredients")
    
    quantity = Column(Float)
    unit = Column(String)

#10 
class user_restriction(Base):
    __tablename__ = 'user_restrictions'


    id = Column(Integer, primary_key=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    restriction_id = Column(Integer, ForeignKey("restrictions.id", ondelete="CASCADE"), nullable=False)

#11
class RecipePreference(Base):
    __tablename__ = 'recipe_preferences'

    recipe_id = Column(Integer, ForeignKey('recipes.id', ondelete='CASCADE'), primary_key=True)
    preference_id = Column(Integer, ForeignKey('preferences.id', ondelete='CASCADE'), primary_key=True)

    preference = relationship("Preference", back_populates="recipes", cascade="all, delete")
    recipe = relationship("Recipe", back_populates="preferences", cascade="all, delete")


class UserPreference(Base):
    __tablename__ = 'user_preferences'
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)
    preference_id = Column(Integer, ForeignKey('preferences.id', ondelete='CASCADE'), primary_key=True)

    user = relationship("User", back_populates="preferences", cascade="all, delete")
    preference = relationship("Preference", back_populates="users", cascade="all, delete")

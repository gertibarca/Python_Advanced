from pydantic import BaseModel
from typing import Optional


class CategoryBase(BaseModel):
    name: str


class CategoryCreate(CategoryBase):
    pass


class Category(CategoryBase):
    id: int


class RecipeBase(BaseModel):
    title: str
    description: str
    ingredients: str
    instructions: str
    category_id: Optional[int] = None


class RecipeCreate(RecipeBase):
    pass


class Recipe(RecipeBase):
    id: int
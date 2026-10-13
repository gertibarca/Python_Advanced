from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class CategoryBase(BaseModel):
    name: str = Field(
        min_length=1,
        max_length=80,
        description="Unique category name",
    )

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        value = " ".join(value.split())
        if not value:
            raise ValueError("Category name cannot be empty.")
        return value


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(CategoryBase):
    pass


class Category(CategoryBase):
    model_config = ConfigDict(from_attributes=True)

    id: int


class RecipeBase(BaseModel):
    title: str = Field(min_length=1, max_length=150)
    description: str = Field(min_length=1, max_length=3000)
    ingredients: str = Field(min_length=1, max_length=10000)
    instructions: str = Field(min_length=1, max_length=20000)

    category_id: Optional[int] = Field(default=None, gt=0)

    prep_time: int = Field(default=0, ge=0, le=1440)
    cook_time: int = Field(default=0, ge=0, le=1440)
    servings: int = Field(default=1, ge=1, le=1000)

    difficulty: str = Field(default="Medium")
    cuisine: Optional[str] = Field(default=None, max_length=80)
    calories: Optional[int] = Field(default=None, ge=0, le=100000)

    @field_validator("title", "description", "ingredients", "instructions")
    @classmethod
    def validate_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("This field cannot be empty.")
        return value

    @field_validator("difficulty")
    @classmethod
    def validate_difficulty(cls, value: str) -> str:
        value = value.strip().capitalize()
        if value not in {"Easy", "Medium", "Hard"}:
            raise ValueError("Difficulty must be Easy, Medium, or Hard.")
        return value

    @field_validator("cuisine")
    @classmethod
    def normalize_cuisine(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        value = value.strip()
        return value or None


class RecipeCreate(RecipeBase):
    pass


class RecipeUpdate(RecipeBase):
    pass


class Recipe(RecipeBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    category_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class RecipePage(BaseModel):
    items: list[Recipe]
    total: int
    page: int
    page_size: int
    total_pages: int


class DashboardStats(BaseModel):
    total_recipes: int
    total_categories: int
    average_cooking_time: float
    average_prep_time: float
    difficulty_counts: dict[str, int]
    category_counts: list[dict]
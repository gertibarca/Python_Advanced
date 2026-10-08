from fastapi import FastAPI, HTTPException
from typing import List

from models import (
    Recipe,
    RecipeCreate,
    Category,
    CategoryCreate
)

from database import (
    create_recipe,
    read_recipes,
    read_recipe,
    update_recipe,
    delete_recipe,
    create_category,
    read_categories,
    read_category,
    update_category,
    delete_category
)


app = FastAPI(
    title="Online Recipe Book API",
    description="API for managing recipes and categories",
    version="1.0.0"
)


@app.get("/")
def root():
    return {
        "message": "Welcome to the Online Recipe Book API"
    }


# =====================================================
# RECIPE ENDPOINTS
# =====================================================

@app.get("/recipes", response_model=List[Recipe])
def get_recipes():
    return read_recipes()


@app.get("/recipes/{recipe_id}", response_model=Recipe)
def get_recipe(recipe_id: int):
    recipe = read_recipe(recipe_id)

    if recipe is None:
        raise HTTPException(
            status_code=404,
            detail="Recipe not found"
        )

    return recipe


@app.post("/recipes")
def add_recipe(recipe: RecipeCreate):
    recipe_id = create_recipe(
        recipe.title,
        recipe.description,
        recipe.ingredients,
        recipe.instructions,
        recipe.category_id
    )

    return {
        "id": recipe_id,
        "message": "Recipe created successfully"
    }


@app.put("/recipes/{recipe_id}")
def edit_recipe(
    recipe_id: int,
    recipe: RecipeCreate
):
    updated = update_recipe(
        recipe_id,
        recipe.title,
        recipe.description,
        recipe.ingredients,
        recipe.instructions,
        recipe.category_id
    )

    if not updated:
        raise HTTPException(
            status_code=404,
            detail="Recipe not found"
        )

    return {
        "message": "Recipe updated successfully"
    }


@app.delete("/recipes/{recipe_id}")
def remove_recipe(recipe_id: int):
    deleted = delete_recipe(recipe_id)

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Recipe not found"
        )

    return {
        "message": "Recipe deleted successfully"
    }


# =====================================================
# CATEGORY ENDPOINTS
# =====================================================

@app.get("/categories", response_model=List[Category])
def get_categories():
    return read_categories()


@app.get("/categories/{category_id}", response_model=Category)
def get_category(category_id: int):
    category = read_category(category_id)

    if category is None:
        raise HTTPException(
            status_code=404,
            detail="Category not found"
        )

    return category


@app.post("/categories")
def add_category(category: CategoryCreate):
    category_id = create_category(category.name)

    if category_id is None:
        raise HTTPException(
            status_code=400,
            detail="Category already exists"
        )

    return {
        "id": category_id,
        "message": "Category created successfully"
    }


@app.put("/categories/{category_id}")
def edit_category(
    category_id: int,
    category: CategoryCreate
):
    updated = update_category(
        category_id,
        category.name
    )

    if not updated:
        raise HTTPException(
            status_code=404,
            detail="Category not found or name already exists"
        )

    return {
        "message": "Category updated successfully"
    }


@app.delete("/categories/{category_id}")
def remove_category(category_id: int):
    deleted = delete_category(category_id)

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Category not found"
        )

    return {
        "message": "Category deleted successfully"
    }
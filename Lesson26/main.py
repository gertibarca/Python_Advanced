from typing import Optional

import sqlite3

from fastapi import FastAPI, HTTPException, Query, status
from fastapi.responses import RedirectResponse

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
    delete_category,
    get_dashboard_stats,
)

from models import (
    Recipe,
    RecipeCreate,
    RecipeUpdate,
    RecipePage,
    Category,
    CategoryCreate,
    CategoryUpdate,
    DashboardStats,
)


app = FastAPI(
    title="Online Recipe Book API",
    description=(
        "A recipe management API with search, filtering, "
        "categories, cooking metadata, and dashboard analytics."
    ),
    version="2.0.0",
)


@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/docs")


@app.get("/health")
def health_check():
    return {"status": "healthy"}


def handle_database_error(error: Exception):
    if isinstance(error, sqlite3.IntegrityError):
        message = str(error).lower()

        if "foreign key" in message:
            raise HTTPException(
                status_code=422,
                detail="The selected category does not exist.",
            )

        if "unique" in message:
            raise HTTPException(
                status_code=409,
                detail="A record with that name already exists.",
            )

        raise HTTPException(
            status_code=422,
            detail="The database rejected the supplied data.",
        )

    raise error


# =====================================================
# DASHBOARD
# =====================================================

@app.get("/stats", response_model=DashboardStats)
def dashboard_stats():
    return get_dashboard_stats()


# =====================================================
# RECIPES
# =====================================================

@app.get("/recipes", response_model=RecipePage)
def get_recipes(
    search: Optional[str] = Query(default=None, max_length=150),
    category_id: Optional[int] = Query(default=None, gt=0),
    difficulty: Optional[str] = Query(default=None),
    cuisine: Optional[str] = Query(default=None, max_length=80),
    sort_by: str = Query(
        default="newest",
        pattern="^(newest|oldest|title_asc|title_desc|cook_time_asc|cook_time_desc)$",
    ),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
):
    if difficulty and difficulty not in {"Easy", "Medium", "Hard"}:
        raise HTTPException(
            status_code=422,
            detail="Difficulty must be Easy, Medium, or Hard.",
        )

    try:
        return read_recipes(
            search=search,
            category_id=category_id,
            difficulty=difficulty,
            cuisine=cuisine,
            sort_by=sort_by,
            page=page,
            page_size=page_size,
        )
    except sqlite3.Error:
        raise HTTPException(
            status_code=500,
            detail="Unable to retrieve recipes.",
        )


@app.get("/recipes/{recipe_id}", response_model=Recipe)
def get_recipe(recipe_id: int):
    recipe = read_recipe(recipe_id)

    if recipe is None:
        raise HTTPException(
            status_code=404,
            detail="Recipe not found.",
        )

    return recipe


@app.post(
    "/recipes",
    status_code=status.HTTP_201_CREATED,
)
def add_recipe(recipe: RecipeCreate):
    try:
        recipe_id = create_recipe(**recipe.model_dump())

        return {
            "id": recipe_id,
            "message": "Recipe created successfully.",
        }
    except sqlite3.IntegrityError as error:
        handle_database_error(error)


@app.put("/recipes/{recipe_id}")
def edit_recipe(recipe_id: int, recipe: RecipeUpdate):
    try:
        updated = update_recipe(
            recipe_id,
            **recipe.model_dump(),
        )

        if not updated:
            raise HTTPException(
                status_code=404,
                detail="Recipe not found.",
            )

        return {"message": "Recipe updated successfully."}
    except sqlite3.IntegrityError as error:
        handle_database_error(error)


@app.delete("/recipes/{recipe_id}")
def remove_recipe(recipe_id: int):
    deleted = delete_recipe(recipe_id)

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Recipe not found.",
        )

    return {"message": "Recipe deleted successfully."}


# =====================================================
# CATEGORIES
# =====================================================

@app.get("/categories", response_model=list[Category])
def get_categories():
    return read_categories()


@app.get("/categories/{category_id}")
def get_category(category_id: int):
    category = read_category(category_id)

    if category is None:
        raise HTTPException(
            status_code=404,
            detail="Category not found.",
        )

    return category


@app.post(
    "/categories",
    status_code=status.HTTP_201_CREATED,
)
def add_category(category: CategoryCreate):
    try:
        category_id = create_category(category.name)

        return {
            "id": category_id,
            "message": "Category created successfully.",
        }
    except sqlite3.IntegrityError:
        raise HTTPException(
            status_code=409,
            detail="A category with this name already exists.",
        )


@app.put("/categories/{category_id}")
def edit_category(
    category_id: int,
    category: CategoryUpdate,
):
    try:
        updated = update_category(
            category_id,
            category.name,
        )

        if not updated:
            if read_category(category_id) is None:
                raise HTTPException(
                    status_code=404,
                    detail="Category not found.",
                )

            raise HTTPException(
                status_code=409,
                detail="A category with this name already exists.",
            )

        return {"message": "Category updated successfully."}
    except sqlite3.IntegrityError:
        raise HTTPException(
            status_code=409,
            detail="A category with this name already exists.",
        )


@app.delete("/categories/{category_id}")
def remove_category(category_id: int):
    deleted = delete_category(category_id)

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Category not found.",
        )

    return {
        "message": (
            "Category deleted successfully. "
            "Recipes previously assigned to it are now uncategorized."
        )
    }
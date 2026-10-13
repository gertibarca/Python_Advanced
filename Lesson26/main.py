import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, HTTPException, Query, status
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, ConfigDict, Field, field_validator
from pwdlib import PasswordHash

# =====================================================
# DATABASE CONFIGURATION & SETUP
# =====================================================

DATABASE_NAME = os.getenv("DATABASE_NAME", "recipes.db")

RECIPE_COLUMNS = {
    "prep_time": "INTEGER NOT NULL DEFAULT 0",
    "cook_time": "INTEGER NOT NULL DEFAULT 0",
    "servings": "INTEGER NOT NULL DEFAULT 1",
    "difficulty": "TEXT NOT NULL DEFAULT 'Medium'",
    "cuisine": "TEXT",
    "calories": "INTEGER",
    "created_at": "TEXT",
    "updated_at": "TEXT",
}


def get_connection() -> sqlite3.Connection:
    connection = sqlite3.connect(DATABASE_NAME, timeout=10)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    connection.execute("PRAGMA busy_timeout = 10000")
    return connection


@contextmanager
def db_session():
    connection = get_connection()
    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def create_tables():
    with db_session() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL
            )
        """)

        connection.execute("""
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL COLLATE NOCASE UNIQUE
            )
        """)

        connection.execute("""
            CREATE TABLE IF NOT EXISTS recipes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                ingredients TEXT NOT NULL,
                instructions TEXT NOT NULL,
                category_id INTEGER,
                FOREIGN KEY (category_id)
                    REFERENCES categories(id)
                    ON DELETE SET NULL
            )
        """)

        existing_columns = {
            row["name"]
            for row in connection.execute("PRAGMA table_info(recipes)").fetchall()
        }

        for column, definition in RECIPE_COLUMNS.items():
            if column not in existing_columns:
                connection.execute(f"ALTER TABLE recipes ADD COLUMN {column} {definition}")

        connection.execute("""
            UPDATE recipes
            SET created_at = COALESCE(created_at, CURRENT_TIMESTAMP)
            WHERE created_at IS NULL
        """)

        connection.execute("""
            UPDATE recipes
            SET updated_at = COALESCE(updated_at, created_at, CURRENT_TIMESTAMP)
            WHERE updated_at IS NULL
        """)

        connection.execute("CREATE INDEX IF NOT EXISTS idx_recipes_title ON recipes(title COLLATE NOCASE)")
        connection.execute("CREATE INDEX IF NOT EXISTS idx_recipes_category ON recipes(category_id)")
        connection.execute("CREATE INDEX IF NOT EXISTS idx_recipes_created ON recipes(created_at DESC)")
        connection.execute("CREATE INDEX IF NOT EXISTS idx_recipes_difficulty ON recipes(difficulty)")


# Initialize database tables on startup
create_tables()

# =====================================================
# PYDANTIC MODELS
# =====================================================

class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=6, max_length=100)


class UserResponse(BaseModel):
    id: int
    username: str


class Token(BaseModel):
    access_token: str
    token_type: str


class CategoryBase(BaseModel):
    name: str = Field(min_length=1, max_length=80, description="Unique category name")

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


# =====================================================
# DATABASE CRUD FUNCTIONS
# =====================================================

def create_user(username: str, password_hash: str):
    with db_session() as connection:
        cursor = connection.execute(
            "INSERT INTO users (username, password_hash) VALUES (?, ?)",
            (username.strip().lower(), password_hash),
        )
        return cursor.lastrowid


def read_user_by_username(username: str):
    with get_connection() as connection:
        row = connection.execute(
            "SELECT * FROM users WHERE username = ?",
            (username.strip().lower(),),
        ).fetchone()
        return dict(row) if row else None


def create_category(name: str) -> Optional[int]:
    name = " ".join(name.split())
    if not name:
        raise ValueError("Category name cannot be empty.")
    with db_session() as connection:
        cursor = connection.execute(
            "INSERT INTO categories (name) VALUES (?)",
            (name,),
        )
        return cursor.lastrowid


def read_categories():
    with get_connection() as connection:
        rows = connection.execute("""
            SELECT c.id, c.name, COUNT(r.id) AS recipe_count
            FROM categories c
            LEFT JOIN recipes r ON r.category_id = c.id
            GROUP BY c.id, c.name
            ORDER BY c.name COLLATE NOCASE
        """).fetchall()
        return [dict(row) for row in rows]


def read_category(category_id: int):
    with get_connection() as connection:
        row = connection.execute("""
            SELECT c.id, c.name, COUNT(r.id) AS recipe_count
            FROM categories c
            LEFT JOIN recipes r ON r.category_id = c.id
            WHERE c.id = ?
            GROUP BY c.id, c.name
        """, (category_id,)).fetchone()
        return dict(row) if row else None


def update_category(category_id: int, name: str) -> bool:
    name = " ".join(name.split())
    if not name:
        raise ValueError("Category name cannot be empty.")
    with db_session() as connection:
        cursor = connection.execute(
            "UPDATE categories SET name = ? WHERE id = ?",
            (name, category_id),
        )
        return cursor.rowcount > 0


def delete_category(category_id: int) -> bool:
    with db_session() as connection:
        cursor = connection.execute("DELETE FROM categories WHERE id = ?", (category_id,))
        return cursor.rowcount > 0


RECIPE_FIELDS = (
    "title", "description", "ingredients", "instructions",
    "category_id", "prep_time", "cook_time", "servings",
    "difficulty", "cuisine", "calories"
)

def _recipe_values(data: dict):
    return tuple(data[field] for field in RECIPE_FIELDS)

def _recipe_query(where="", order_by="r.id DESC"):
    return f"""
        SELECT
            r.id, r.title, r.description, r.ingredients, r.instructions,
            r.category_id, c.name AS category_name,
            r.prep_time, r.cook_time, r.servings, r.difficulty,
            r.cuisine, r.calories, r.created_at, r.updated_at
        FROM recipes r
        LEFT JOIN categories c ON c.id = r.category_id
        {where}
        ORDER BY {order_by}
    """

def create_recipe(**kwargs):
    with db_session() as connection:
        cursor = connection.execute("""
            INSERT INTO recipes (
                title, description, ingredients, instructions,
                category_id, prep_time, cook_time, servings,
                difficulty, cuisine, calories,
                created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        """, _recipe_values(kwargs))
        return cursor.lastrowid

def read_recipes(
    search: Optional[str] = None,
    category_id: Optional[int] = None,
    difficulty: Optional[str] = None,
    cuisine: Optional[str] = None,
    sort_by: str = "newest",
    page: int = 1,
    page_size: int = 20,
):
    sort_options = {
        "newest": "r.id DESC",
        "oldest": "r.id ASC",
        "title_asc": "r.title COLLATE NOCASE ASC",
        "title_desc": "r.title COLLATE NOCASE DESC",
        "cook_time_asc": "r.cook_time ASC, r.id DESC",
        "cook_time_desc": "r.cook_time DESC, r.id DESC",
    }
    order_by = sort_options.get(sort_by, sort_options["newest"])
    clauses = []
    parameters = []

    if search and search.strip():
        escaped = (
            search.strip()
            .replace("\\", "\\\\")
            .replace("%", "\\%")
            .replace("_", "\\_")
        )
        pattern = f"%{escaped}%"
        clauses.append("""
            (
                r.title LIKE ? ESCAPE '\\'
                OR r.description LIKE ? ESCAPE '\\'
                OR r.ingredients LIKE ? ESCAPE '\\'
            )
        """)
        parameters.extend([pattern, pattern, pattern])

    if category_id is not None:
        clauses.append("r.category_id = ?")
        parameters.append(category_id)

    if difficulty:
        clauses.append("r.difficulty = ?")
        parameters.append(difficulty)

    if cuisine and cuisine.strip():
        clauses.append("r.cuisine = ?")
        parameters.append(cuisine.strip())

    where = "WHERE " + " AND ".join(clauses) if clauses else ""
    offset = (page - 1) * page_size

    with get_connection() as connection:
        total = connection.execute(
            f"SELECT COUNT(*) FROM recipes r {where}",
            parameters,
        ).fetchone()[0]

        rows = connection.execute(
            _recipe_query(where, order_by) + " LIMIT ? OFFSET ?",
            [*parameters, page_size, offset],
        ).fetchall()

        return {
            "items": [dict(row) for row in rows],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size,
        }

def read_recipe(recipe_id: int):
    with get_connection() as connection:
        row = connection.execute(
            _recipe_query("WHERE r.id = ?", "r.id DESC"),
            (recipe_id,),
        ).fetchone()
        return dict(row) if row else None

def update_recipe(recipe_id: int, **kwargs) -> bool:
    with db_session() as connection:
        cursor = connection.execute("""
            UPDATE recipes
            SET
                title = ?, description = ?, ingredients = ?, instructions = ?,
                category_id = ?, prep_time = ?, cook_time = ?, servings = ?,
                difficulty = ?, cuisine = ?, calories = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (*_recipe_values(kwargs), recipe_id))
        return cursor.rowcount > 0

def delete_recipe(recipe_id: int) -> bool:
    with db_session() as connection:
        cursor = connection.execute("DELETE FROM recipes WHERE id = ?", (recipe_id,))
        return cursor.rowcount > 0

def get_dashboard_stats():
    with get_connection() as connection:
        totals = connection.execute("""
            SELECT
                COUNT(*) AS total_recipes,
                COALESCE(AVG(cook_time), 0) AS average_cooking_time,
                COALESCE(AVG(prep_time), 0) AS average_prep_time
            FROM recipes
        """).fetchone()

        category_total = connection.execute("SELECT COUNT(*) FROM categories").fetchone()[0]

        difficulty_rows = connection.execute("""
            SELECT difficulty, COUNT(*) AS count
            FROM recipes GROUP BY difficulty
        """).fetchall()

        category_rows = connection.execute("""
            SELECT c.name, COUNT(r.id) AS count
            FROM categories c
            LEFT JOIN recipes r ON r.category_id = c.id
            GROUP BY c.id, c.name
            ORDER BY count DESC, c.name
        """).fetchall()

        return {
            "total_recipes": totals["total_recipes"],
            "total_categories": category_total,
            "average_cooking_time": round(totals["average_cooking_time"], 1),
            "average_prep_time": round(totals["average_prep_time"], 1),
            "difficulty_counts": {row["difficulty"]: row["count"] for row in difficulty_rows},
            "category_counts": [{"category": row["name"], "count": row["count"]} for row in category_rows],
        }


# =====================================================
# FASTAPI APP & ROUTES
# =====================================================

app = FastAPI(
    title="Online Recipe Book API",
    description="A recipe management API with authentication, search, filtering, categories, and dashboard analytics.",
    version="2.0.0",
)

pwd_context = PasswordHash.recommended()


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
            raise HTTPException(status_code=422, detail="The selected category does not exist.")
        if "unique" in message:
            raise HTTPException(status_code=409, detail="A record with that name already exists.")
        raise HTTPException(status_code=422, detail="The database rejected the supplied data.")
    raise error


# -------------------------
# AUTHENTICATION ENDPOINTS
# -------------------------

@app.post("/auth/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user: UserCreate):
    try:
        hashed_pw = pwd_context.hash(user.password)
        user_id = create_user(user.username, hashed_pw)
        return {"id": user_id, "username": user.username}
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Username already registered.")


@app.post("/auth/login", response_model=Token)
def login_user(user: UserCreate):
    db_user = read_user_by_username(user.username)
    if not db_user or not pwd_context.verify(user.password, db_user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid username or password.")
    return {"access_token": f"token-for-{db_user['username']}", "token_type": "bearer"}


# -------------------------
# DASHBOARD ENDPOINT
# -------------------------

@app.get("/stats", response_model=DashboardStats)
def dashboard_stats():
    return get_dashboard_stats()


# -------------------------
# RECIPE ENDPOINTS
# -------------------------

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
        raise HTTPException(status_code=422, detail="Difficulty must be Easy, Medium, or Hard.")

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
        raise HTTPException(status_code=500, detail="Unable to retrieve recipes.")


@app.get("/recipes/{recipe_id}", response_model=Recipe)
def get_recipe(recipe_id: int):
    recipe = read_recipe(recipe_id)
    if recipe is None:
        raise HTTPException(status_code=404, detail="Recipe not found.")
    return recipe


@app.post("/recipes", status_code=status.HTTP_201_CREATED)
def add_recipe(recipe: RecipeCreate):
    try:
        recipe_id = create_recipe(**recipe.model_dump())
        return {"id": recipe_id, "message": "Recipe created successfully."}
    except sqlite3.IntegrityError as error:
        handle_database_error(error)


@app.put("/recipes/{recipe_id}")
def edit_recipe(recipe_id: int, recipe: RecipeUpdate):
    try:
        updated = update_recipe(recipe_id, **recipe.model_dump())
        if not updated:
            raise HTTPException(status_code=404, detail="Recipe not found.")
        return {"message": "Recipe updated successfully."}
    except sqlite3.IntegrityError as error:
        handle_database_error(error)


@app.delete("/recipes/{recipe_id}")
def remove_recipe(recipe_id: int):
    deleted = delete_recipe(recipe_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Recipe not found.")
    return {"message": "Recipe deleted successfully."}


# -------------------------
# CATEGORY ENDPOINTS
# -------------------------

@app.get("/categories", response_model=list[Category])
def get_categories():
    return read_categories()


@app.get("/categories/{category_id}")
def get_category(category_id: int):
    category = read_category(category_id)
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found.")
    return category


@app.post("/categories", status_code=status.HTTP_201_CREATED)
def add_category(category: CategoryCreate):
    try:
        category_id = create_category(category.name)
        return {"id": category_id, "message": "Category created successfully."}
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=409, detail="A category with this name already exists.")


@app.put("/categories/{category_id}")
def edit_category(category_id: int, category: CategoryUpdate):
    try:
        updated = update_category(category_id, category.name)
        if not updated:
            if read_category(category_id) is None:
                raise HTTPException(status_code=404, detail="Category not found.")
            raise HTTPException(status_code=409, detail="A category with this name already exists.")
        return {"message": "Category updated successfully."}
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=409, detail="A category with this name already exists.")


@app.delete("/categories/{category_id}")
def remove_category(category_id: int):
    deleted = delete_category(category_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Recipe not found.")
    return {"message": "Category deleted successfully."}
import os
import sqlite3

from contextlib import contextmanager
from pathlib import Path
from typing import Optional


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
    connection = sqlite3.connect(
        DATABASE_NAME,
        timeout=10,
    )
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
            for row in connection.execute(
                "PRAGMA table_info(recipes)"
            ).fetchall()
        }

        for column, definition in RECIPE_COLUMNS.items():
            if column not in existing_columns:
                connection.execute(
                    f"ALTER TABLE recipes ADD COLUMN {column} {definition}"
                )

        # Backfill timestamps for legacy records.
        connection.execute("""
            UPDATE recipes
            SET created_at = COALESCE(
                created_at,
                CURRENT_TIMESTAMP
            )
            WHERE created_at IS NULL
        """)

        connection.execute("""
            UPDATE recipes
            SET updated_at = COALESCE(
                updated_at,
                created_at,
                CURRENT_TIMESTAMP
            )
            WHERE updated_at IS NULL
        """)

        connection.execute("""
            CREATE INDEX IF NOT EXISTS idx_recipes_title
            ON recipes(title COLLATE NOCASE)
        """)

        connection.execute("""
            CREATE INDEX IF NOT EXISTS idx_recipes_category
            ON recipes(category_id)
        """)

        connection.execute("""
            CREATE INDEX IF NOT EXISTS idx_recipes_created
            ON recipes(created_at DESC)
        """)

        connection.execute("""
            CREATE INDEX IF NOT EXISTS idx_recipes_difficulty
            ON recipes(difficulty)
        """)


# =====================================================
# CATEGORY OPERATIONS
# =====================================================

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
            SELECT
                c.id,
                c.name,
                COUNT(r.id) AS recipe_count
            FROM categories c
            LEFT JOIN recipes r ON r.category_id = c.id
            GROUP BY c.id, c.name
            ORDER BY c.name COLLATE NOCASE
        """).fetchall()

        return [dict(row) for row in rows]


def read_category(category_id: int):
    with get_connection() as connection:
        row = connection.execute("""
            SELECT
                c.id,
                c.name,
                COUNT(r.id) AS recipe_count
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
        cursor = connection.execute("""
            UPDATE categories
            SET name = ?
            WHERE id = ?
        """, (name, category_id))

        return cursor.rowcount > 0


def delete_category(category_id: int) -> bool:
    with db_session() as connection:
        cursor = connection.execute(
            "DELETE FROM categories WHERE id = ?",
            (category_id,),
        )
        return cursor.rowcount > 0


# =====================================================
# RECIPE OPERATIONS
# =====================================================

RECIPE_FIELDS = (
    "title",
    "description",
    "ingredients",
    "instructions",
    "category_id",
    "prep_time",
    "cook_time",
    "servings",
    "difficulty",
    "cuisine",
    "calories",
)


def _recipe_values(data: dict):
    return tuple(data[field] for field in RECIPE_FIELDS)


def _recipe_query(where="", order_by="r.id DESC"):
    # where/order_by are internal SQL fragments only.
    return f"""
        SELECT
            r.id,
            r.title,
            r.description,
            r.ingredients,
            r.instructions,
            r.category_id,
            c.name AS category_name,
            r.prep_time,
            r.cook_time,
            r.servings,
            r.difficulty,
            r.cuisine,
            r.calories,
            r.created_at,
            r.updated_at
        FROM recipes r
        LEFT JOIN categories c ON c.id = r.category_id
        {where}
        ORDER BY {order_by}
    """


def create_recipe(
    title: str,
    description: str,
    ingredients: str,
    instructions: str,
    category_id: Optional[int] = None,
    prep_time: int = 0,
    cook_time: int = 0,
    servings: int = 1,
    difficulty: str = "Medium",
    cuisine: Optional[str] = None,
    calories: Optional[int] = None,
):
    data = {
        "title": title,
        "description": description,
        "ingredients": ingredients,
        "instructions": instructions,
        "category_id": category_id,
        "prep_time": prep_time,
        "cook_time": cook_time,
        "servings": servings,
        "difficulty": difficulty,
        "cuisine": cuisine,
        "calories": calories,
    }

    with db_session() as connection:
        cursor = connection.execute("""
            INSERT INTO recipes (
                title, description, ingredients, instructions,
                category_id, prep_time, cook_time, servings,
                difficulty, cuisine, calories,
                created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                    CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        """, _recipe_values(data))

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
        pattern = f"%{search.strip()}%"
        clauses.append("""
            (
                r.title LIKE ? ESCAPE '\\'
                OR r.description LIKE ? ESCAPE '\\'
                OR r.ingredients LIKE ? ESCAPE '\\'
            )
        """)
        escaped = (
            search.strip()
            .replace("\\", "\\\\")
            .replace("%", "\\%")
            .replace("_", "\\_")
        )
        pattern = f"%{escaped}%"
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


def update_recipe(
    recipe_id: int,
    title: str,
    description: str,
    ingredients: str,
    instructions: str,
    category_id: Optional[int] = None,
    prep_time: int = 0,
    cook_time: int = 0,
    servings: int = 1,
    difficulty: str = "Medium",
    cuisine: Optional[str] = None,
    calories: Optional[int] = None,
) -> bool:
    data = {
        "title": title,
        "description": description,
        "ingredients": ingredients,
        "instructions": instructions,
        "category_id": category_id,
        "prep_time": prep_time,
        "cook_time": cook_time,
        "servings": servings,
        "difficulty": difficulty,
        "cuisine": cuisine,
        "calories": calories,
    }

    with db_session() as connection:
        cursor = connection.execute("""
            UPDATE recipes
            SET
                title = ?,
                description = ?,
                ingredients = ?,
                instructions = ?,
                category_id = ?,
                prep_time = ?,
                cook_time = ?,
                servings = ?,
                difficulty = ?,
                cuisine = ?,
                calories = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (*_recipe_values(data), recipe_id))

        return cursor.rowcount > 0


def delete_recipe(recipe_id: int) -> bool:
    with db_session() as connection:
        cursor = connection.execute(
            "DELETE FROM recipes WHERE id = ?",
            (recipe_id,),
        )
        return cursor.rowcount > 0


# =====================================================
# DASHBOARD STATISTICS
# =====================================================

def get_dashboard_stats():
    with get_connection() as connection:
        totals = connection.execute("""
            SELECT
                COUNT(*) AS total_recipes,
                COALESCE(AVG(cook_time), 0) AS average_cooking_time,
                COALESCE(AVG(prep_time), 0) AS average_prep_time
            FROM recipes
        """).fetchone()

        category_total = connection.execute(
            "SELECT COUNT(*) FROM categories"
        ).fetchone()[0]

        difficulty_rows = connection.execute("""
            SELECT difficulty, COUNT(*) AS count
            FROM recipes
            GROUP BY difficulty
        """).fetchall()

        category_rows = connection.execute("""
            SELECT
                c.name,
                COUNT(r.id) AS count
            FROM categories c
            LEFT JOIN recipes r ON r.category_id = c.id
            GROUP BY c.id, c.name
            ORDER BY count DESC, c.name
        """).fetchall()

        return {
            "total_recipes": totals["total_recipes"],
            "total_categories": category_total,
            "average_cooking_time": round(
                totals["average_cooking_time"], 1
            ),
            "average_prep_time": round(
                totals["average_prep_time"], 1
            ),
            "difficulty_counts": {
                row["difficulty"]: row["count"]
                for row in difficulty_rows
            },
            "category_counts": [
                {"category": row["name"], "count": row["count"]}
                for row in category_rows
            ],
        }


create_tables()
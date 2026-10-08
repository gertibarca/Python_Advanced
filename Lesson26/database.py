import sqlite3
from typing import Optional


DATABASE_NAME = "recipes.db"


def get_connection():
    connection = sqlite3.connect(DATABASE_NAME)
    connection.row_factory = sqlite3.Row
    return connection


def create_tables():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS recipes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            ingredients TEXT NOT NULL,
            instructions TEXT NOT NULL,
            category_id INTEGER,
            FOREIGN KEY (category_id) REFERENCES categories(id)
        )
    """)

    connection.commit()
    connection.close()


# -------------------------
# CATEGORY CRUD
# -------------------------

def create_category(name: str):
    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            "INSERT INTO categories (name) VALUES (?)",
            (name,)
        )

        connection.commit()
        category_id = cursor.lastrowid

        return category_id

    except sqlite3.IntegrityError:
        return None

    finally:
        connection.close()


def read_categories():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM categories ORDER BY name")

    categories = cursor.fetchall()
    connection.close()

    return [dict(category) for category in categories]


def read_category(category_id: int):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        "SELECT * FROM categories WHERE id = ?",
        (category_id,)
    )

    category = cursor.fetchone()
    connection.close()

    return dict(category) if category else None


def update_category(category_id: int, name: str):
    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            "UPDATE categories SET name = ? WHERE id = ?",
            (name, category_id)
        )

        connection.commit()
        updated = cursor.rowcount > 0

        return updated

    except sqlite3.IntegrityError:
        return False

    finally:
        connection.close()


def delete_category(category_id: int):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        "DELETE FROM categories WHERE id = ?",
        (category_id,)
    )

    connection.commit()
    deleted = cursor.rowcount > 0

    connection.close()

    return deleted


# -------------------------
# RECIPE CRUD
# -------------------------

def create_recipe(
    title: str,
    description: str,
    ingredients: str,
    instructions: str,
    category_id: Optional[int] = None
):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO recipes
        (title, description, ingredients, instructions, category_id)
        VALUES (?, ?, ?, ?, ?)
    """, (
        title,
        description,
        ingredients,
        instructions,
        category_id
    ))

    connection.commit()
    recipe_id = cursor.lastrowid

    connection.close()

    return recipe_id


def read_recipes():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            recipes.id,
            recipes.title,
            recipes.description,
            recipes.ingredients,
            recipes.instructions,
            recipes.category_id,
            categories.name AS category_name
        FROM recipes
        LEFT JOIN categories
            ON recipes.category_id = categories.id
        ORDER BY recipes.id DESC
    """)

    recipes = cursor.fetchall()
    connection.close()

    return [dict(recipe) for recipe in recipes]


def read_recipe(recipe_id: int):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            recipes.id,
            recipes.title,
            recipes.description,
            recipes.ingredients,
            recipes.instructions,
            recipes.category_id,
            categories.name AS category_name
        FROM recipes
        LEFT JOIN categories
            ON recipes.category_id = categories.id
        WHERE recipes.id = ?
    """, (recipe_id,))

    recipe = cursor.fetchone()
    connection.close()

    return dict(recipe) if recipe else None


def update_recipe(
    recipe_id: int,
    title: str,
    description: str,
    ingredients: str,
    instructions: str,
    category_id: Optional[int] = None
):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE recipes
        SET
            title = ?,
            description = ?,
            ingredients = ?,
            instructions = ?,
            category_id = ?
        WHERE id = ?
    """, (
        title,
        description,
        ingredients,
        instructions,
        category_id,
        recipe_id
    ))

    connection.commit()
    updated = cursor.rowcount > 0

    connection.close()

    return updated


def delete_recipe(recipe_id: int):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        "DELETE FROM recipes WHERE id = ?",
        (recipe_id,)
    )

    connection.commit()
    deleted = cursor.rowcount > 0

    connection.close()

    return deleted


create_tables()
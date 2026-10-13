import os
import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000").rstrip("/")

st.set_page_config(
    page_title="Online Recipe Book",
    page_icon="🍳",
    layout="wide",
)

st.title("🍳 Online Recipe Book")
st.write("Manage your recipes and categories in one place.")


# =====================================================
# API HELPERS
# =====================================================

def api_request(method, endpoint, **kwargs):
    try:
        response = requests.request(
            method,
            f"{API_URL}{endpoint}",
            timeout=10,
            **kwargs,
        )

        if not response.ok:
            try:
                detail = response.json().get("detail", response.text)
            except (ValueError, AttributeError):
                detail = response.text

            st.error(f"API error ({response.status_code}): {detail}")
            return None

        if response.status_code == 204 or not response.content:
            return {}

        return response.json()

    except requests.RequestException as error:
        st.error(f"Could not connect to the API: {error}")
        return None


def get_recipes():
    data = api_request("GET", "/recipes")

    if data is None:
        return []

    # Supports both a direct list and a paginated response.
    if isinstance(data, dict):
        data = data.get("items", [])

    if not isinstance(data, list):
        st.error("Unexpected response format from /recipes.")
        return []

    return [item for item in data if isinstance(item, dict)]


def get_categories():
    data = api_request("GET", "/categories")

    if data is None:
        return []

    if isinstance(data, dict):
        data = data.get("items", [])

    if not isinstance(data, list):
        st.error("Unexpected response format from /categories.")
        return []

    return [item for item in data if isinstance(item, dict)]


def show_recipe_details(recipe):
    st.write(f"**Description:** {recipe.get('description', '')}")
    st.write(f"**Category:** {recipe.get('category_name') or 'No category'}")

    with st.expander("Ingredients and instructions"):
        st.markdown("**Ingredients**")
        st.text(recipe.get("ingredients", ""))

        st.markdown("**Instructions**")
        st.text(recipe.get("instructions", ""))


def category_choices(categories):
    choices = {"No category": None}

    for category in categories:
        if category.get("id") is not None:
            choices[
                f"{category['name']} (ID: {category['id']})"
            ] = category["id"]

    return choices


# =====================================================
# SIDEBAR
# =====================================================

page = st.sidebar.radio(
    "Navigation",
    ["Dashboard", "Manage Recipes", "Manage Categories"],
)


# =====================================================
# DASHBOARD
# =====================================================

if page == "Dashboard":
    st.header("📊 Dashboard")

    recipes = get_recipes()
    categories = get_categories()

    col1, col2 = st.columns(2)

    col1.metric("Total Recipes", len(recipes))
    col2.metric("Total Categories", len(categories))

    st.subheader("All Recipes")

    if recipes:
        search = st.text_input("🔎 Search recipes by title")

        filtered_recipes = [
            recipe for recipe in recipes
            if search.strip().lower() in recipe.get("title", "").lower()
        ]

        if filtered_recipes:
            st.dataframe(
                [
                    {
                        "ID": recipe.get("id"),
                        "Title": recipe.get("title", ""),
                        "Description": recipe.get("description", ""),
                        "Category": recipe.get("category_name") or "No category",
                    }
                    for recipe in filtered_recipes
                ],
                use_container_width=True,
                hide_index=True,
            )

            for recipe in filtered_recipes:
                with st.expander(
                    f"🍽️ {recipe.get('title', 'Untitled recipe')}"
                ):
                    show_recipe_details(recipe)
        else:
            st.info("No matching recipes found.")
    else:
        st.info("No recipes available.")


# =====================================================
# MANAGE RECIPES
# =====================================================

elif page == "Manage Recipes":
    st.header("🍲 Manage Recipes")

    categories = get_categories()
    choices = category_choices(categories)

    tab_add, tab_edit, tab_delete = st.tabs(
        ["➕ Add Recipe", "✏️ Edit Recipe", "🗑️ Delete Recipe"]
    )

    # -------------------------
    # ADD RECIPE
    # -------------------------

    with tab_add:
        st.subheader("Add New Recipe")

        with st.form("add_recipe_form"):
            title = st.text_input("Recipe Title")
            description = st.text_area("Description")
            ingredients = st.text_area(
                "Ingredients",
                placeholder="2 eggs\n1 cup flour\n1 cup milk",
            )
            instructions = st.text_area(
                "Instructions",
                placeholder="1. Prepare ingredients.\n2. Cook and serve.",
            )
            category_name = st.selectbox("Category", list(choices.keys()))

            submitted = st.form_submit_button("Add Recipe")

        if submitted:
            if not all(
                value.strip()
                for value in [title, description, ingredients, instructions]
            ):
                st.error("Please complete all required fields.")
            else:
                result = api_request(
                    "POST",
                    "/recipes",
                    json={
                        "title": title.strip(),
                        "description": description.strip(),
                        "ingredients": ingredients.strip(),
                        "instructions": instructions.strip(),
                        "category_id": choices[category_name],
                    },
                )

                if result is not None:
                    st.success("Recipe added successfully!")
                    st.rerun()

    # -------------------------
    # EDIT RECIPE
    # -------------------------

    with tab_edit:
        st.subheader("Edit Recipe")

        recipes = get_recipes()

        if recipes:
            recipe_options = {
                f"{r.get('id')} - {r.get('title', 'Untitled')}": r
                for r in recipes
                if r.get("id") is not None
            }

            if recipe_options:
                selected_label = st.selectbox(
                    "Select recipe",
                    list(recipe_options.keys()),
                    key="edit_recipe_select",
                )
                current = recipe_options[selected_label]

                current_category_id = current.get("category_id")
                choice_names = list(choices.keys())

                selected_category = next(
                    (
                        name for name, category_id in choices.items()
                        if category_id == current_category_id
                    ),
                    "No category",
                )

                with st.form("edit_recipe_form"):
                    title = st.text_input(
                        "Recipe Title",
                        value=current.get("title", ""),
                    )
                    description = st.text_area(
                        "Description",
                        value=current.get("description", ""),
                    )
                    ingredients = st.text_area(
                        "Ingredients",
                        value=current.get("ingredients", ""),
                    )
                    instructions = st.text_area(
                        "Instructions",
                        value=current.get("instructions", ""),
                    )
                    category_name = st.selectbox(
                        "Category",
                        choice_names,
                        index=choice_names.index(selected_category),
                    )

                    submitted = st.form_submit_button("Update Recipe")

                if submitted:
                    if not all(
                        value.strip()
                        for value in [
                            title, description, ingredients, instructions
                        ]
                    ):
                        st.error("Please complete all required fields.")
                    else:
                        result = api_request(
                            "PUT",
                            f"/recipes/{current['id']}",
                            json={
                                "title": title.strip(),
                                "description": description.strip(),
                                "ingredients": ingredients.strip(),
                                "instructions": instructions.strip(),
                                "category_id": choices[category_name],
                            },
                        )

                        if result is not None:
                            st.success("Recipe updated successfully!")
                            st.rerun()
            else:
                st.info("No valid recipes available to edit.")
        else:
            st.info("No recipes available to edit.")

    # -------------------------
    # DELETE RECIPE
    # -------------------------

    with tab_delete:
        st.subheader("Delete Recipe")

        recipes = get_recipes()

        if recipes:
            recipe_options = {
                f"{r.get('id')} - {r.get('title', 'Untitled')}": r
                for r in recipes
                if r.get("id") is not None
            }

            if recipe_options:
                selected_label = st.selectbox(
                    "Select recipe to delete",
                    list(recipe_options.keys()),
                    key="delete_recipe_select",
                )
                selected = recipe_options[selected_label]

                st.warning(
                    f"You are about to delete '{selected.get('title', '')}'."
                )

                confirm = st.checkbox(
                    "I confirm that I want to delete this recipe.",
                    key="confirm_delete_recipe",
                )

                if st.button(
                    "Delete Recipe",
                    type="primary",
                    disabled=not confirm,
                ):
                    result = api_request(
                        "DELETE",
                        f"/recipes/{selected['id']}",
                    )

                    if result is not None:
                        st.success("Recipe deleted successfully!")
                        st.rerun()
            else:
                st.info("No valid recipes available to delete.")
        else:
            st.info("No recipes available to delete.")


# =====================================================
# MANAGE CATEGORIES
# =====================================================

elif page == "Manage Categories":
    st.header("📁 Manage Categories")

    tab_add, tab_edit, tab_delete = st.tabs(
        ["➕ Add Category", "✏️ Edit Category", "🗑️ Delete Category"]
    )

    # -------------------------
    # ADD CATEGORY
    # -------------------------

    with tab_add:
        st.subheader("Add New Category")

        with st.form("add_category_form"):
            name = st.text_input("Category Name")
            submitted = st.form_submit_button("Add Category")

        if submitted:
            if not name.strip():
                st.error("Category name is required.")
            else:
                result = api_request(
                    "POST",
                    "/categories",
                    json={"name": name.strip()},
                )

                if result is not None:
                    st.success("Category added successfully!")
                    st.rerun()

    # -------------------------
    # EDIT CATEGORY
    # -------------------------

    with tab_edit:
        st.subheader("Edit Category")

        categories = get_categories()

        if categories:
            category_options = {
                f"{c.get('id')} - {c.get('name', '')}": c
                for c in categories
                if c.get("id") is not None
            }

            if category_options:
                selected_label = st.selectbox(
                    "Select category",
                    list(category_options.keys()),
                    key="edit_category_select",
                )
                current = category_options[selected_label]

                with st.form("edit_category_form"):
                    name = st.text_input(
                        "Category Name",
                        value=current.get("name", ""),
                    )
                    submitted = st.form_submit_button("Update Category")

                if submitted:
                    if not name.strip():
                        st.error("Category name is required.")
                    else:
                        result = api_request(
                            "PUT",
                            f"/categories/{current['id']}",
                            json={"name": name.strip()},
                        )

                        if result is not None:
                            st.success("Category updated successfully!")
                            st.rerun()
            else:
                st.info("No valid categories available.")
        else:
            st.info("No categories available to edit.")

    # -------------------------
    # DELETE CATEGORY
    # -------------------------

    with tab_delete:
        st.subheader("Delete Category")

        categories = get_categories()

        if categories:
            category_options = {
                f"{c.get('id')} - {c.get('name', '')}": c
                for c in categories
                if c.get("id") is not None
            }

            if category_options:
                selected_label = st.selectbox(
                    "Select category to delete",
                    list(category_options.keys()),
                    key="delete_category_select",
                )
                selected = category_options[selected_label]

                st.warning(
                    "Deleting a category may affect recipes assigned to it."
                )

                confirm = st.checkbox(
                    "I confirm that I want to delete this category.",
                    key="confirm_delete_category",
                )

                if st.button(
                    "Delete Category",
                    type="primary",
                    disabled=not confirm,
                ):
                    result = api_request(
                        "DELETE",
                        f"/categories/{selected['id']}",
                    )

                    if result is not None:
                        st.success("Category deleted successfully!")
                        st.rerun()
            else:
                st.info("No valid categories available to delete.")
        else:
            st.info("No categories available to delete.")
import os
import requests
import streamlit as st

from dotenv import load_dotenv


load_dotenv()

API_URL = os.getenv(
    "API_URL",
    "http://127.0.0.1:8000"
)


st.set_page_config(
    page_title="Online Recipe Book",
    page_icon="🍳",
    layout="wide"
)


st.title("🍳 Online Recipe Book")
st.write("Manage your recipes and categories in one place.")


# =====================================================
# HELPER FUNCTIONS
# =====================================================

def get_categories():
    response = requests.get(
        f"{API_URL}/categories"
    )

    if response.status_code == 200:
        return response.json()

    return []


def get_recipes():
    response = requests.get(
        f"{API_URL}/recipes"
    )

    if response.status_code == 200:
        return response.json()

    return []


# =====================================================
# SIDEBAR
# =====================================================

page = st.sidebar.radio(
    "Navigation",
    [
        "Dashboard",
        "Manage Recipes",
        "Manage Categories"
    ]
)


# =====================================================
# DASHBOARD
# =====================================================

if page == "Dashboard":

    st.header("📊 Dashboard")

    recipes = get_recipes()
    categories = get_categories()

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "Total Recipes",
            len(recipes)
        )

    with col2:
        st.metric(
            "Total Categories",
            len(categories)
        )

    st.subheader("Recipes")

    if recipes:

        recipe_table = []

        for recipe in recipes:
            recipe_table.append({
                "ID": recipe["id"],
                "Title": recipe["title"],
                "Description": recipe["description"],
                "Category": recipe.get(
                    "category_name",
                    "No category"
                )
            })

        st.dataframe(
            recipe_table,
            use_container_width=True
        )

    else:
        st.info("No recipes available.")


# =====================================================
# MANAGE RECIPES
# =====================================================

elif page == "Manage Recipes":

    st.header("🍲 Manage Recipes")

    categories = get_categories()

    category_options = {
        "No category": None
    }

    for category in categories:
        category_options[
            category["name"]
        ] = category["id"]

    tab1, tab2, tab3 = st.tabs([
        "Add Recipe",
        "Edit Recipe",
        "Delete Recipe"
    ])


    # -------------------------
    # ADD RECIPE
    # -------------------------

    with tab1:

        st.subheader("Add New Recipe")

        with st.form("add_recipe_form"):

            title = st.text_input(
                "Recipe Title"
            )

            description = st.text_area(
                "Description"
            )

            ingredients = st.text_area(
                "Ingredients",
                placeholder="2 eggs\n1 cup flour\n1 cup milk"
            )

            instructions = st.text_area(
                "Instructions"
            )

            category_name = st.selectbox(
                "Category",
                list(category_options.keys())
            )

            submitted = st.form_submit_button(
                "Add Recipe"
            )

            if submitted:

                if not title or not description:
                    st.error(
                        "Title and description are required."
                    )

                elif not ingredients or not instructions:
                    st.error(
                        "Ingredients and instructions are required."
                    )

                else:

                    data = {
                        "title": title,
                        "description": description,
                        "ingredients": ingredients,
                        "instructions": instructions,
                        "category_id": category_options[
                            category_name
                        ]
                    }

                    response = requests.post(
                        f"{API_URL}/recipes",
                        json=data
                    )

                    if response.status_code == 200:
                        st.success(
                            "Recipe added successfully!"
                        )
                        st.rerun()
                    else:
                        st.error(
                            response.text
                        )


    # -------------------------
    # EDIT RECIPE
    # -------------------------

    with tab2:

        st.subheader("Edit Recipe")

        recipes = get_recipes()

        if recipes:

            recipe_options = {
                f'{recipe["id"]} - {recipe["title"]}':
                recipe["id"]
                for recipe in recipes
            }

            selected_recipe = st.selectbox(
                "Select Recipe",
                list(recipe_options.keys())
            )

            recipe_id = recipe_options[selected_recipe]

            current_recipe = next(
                recipe
                for recipe in recipes
                if recipe["id"] == recipe_id
            )

            with st.form("edit_recipe_form"):

                title = st.text_input(
                    "Recipe Title",
                    value=current_recipe["title"]
                )

                description = st.text_area(
                    "Description",
                    value=current_recipe["description"]
                )

                ingredients = st.text_area(
                    "Ingredients",
                    value=current_recipe["ingredients"]
                )

                instructions = st.text_area(
                    "Instructions",
                    value=current_recipe["instructions"]
                )

                current_category_id = current_recipe.get(
                    "category_id"
                )

                category_names = list(
                    category_options.keys()
                )

                selected_category_name = "No category"

                for name, category_id in category_options.items():
                    if category_id == current_category_id:
                        selected_category_name = name

                category_name = st.selectbox(
                    "Category",
                    category_names,
                    index=category_names.index(
                        selected_category_name
                    )
                )

                submitted = st.form_submit_button(
                    "Update Recipe"
                )

                if submitted:

                    data = {
                        "title": title,
                        "description": description,
                        "ingredients": ingredients,
                        "instructions": instructions,
                        "category_id": category_options[
                            category_name
                        ]
                    }

                    response = requests.put(
                        f"{API_URL}/recipes/{recipe_id}",
                        json=data
                    )

                    if response.status_code == 200:
                        st.success(
                            "Recipe updated successfully!"
                        )
                        st.rerun()
                    else:
                        st.error(
                            response.text
                        )

        else:
            st.info("No recipes available to edit.")


    # -------------------------
    # DELETE RECIPE
    # -------------------------

    with tab3:

        st.subheader("Delete Recipe")

        recipes = get_recipes()

        if recipes:

            recipe_options = {
                f'{recipe["id"]} - {recipe["title"]}':
                recipe["id"]
                for recipe in recipes
            }

            selected_recipe = st.selectbox(
                "Select Recipe to Delete",
                list(recipe_options.keys()),
                key="delete_recipe"
            )

            recipe_id = recipe_options[selected_recipe]

            if st.button(
                "Delete Recipe",
                type="primary"
            ):

                response = requests.delete(
                    f"{API_URL}/recipes/{recipe_id}"
                )

                if response.status_code == 200:
                    st.success(
                        "Recipe deleted successfully!"
                    )
                    st.rerun()
                else:
                    st.error(
                        response.text
                    )

        else:
            st.info("No recipes available to delete.")


# =====================================================
# MANAGE CATEGORIES
# =====================================================

elif page == "Manage Categories":

    st.header("📁 Manage Categories")

    tab1, tab2, tab3 = st.tabs([
        "Add Category",
        "Edit Category",
        "Delete Category"
    ])


    # -------------------------
    # ADD CATEGORY
    # -------------------------

    with tab1:

        st.subheader("Add New Category")

        with st.form("add_category_form"):

            name = st.text_input(
                "Category Name"
            )

            submitted = st.form_submit_button(
                "Add Category"
            )

            if submitted:

                if not name:
                    st.error(
                        "Category name is required."
                    )

                else:

                    response = requests.post(
                        f"{API_URL}/categories",
                        json={"name": name}
                    )

                    if response.status_code == 200:
                        st.success(
                            "Category added successfully!"
                        )
                        st.rerun()
                    else:
                        st.error(
                            response.text
                        )


    # -------------------------
    # EDIT CATEGORY
    # -------------------------

    with tab2:

        st.subheader("Edit Category")

        categories = get_categories()

        if categories:

            category_options = {
                f'{category["id"]} - {category["name"]}':
                category["id"]
                for category in categories
            }

            selected_category = st.selectbox(
                "Select Category",
                list(category_options.keys())
            )

            category_id = category_options[
                selected_category
            ]

            current_category = next(
                category
                for category in categories
                if category["id"] == category_id
            )

            with st.form("edit_category_form"):

                name = st.text_input(
                    "Category Name",
                    value=current_category["name"]
                )

                submitted = st.form_submit_button(
                    "Update Category"
                )

                if submitted:

                    response = requests.put(
                        f"{API_URL}/categories/{category_id}",
                        json={"name": name}
                    )

                    if response.status_code == 200:
                        st.success(
                            "Category updated successfully!"
                        )
                        st.rerun()
                    else:
                        st.error(
                            response.text
                        )

        else:
            st.info("No categories available.")


    # -------------------------
    # DELETE CATEGORY
    # -------------------------

    with tab3:

        st.subheader("Delete Category")

        categories = get_categories()

        if categories:

            category_options = {
                f'{category["id"]} - {category["name"]}':
                category["id"]
                for category in categories
            }

            selected_category = st.selectbox(
                "Select Category to Delete",
                list(category_options.keys()),
                key="delete_category"
            )

            category_id = category_options[
                selected_category
            ]

            if st.button(
                "Delete Category",
                type="primary"
            ):

                response = requests.delete(
                    f"{API_URL}/categories/{category_id}"
                )

                if response.status_code == 200:
                    st.success(
                        "Category deleted successfully!"
                    )
                    st.rerun()
                else:
                    st.error(
                        response.text
                    )

        else:
            st.info("No categories available.")
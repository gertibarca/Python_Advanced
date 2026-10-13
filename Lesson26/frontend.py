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

# =====================================================
# SESSION STATE SETUP
# =====================================================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "reg_success" not in st.session_state:
    st.session_state.reg_success = ""


# =====================================================
# API HELPER
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
        st.error(f"Could not connect to the API: {error} (Is FastAPI running on {API_URL}?)")
        return None


# =====================================================
# LAYOUT COMPONENTS (HEADER & FOOTER)
# =====================================================
def render_header():
    st.markdown(
        """
        <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #eaeaea; padding-bottom: 10px; margin-bottom: 25px;">
            <h1 style="margin: 0; color: #FF4B4B;">🍳 Online Recipe Book</h1>
            <p style="margin: 0; font-size: 14px; color: #666;">Your digital kitchen & meal management companion</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_footer():
    st.markdown(
        """
        <hr style="margin-top: 60px; margin-bottom: 20px;">
        <div style="text-align: center; color: #888; font-size: 13px;">
            <p>🍳 <b>Online Recipe Book App</b> • Powered by FastAPI, SQLite & Streamlit</p>
            <p style="margin-top: -8px;">© 2026 All Rights Reserved.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


# =====================================================
# DATA FETCHING HELPERS
# =====================================================
def get_recipes():
    data = api_request("GET", "/recipes")
    if data is None:
        return []
    if isinstance(data, dict):
        data = data.get("items", [])
    if not isinstance(data, list):
        return []
    return [item for item in data if isinstance(item, dict)]


def get_categories():
    data = api_request("GET", "/categories")
    if data is None:
        return []
    if isinstance(data, dict):
        data = data.get("items", [])
    if not isinstance(data, list):
        return []
    return [item for item in data if isinstance(item, dict)]


def show_recipe_details(recipe):
    st.write(f"**Description:** {recipe.get('description', '')}")
    st.write(f"**Category:** {recipe.get('category_name') or 'No category'}")
    st.write(
        f"**Difficulty:** {recipe.get('difficulty', 'Medium')} | **Prep Time:** {recipe.get('prep_time', 0)} mins | **Cook Time:** {recipe.get('cook_time', 0)} mins")

    with st.expander("View Ingredients and Instructions"):
        st.markdown("**Ingredients**")
        st.text(recipe.get("ingredients", ""))

        st.markdown("**Instructions**")
        st.text(recipe.get("instructions", ""))


def category_choices(categories):
    choices = {"No category": None}
    for category in categories:
        if category.get("id") is not None:
            choices[f"{category['name']} (ID: {category['id']})"] = category["id"]
    return choices


# =====================================================
# AUTHENTICATION SCREEN VIEW
# =====================================================
def render_auth_screen():
    render_header()

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.subheader("🔒 Account Authentication Required")

        if st.session_state.reg_success:
            st.success(st.session_state.reg_success)

        tab_login, tab_register = st.tabs(["🔑 Login", "📝 Register"])

        with tab_login:
            with st.form("login_form"):
                username = st.text_input("Username")
                password = st.text_input("Password", type="password")
                submit_login = st.form_submit_button("Login to App", use_container_width=True)

            if submit_login:
                if not username or not password:
                    st.error("Please fill in all fields.")
                else:
                    res = api_request("POST", "/auth/login", json={"username": username.strip(), "password": password})
                    if res and "access_token" in res:
                        st.session_state.logged_in = True
                        st.session_state.username = username.strip()
                        st.session_state.reg_success = ""
                        st.success("Logged in successfully!")
                        st.rerun()

        with tab_register:
            with st.form("register_form"):
                new_username = st.text_input("Choose Username")
                new_password = st.text_input("Choose Password (min 6 chars)", type="password")
                submit_reg = st.form_submit_button("Create Account", use_container_width=True)

            if submit_reg:
                if not new_username or not new_password:
                    st.error("Please fill in all fields.")
                else:
                    res = api_request("POST", "/auth/register",
                                      json={"username": new_username.strip(), "password": new_password})
                    if res is not None:
                        st.session_state.reg_success = f"🎉 Account '{new_username.strip()}' created successfully! You can now log in using the Login tab."
                        st.rerun()

    render_footer()


# =====================================================
# PROTECTED MAIN APPLICATION VIEW
# =====================================================
def render_main_app():
    render_header()

    st.sidebar.markdown(f"👤 Signed in as: **{st.session_state.username}**")
    if st.sidebar.button("🚪 Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.rerun()

    st.sidebar.markdown("---")
    page = st.sidebar.radio(
        "Navigation",
        ["Dashboard", "Manage Recipes", "Manage Categories"],
    )

    # -------------------------
    # DASHBOARD
    # -------------------------
    if page == "Dashboard":
        st.header("📊 Dashboard & Analytics")

        recipes = get_recipes()
        categories = get_categories()

        col1, col2 = st.columns(2)
        col1.metric("Total Recipes", len(recipes))
        col2.metric("Total Categories", len(categories))

        st.subheader("Explore Recipes")

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
                            "Category": recipe.get("category_name") or "No category",
                            "Difficulty": recipe.get("difficulty", "Medium"),
                            "Cook Time (mins)": recipe.get("cook_time", 0),
                        }
                        for recipe in filtered_recipes
                    ],
                    use_container_width=True,
                    hide_index=True,
                )

                for recipe in filtered_recipes:
                    with st.expander(f"🍽️ {recipe.get('title', 'Untitled recipe')} (ID: {recipe.get('id')})"):
                        show_recipe_details(recipe)
            else:
                st.info("No matching recipes found.")
        else:
            st.info("No recipes available yet. Add some via the 'Manage Recipes' tab!")

    # -------------------------
    # MANAGE RECIPES
    # -------------------------
    elif page == "Manage Recipes":
        st.header("🍲 Manage Recipes")

        categories = get_categories()
        choices = category_choices(categories)

        tab_add, tab_edit, tab_delete = st.tabs(
            ["➕ Add Recipe", "✏️ Edit Recipe", "🗑️ Delete Recipe"]
        )

        with tab_add:
            st.subheader("Add New Recipe")

            with st.form("add_recipe_form"):
                title = st.text_input("Recipe Title")
                description = st.text_area("Description")
                ingredients = st.text_area("Ingredients", placeholder="2 eggs\n1 cup flour")
                instructions = st.text_area("Instructions", placeholder="1. Mix ingredients.\n2. Bake.")

                col_a, col_b, col_c = st.columns(3)
                with col_a:
                    prep_time = st.number_input("Prep Time (mins)", min_value=0, value=10)
                with col_b:
                    cook_time = st.number_input("Cook Time (mins)", min_value=0, value=20)
                with col_c:
                    servings = st.number_input("Servings", min_value=1, value=2)

                col_d, col_e = st.columns(2)
                with col_d:
                    difficulty = st.selectbox("Difficulty", ["Easy", "Medium", "Hard"])
                with col_e:
                    cuisine = st.text_input("Cuisine (Optional)", placeholder="Italian, Mexican...")

                category_name = st.selectbox("Category", list(choices.keys()))
                submitted = st.form_submit_button("Add Recipe", type="primary")

            if submitted:
                if not all(v.strip() for v in [title, description, ingredients, instructions]):
                    st.error("Please complete all required text fields.")
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
                            "prep_time": int(prep_time),
                            "cook_time": int(cook_time),
                            "servings": int(servings),
                            "difficulty": difficulty,
                            "cuisine": cuisine.strip() if cuisine else None,
                        },
                    )

                    if result is not None:
                        st.success("Recipe added successfully!")
                        st.rerun()

        with tab_edit:
            st.subheader("Edit Existing Recipe")
            recipes = get_recipes()

            if recipes:
                recipe_options = {f"{r.get('id')} - {r.get('title', 'Untitled')}": r for r in recipes if
                                  r.get("id") is not None}
                selected_label = st.selectbox("Select recipe to edit", list(recipe_options.keys()))
                current = recipe_options[selected_label]

                current_cat_id = current.get("category_id")
                choice_names = list(choices.keys())
                selected_category = next((name for name, cid in choices.items() if cid == current_cat_id),
                                         "No category")

                with st.form("edit_recipe_form"):
                    title = st.text_input("Recipe Title", value=current.get("title", ""))
                    description = st.text_area("Description", value=current.get("description", ""))
                    ingredients = st.text_area("Ingredients", value=current.get("ingredients", ""))
                    instructions = st.text_area("Instructions", value=current.get("instructions", ""))

                    col_a, col_b, col_c = st.columns(3)
                    with col_a:
                        prep_time = st.number_input("Prep Time (mins)", min_value=0, value=current.get("prep_time", 0))
                    with col_b:
                        cook_time = st.number_input("Cook Time (mins)", min_value=0, value=current.get("cook_time", 0))
                    with col_c:
                        servings = st.number_input("Servings", min_value=1, value=current.get("servings", 1))

                    col_d, col_e = st.columns(2)
                    with col_d:
                        diff_options = ["Easy", "Medium", "Hard"]
                        cur_diff = current.get("difficulty", "Medium")
                        difficulty = st.selectbox("Difficulty", diff_options,
                                                  index=diff_options.index(cur_diff) if cur_diff in diff_options else 1)
                    with col_e:
                        cuisine = st.text_input("Cuisine", value=current.get("cuisine", "") or "")

                    category_name = st.selectbox("Category", choice_names, index=choice_names.index(
                        selected_category) if selected_category in choice_names else 0)
                    submitted_edit = st.form_submit_button("Update Recipe", type="primary")

                if submitted_edit:
                    if not all(v.strip() for v in [title, description, ingredients, instructions]):
                        st.error("Please complete all required text fields.")
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
                                "prep_time": int(prep_time),
                                "cook_time": int(cook_time),
                                "servings": int(servings),
                                "difficulty": difficulty,
                                "cuisine": cuisine.strip() if cuisine else None,
                            },
                        )

                        if result is not None:
                            st.success("Recipe updated successfully!")
                            st.rerun()
            else:
                st.info("No recipes available to edit.")

        with tab_delete:
            st.subheader("Delete Recipe")
            recipes = get_recipes()

            if recipes:
                recipe_options = {f"{r.get('id')} - {r.get('title', 'Untitled')}": r for r in recipes if
                                  r.get("id") is not None}
                selected_label = st.selectbox("Select recipe to delete", list(recipe_options.keys()), key="del_rec_sel")
                selected = recipe_options[selected_label]

                st.warning(f"You are about to delete '{selected.get('title', '')}'. This action cannot be undone.")
                confirm = st.checkbox("I confirm that I want to delete this recipe.", key="conf_del_rec")

                if st.button("Delete Recipe Now", type="primary", disabled=not confirm):
                    result = api_request("DELETE", f"/recipes/{selected['id']}")
                    if result is not None:
                        st.success("Recipe deleted successfully!")
                        st.rerun()
            else:
                st.info("No recipes available to delete.")

    # -------------------------
    # MANAGE CATEGORIES
    # -------------------------
    elif page == "Manage Categories":
        st.header("📁 Manage Categories")

        tab_add, tab_edit, tab_delete = st.tabs(
            ["➕ Add Category", "✏️ Edit Category", "🗑️ Delete Category"]
        )

        with tab_add:
            st.subheader("Add New Category")
            with st.form("add_cat_form"):
                name = st.text_input("Category Name")
                submitted = st.form_submit_button("Add Category", type="primary")

            if submitted:
                if not name.strip():
                    st.error("Category name is required.")
                else:
                    result = api_request("POST", "/categories", json={"name": name.strip()})
                    if result is not None:
                        st.success("Category added successfully!")
                        st.rerun()

        with tab_edit:
            st.subheader("Edit Category")
            categories = get_categories()

            if categories:
                cat_options = {f"{c.get('id')} - {c.get('name', '')}": c for c in categories if c.get("id") is not None}
                selected_label = st.selectbox("Select category to edit", list(cat_options.keys()), key="edit_cat_sel")
                current = cat_options[selected_label]

                with st.form("edit_cat_form"):
                    name = st.text_input("Category Name", value=current.get("name", ""))
                    submitted = st.form_submit_button("Update Category", type="primary")

                if submitted:
                    if not name.strip():
                        st.error("Category name is required.")
                    else:
                        result = api_request("PUT", f"/categories/{current['id']}", json={"name": name.strip()})
                        if result is not None:
                            st.success("Category updated successfully!")
                            st.rerun()
            else:
                st.info("No categories available to edit.")

        with tab_delete:
            st.subheader("Delete Category")
            categories = get_categories()

            if categories:
                cat_options = {f"{c.get('id')} - {c.get('name', '')}": c for c in categories if c.get("id") is not None}
                selected_label = st.selectbox("Select category to delete", list(cat_options.keys()), key="del_cat_sel")
                selected = cat_options[selected_label]

                st.warning(
                    "Deleting a category will unassign any recipes linked to it (they will become 'No category').")
                confirm = st.checkbox("I confirm that I want to delete this category.", key="conf_del_cat")

                if st.button("Delete Category Now", type="primary", disabled=not confirm):
                    result = api_request("DELETE", f"/categories/{selected['id']}")
                    if result is not None:
                        st.success("Category deleted successfully!")
                        st.rerun()
            else:
                st.info("No categories available to delete.")

    render_footer()


# =====================================================
# APP ROUTER CONTROLLER
# =====================================================
if not st.session_state.logged_in:
    render_auth_screen()
else:
    render_main_app()
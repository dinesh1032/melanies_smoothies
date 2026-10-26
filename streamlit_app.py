
import streamlit as st
import requests
import pandas as pd
from snowflake.snowpark.functions import col

# Page configuration
st.set_page_config(
    page_title="Customize Your Smoothie",
    page_icon="🥤",
    layout="centered"
)

# App title
st.title("🥤 Customize Your Smoothie! 🥤")
st.write("Choose the fruits you want in your custom Smoothie!")

# Connect to Snowflake
cnx = st.connection("snowflake")
session = cnx.session()

# Customer name
name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on your Smoothie will be:", name_on_order)

# Fetch fruit options and API search values from Snowflake
try:
    fruit_rows = (
        session.table("smoothies.public.fruit_options")
        .select(col("FRUIT_NAME"), col("SEARCH_ON"))
        .collect()
    )

    fruit_options = [row["FRUIT_NAME"] for row in fruit_rows]

    # Map each fruit name to its correct API search value
    fruit_search_values = {
        row["FRUIT_NAME"]: row["SEARCH_ON"]
        for row in fruit_rows
    }

except Exception as e:
    st.error(f"Unable to load fruit options: {e}")
    st.stop()

# Select ingredients
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    options=fruit_options,
    max_selections=5
)

# Show selected ingredients
if ingredients_list:
    st.write("**Selected ingredients:**", ", ".join(ingredients_list))

# Submit order
if st.button("Submit Order", type="primary"):
    if not name_on_order.strip():
        st.warning("Please enter a name for your smoothie.")

    elif not ingredients_list:
        st.warning("Please choose at least one fruit.")

    else:
        ingredients_string = " ".join(ingredients_list)

        try:
            session.sql(
                """
                INSERT INTO smoothies.public.orders
                    (ingredients, name_on_order)
                VALUES (?, ?)
                """,
                params=[
                    ingredients_string,
                    name_on_order.strip()
                ]
            ).collect()

            st.success("Your smoothie is ordered! ✅")
            st.write(f"**Name:** {name_on_order.strip()}")
            st.write(f"**Ingredients:** {ingredients_string}")

        except Exception as e:
            st.error(f"Unable to submit your order: {e}")

# Fruit nutrition information
st.divider()

for fruit_chosen in ingredients_list:
    st.subheader(f"{fruit_chosen} Nutrition Information")

    # Get the correct search value from Snowflake
    search_value = fruit_search_values.get(fruit_chosen)

    if not search_value:
        st.warning(f"No SEARCH_ON value found for {fruit_chosen}.")
        continue

    st.info(
        f"The search value for {fruit_chosen} is {search_value}."
    )

    try:
        response = requests.get(
            "https://my.smoothiefroot.com/api/fruit/"
            + str(search_value).strip(),
            timeout=10
        )

        response.raise_for_status()
        response_data = response.json()

        # Display API response in a readable table
        if isinstance(response_data, dict):
            sf_df = pd.DataFrame([response_data])
            st.dataframe(
                data=sf_df,
                use_container_width=True,
                hide_index=True
            )

        elif isinstance(response_data, list):
            sf_df = pd.DataFrame(response_data)
            st.dataframe(
                data=sf_df,
                use_container_width=True,
                hide_index=True
            )

        else:
            st.write(response_data)

    except requests.RequestException as e:
        st.error(f"Unable to retrieve fruit information: {e}")

    except ValueError:
        st.error(f"Invalid JSON response for {fruit_chosen}.")

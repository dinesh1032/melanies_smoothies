
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

st.write(
    "Choose the fruits you want in your custom Smoothie!"
)

# Connect to Snowflake
cnx = st.connection("snowflake")
session = cnx.session()

# Customer name
name_on_order = st.text_input("Name on Smoothie:")

st.write(
    "The name on your Smoothie will be:",
    name_on_order
)

# Fetch fruit options and SEARCH_ON values from Snowflake
try:
    my_dataframe = (
        session.table("smoothies.public.fruit_options")
        .select(
            col("FRUIT_NAME"),
            col("SEARCH_ON")
        )
    )

    # Convert Snowpark DataFrame to Pandas DataFrame
    pd_df = my_dataframe.to_pandas()

    # Get fruit names for multiselect
    fruit_options = pd_df["FRUIT_NAME"].tolist()

except Exception as e:
    st.error(f"Unable to load fruit options: {e}")
    st.stop()

# Select ingredients
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    fruit_options,
    max_selections=5
)

# Show selected ingredients
if ingredients_list:
    st.write(
        "**Selected ingredients:**",
        ", ".join(ingredients_list)
    )

# Submit order
if st.button("Submit Order", type="primary"):

    if not name_on_order.strip():
        st.warning("Please enter a name for your smoothie.")

    elif not ingredients_list:
        st.warning("Please choose at least one fruit.")

    else:
        # Build ingredients string
        ingredients_string = " ".join(ingredients_list)

        try:
            # Insert order into Snowflake
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

            st.success(
                "Your smoothie is ordered! ✅"
            )

            st.write(
                f"**Name:** {name_on_order.strip()}"
            )

            st.write(
                f"**Ingredients:** {ingredients_string}"
            )

        except Exception as e:
            st.error(
                f"Unable to submit your order: {e}"
            )

# Fruit nutrition information
st.divider()

for fruit_chosen in ingredients_list:

    # Find SEARCH_ON value for the selected fruit
    search_on_rows = pd_df.loc[
        pd_df["FRUIT_NAME"] == fruit_chosen,
        "SEARCH_ON"
    ]

    if search_on_rows.empty or pd.isna(search_on_rows.iloc[0]):
        st.warning(
            f"No SEARCH_ON value found for {fruit_chosen}."
        )
        continue

    search_on = str(search_on_rows.iloc[0]).strip()

    # Display fruit heading
    st.subheader(
        fruit_chosen + " Nutrition Information"
    )

    # Display search value as shown in the screenshot
    st.info(
        f"The search value for {fruit_chosen} is {search_on}."
    )

    try:
        # Call fruit nutrition API using SEARCH_ON
        smoothiefroot_response = requests.get(
            f"https://my.smoothiefroot.com/api/fruit/{search_on}",
            timeout=10
        )

        smoothiefroot_response.raise_for_status()

        response_data = smoothiefroot_response.json()

        # Display API response in a table
        if isinstance(response_data, dict):

            sf_df = st.dataframe(
                data=pd.DataFrame([response_data]),
                use_container_width=True,
                hide_index=True
            )

        elif isinstance(response_data, list):

            sf_df = st.dataframe(
                data=pd.DataFrame(response_data),
                use_container_width=True,
                hide_index=True
            )

        else:
            st.write(response_data)

    except requests.RequestException as e:
        st.error(
            f"Unable to retrieve fruit information: {e}"
        )

    except ValueError:
        st.error(
            f"Invalid JSON response for {fruit_chosen}."
        )

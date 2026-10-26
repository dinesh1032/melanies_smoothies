
import streamlit as st
import requests
from snowflake.snowpark.functions import col

# Page configuration
st.set_page_config(
    page_title="Customize Your Smoothie",
    page_icon="🥤",
    layout="centered"
)

# App title
st.title("🥤 Customize Your Smoothie! 🥤")
st.write("Choose the fruits you want in your custom smoothie.")

# Connect to Snowflake
cnx = st.connection("snowflake")
session = cnx.session()

# Customer name
name_on_order = st.text_input("Name on Smoothie:")

# Fetch fruit options from Snowflake
try:
    fruit_rows = (
        session.table("smoothies.public.fruit_options")
        .select(col("FRUIT_NAME"))
        .collect()
    )

    fruit_options = [row["FRUIT_NAME"] for row in fruit_rows]

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
    #ingredients_string +=

# Submit order
if st.button("Submit Order", type="primary"):
    if not name_on_order.strip():
        st.warning("Please enter a name for your smoothie.")

    elif not ingredients_list:
        st.warning("Please choose at least one fruit.")

    else:
        ingredients_string = " ".join(ingredients_list)

        try:
            # Use parameterized SQL to safely insert the order
            session.sql(
                """
                INSERT INTO smoothies.public.orders
                    (ingredients, name_on_order)
                VALUES (?, ?)
                """,
                params=[ingredients_string, name_on_order.strip()]
            ).collect()

            st.success("Your smoothie is ordered! ✅")
            st.write(f"**Name:** {name_on_order.strip()}")
            st.write(f"**Ingredients:** {ingredients_string}")

        except Exception as e:
            st.error(f"Unable to submit your order: {e}")

# Fruit API example
st.divider()
st.subheader("🍉 Watermelon Information")

if st.button("Get Watermelon Information"):
    try:
        response = requests.get(
            "https://my.smoothiefroot.com/api/fruit/watermelon",
            timeout=10
        )
        response.raise_for_status()

        try:
            #st.json(response.json())
            sf_df = st.dataframe(data=response.json(),use_container_width=True)
        except ValueError:
            st.text(response.text)

    except requests.RequestException as e:
        st.error(f"Unable to retrieve watermelon information: {e}")




# # Import python packages
# import streamlit as st
# #from snowflake.snowpark.context import get_active_session
# from snowflake.snowpark.functions import col

# # Write directly to the app
# st.title(f" :cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
# st.write(
#   """Choose the fruits you want in your custom smoothie!
#   """
# )

# cnx = st.connection("snowflake")
# session = cnx.session()

# # option = st.selectbox('What is your favourite fruit?',('Banana','Strawberries','Peaches'))

# # st.write('Your favorite fruit is:',option)

# name_on_order = st.text_input('Name on Smoothie:')
# st.write('The name in your Smoothie will be:',name_on_order)

# #session = get_active_session()
# my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))
# #st.dataframe(data=my_dataframe, use_container_width=True)

# ingredients_list = st.multiselect('Choose up to 5 ingredients:',my_dataframe,max_selections=5)

# if ingredients_list:
#     # st.write(ingredients_list)
#     # st.text(ingredients_list)

#     ingredients_string = ''

#     for fruit_chosen in ingredients_list:
#         ingredients_string += fruit_chosen + ' '

#     #st.write(ingredients_string)

#     my_insert_stmt = """ insert into smoothies.public.orders(ingredients,name_on_order)
#                     values ('""" + ingredients_string + """','"""+name_on_order+"""')"""

#     st.write(my_insert_stmt)
#     time_to_insert = st.button('Submit Order')

#     if time_to_insert:
#         session.sql(my_insert_stmt).collect()
        
#         st.success('Your Smoothie is ordered!', icon="✅")

# import requests  
# smoothiefroot_response = requests.get("(https://my.smoothiefroot.com/api/fruit/watermelon)")  
# st.text(smoothiefroot_response)

    



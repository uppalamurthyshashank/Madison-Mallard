import streamlit as st
import pandas as pd

# Load the menu data
@st.cache_data
def load_menu_data():
    menu_data = pd.read_csv("Updated Menu.csv")
    return menu_data

menu_data = load_menu_data()

def search_menu(query):
    dietary_types = {
        "DF": "Dairy-Free",
        "GF": "Gluten-Free",
        "NF": "Nut-Free",
        "VN": "Vegan",
        "VG": "Vegetarian"
    }
    
    # Determine if the query is about dietary information
    dietary_query = None
    for code, description in dietary_types.items():
        if code.lower() in query.lower() or description.lower() in query.lower():
            dietary_query = code
            break
    
    # Extract item name from the query
    item_name_query = query.lower()
    for key in ["is", "are", "vegan", "gluten-free", "dairy-free", "nut-free", "vegetarian", ""]:
        item_name_query = item_name_query.replace(key, "").strip()
    
    # Search for the item
    results = menu_data[menu_data['Item Name'].str.contains(item_name_query, case=False, na=False)]
    
    if not results.empty:
        if dietary_query:
            response = []
            for _, row in results.iterrows():
                dietary_info = row["Dietary Information"]
                dietary_info_list = [dietary_types[key] for key in dietary_types if key in dietary_info]
                dietary_info_str = ', '.join(dietary_info_list)
                
                if dietary_query in dietary_info:
                    response.append({
                        "Item Name": row["Item Name"],
                        "Message": f"Yes, {row['Item Name']} is {dietary_types[dietary_query]}."
                    })
                else:
                    response.append({
                        "Item Name": row["Item Name"],
                        "Message": f"No, {row['Item Name']} is not {dietary_types[dietary_query]}. It is {dietary_info_str}."
                    })
            return pd.DataFrame(response)
        else:
            return results[['Item Name', 'Price', 'Restaurent Name', 'Dietary Information']]
    return None

st.title("Madison Mallards Menu Chatbot")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
if prompt := st.chat_input("What menu item would you like to know about?"):
    # Display user message in chat message container
    st.chat_message("user").markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    response = search_menu(prompt)
    if response is not None:
        # Display assistant response in chat message container as table
        with st.chat_message("assistant"):
            st.table(response)
        # Add assistant response to chat history as table
        st.session_state.messages.append({"role": "assistant", "content": response.to_markdown()})
    else:
        response = f"Sorry, I couldn't find any menu items matching '{prompt}'."
        # Display assistant response in chat message container as text
        with st.chat_message("assistant"):
            st.markdown(response)
        # Add assistant response to chat history as text
        st.session_state.messages.append({"role": "assistant", "content": response})

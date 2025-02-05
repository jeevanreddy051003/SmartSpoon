import os
import streamlit as st
from groq import Groq
from PIL import Image
import pytesseract

# Set the GROQ_API_KEY environment variable
os.environ["GROQ_API_KEY"] = "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"

client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),  # Use GROQ_API_KEY environment variable
)

def get_recipe_suggestions(ingredients):
    """
    Use the AI model to suggest recipes based on ingredients.
    """
    query = (
        f"I have the following ingredients: {', '.join(ingredients)}. "
        "Suggest some recipes I can make and provide step-by-step cooking instructions for each."
    )
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": query,
            }
        ],
        model="llama3-8b-8192",
    )
    return chat_completion.choices[0].message.content

def get_recipe_instructions_by_name(recipe_name):
    """
    Use the AI model to generate instructions for a specific recipe name.
    """
    query = f"Provide step-by-step cooking instructions for the recipe: {recipe_name}."
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": query,
            }
        ],
        model="llama3-8b-8192",
    )
    return chat_completion.choices[0].message.content

def get_recipe_from_photo(photo):
    """
    Process an uploaded photo to generate cooking instructions.
    """
    try:
        # Extract text from the image
        extracted_text = pytesseract.image_to_string(photo)
        
        # Use the extracted text to generate instructions
        query = f"The text from the image is: {extracted_text}. Provide step-by-step cooking instructions for the recipe."
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": query,
                }
            ],
            model="llama3-8b-8192",
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        return f"Error processing the photo: {e}"

# Streamlit Interface
st.title("AI Cooking Assistant")
st.sidebar.header("Choose an Option")
option = st.sidebar.radio(
    "What do you want to do?",
    ("Suggest Recipes", "Get Instructions by Recipe Name", "Upload Recipe Photo")
)

if option == "Suggest Recipes":
    st.header("Suggest Recipes Based on Ingredients")
    ingredients_input = st.text_input("Enter ingredients (comma-separated):")
    if st.button("Get Recipes"):
        if ingredients_input:
            ingredients = [i.strip() for i in ingredients_input.split(",")]
            recipes = get_recipe_suggestions(ingredients)
            st.subheader("Suggested Recipes and Instructions")
            st.write(recipes)
        else:
            st.warning("Please enter some ingredients.")

elif option == "Get Instructions by Recipe Name":
    st.header("Get Cooking Instructions for a Recipe")
    recipe_name = st.text_input("Enter the recipe name:")
    if st.button("Get Instructions"):
        if recipe_name:
            instructions = get_recipe_instructions_by_name(recipe_name)
            st.subheader("Cooking Instructions")
            st.write(instructions)
        else:
            st.warning("Please enter a recipe name.")

elif option == "Upload Recipe Photo":
    st.header("Upload a Recipe Photo")
    photo = st.file_uploader("Upload an image file:", type=["jpg", "jpeg", "png"])
    if st.button("Get Instructions from Photo"):
        if photo:
            image = Image.open(photo)
            instructions = get_recipe_from_photo(image)
            st.subheader("Cooking Instructions")
            st.write(instructions)
        else:
            st.warning("Please upload a valid image file.")

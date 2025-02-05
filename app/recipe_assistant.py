import os
from groq import Groq


os.environ["GROQ_API_KEY"] = "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"

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def get_recipe_suggestions(ingredients):
    query = (
        f"I have the following ingredients: {', '.join(ingredients)}. "
        "Suggest some recipes I can make and provide step-by-step cooking instructions for each."
    )
    chat_completion = client.chat.completions.create(
        messages=[{"role": "user", "content": query}],
        model="llama3-8b-8192",
    )
    return chat_completion.choices[0].message.content

def get_recipe_instructions_by_name(recipe_name):
    query = f"Provide step-by-step cooking instructions for the recipe: {recipe_name}."
    chat_completion = client.chat.completions.create(
        messages=[{"role": "user", "content": query}],
        model="llama3-8b-8192",
    )
    return chat_completion.choices[0].message.content

def get_recipe_instructions_from_image(image_filename):
    recipe_name = os.path.splitext(image_filename)[0]
    
    query = f"Provide detailed step-by-step cooking instructions for preparing a {recipe_name}. Include ingredients and cooking method."
    chat_completion = client.chat.completions.create(
        messages=[{"role": "user", "content": query}],
        model="llama3-8b-8192",
    )
    return chat_completion.choices[0].message.content
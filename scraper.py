# scraper.py
import requests

# API_KEY = "923046629bdc41b58280d5db449aae9c"
API_KEY = "75dd9a22d7dd4f0e9b963531edf71eff"

class RecipeScraper:

    def fetch(self, dish_name: str):
        """
        Fetch a recipe using Spoonacular API.
        """

        print(f"[API] Searching for: {dish_name}")

        # 1. Search for recipe ID
        search_url = "https://api.spoonacular.com/recipes/complexSearch"
        params = {
            "query": dish_name,
            "number": 1,
            "apiKey": API_KEY
        }

        search_res = requests.get(search_url, params=params).json()

        if not search_res.get("results"):
            print("[API] No recipe found in search results.")
            return None

        recipe_id = search_res["results"][0]["id"]

        # 2. Get full recipe info
        info_url = f"https://api.spoonacular.com/recipes/{recipe_id}/information"
        params = {"apiKey": API_KEY}

        info = requests.get(info_url, params=params).json()

        # Extract data
        title = info.get("title", dish_name)
        ingredients = []
        for item in info.get("extendedIngredients", []):
            ingredients.append({"name": item["original"], "quantity": ""})

        steps = []
        try:
            steps_list = info["analyzedInstructions"][0]["steps"]
            for s in steps_list:
                steps.append(s["step"])
        except Exception:
            steps.append("No steps available from API.")

        return {
            "dish_name": title,
            "ingredients": ingredients,
            "steps": steps
        }

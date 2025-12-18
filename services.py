import json
from scraper import RecipeScraper
from models import CompletedRecipe, RecipeRequest, User, Preferences, Recipe, Ingredient


# -----------------------------------------------------------
# LOADERS
# -----------------------------------------------------------

def _load_json(path):
    try:
        with open(path, "r") as f:
            return json.load(f)
    except:
        return {}

def _save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=4)


def _load_recipes():
    return _load_json("data/recipes.json")

def _load_users():
    return _load_json("data/users.json")

def _load_history():
    return _load_json("data/history.json")

def _load_prefs():
    return _load_json("data/preferences.json")

def _load_subs():
    return _load_json("data/substitutions.json")

# -----------------------------------------------------------
# SERVICES
# -----------------------------------------------------------

class AuthService: 
    def __init__(self):
        self.users = _load_users()
        self.current_user = None

    def registerUser(self, username, password):        
        if not username or not password:
            return False, "Username / Password cannot be empty."
        
        if username in self.users:
            return False, "Username already exists."
        
        user = User(username=username, password=password)
        self.users[user.username] = {"password": user.password}
        _save_json("data/users.json", self.users)
        
        return True, "Registration successful."

    def authenticate(self, username, password):
        if username not in self.users:
            return False, "User does not exist."

        if self.users[username]["password"] != password:
            return False, "Incorrect password."

        self.current_user = username
        return True, "Login successful."
    

class PreferencesService:

    def __init__(self):
        self.preferences = _load_prefs()
        raw = _load_prefs() 
        self.preferences = {}

        for username, data in raw.items():
            self.preferences[username] = Preferences(
                username=username,
                diet_mode=data.get("diet_mode", "none"),
                exclusions=data.get("exclusions", []),
            )

    def viewPreferences(self, username):
        prefs = self.preferences.get(username)

        if not prefs:
            return {
                "diet_mode": "none",
                "exclusions": []
            }

        return {
            "diet_mode": prefs.diet_mode,
            "exclusions": prefs.exclusions
        }


    def updatePreferences(self, username, diet_mode, exclusions):
        prefs = Preferences(
            username=username,
            diet_mode=diet_mode,
            exclusions=exclusions
        )
        self.preferences[username] = prefs


        raw = {
            uname: {
                "diet_mode": p.diet_mode,
                "exclusions": p.exclusions
            }
            for uname, p in self.preferences.items()
        }

        _save_json("data/preferences.json", raw)


class RecipeService:
    
    def __init__(self):
        self.recipes = _load_recipes()
        self.subs = _load_subs()
        self.scraper = RecipeScraper()
        self.validator = Validator()

    def _dict_to_recipe(self, data: dict) -> Recipe:
        """Convert a raw dict (from JSON/API) into a Recipe object."""
        return Recipe(
            dish_name=data.get("dish_name", ""),
            ingredients=[
                Ingredient(
                    name=ing.get("name", ""),
                    quantity=ing.get("quantity", "")
                )
                for ing in data.get("ingredients", [])
            ],
            steps=data.get("steps", []),
        )

    def _recipe_to_dict(self, recipe: Recipe) -> dict:
        """Convert a Recipe object back into the dict format used by views/history."""
        return {
            "dish_name": recipe.dish_name,
            "ingredients": [
                {"name": ing.name, "quantity": ing.quantity}
                for ing in recipe.ingredients
            ],
            "steps": recipe.steps,
        }

    # ------------------------------
    # FIND RECIPE
    # ------------------------------
    def findRecipe(self, dish_name: str):
        dish = dish_name.lower().strip()

        # 1. Search local DB
        for r in self.recipes:
            if dish in r.get("dish_name", "").lower():
                # return r
                return self._dict_to_recipe(r)

        # 2. Try API
        scraped = self.scraper.fetch(dish_name)
        if scraped:
            return self._dict_to_recipe(scraped)

        return None

    # ------------------------------
    # FEASIBILITY CHECK
    # ------------------------------
    def validateRecipe(self, recipe: dict, preferences: dict):
        result = self.validator.checkFeasibility(recipe, preferences)

        if not result["feasible"]:
            return {
                "feasible": False,
                "reason": result["reason"]
            }

        exclusions = [e.lower() for e in preferences.get("exclusions", [])]
        applied_subs = []

        # for ing in recipe["ingredients"]:
        #     name = ing["name"].lower()
        #     for banned in exclusions:
        #         if banned in name and banned in self.subs:
        #             ing["name"] = self.subs[banned]
        #             applied_subs.append((banned, self.subs[banned]))

        for ing in recipe.ingredients:
            name = ing.name.lower()
            for banned in exclusions:
                if banned in name and banned in self.subs:
                    ing.name = self.subs[banned]
                    applied_subs.append((banned, self.subs[banned]))

        return {
            "feasible": True,
            "substitutions": applied_subs
        }

    # ------------------------------
    # GENERATE RECIPE
    # ------------------------------
    def generateCompliantRecipe(self, request: RecipeRequest):
        recipe = self.findRecipe(request.dish_name)

        if not recipe:
            return {
                "success": False,
                "message": "Could not find a recipe online or locally."
            }

        preferences = {
            "diet_mode": request.diet_mode,
            "exclusions": request.exclusions
        }

        feasibility = self.validateRecipe(recipe, preferences)

        if not feasibility["feasible"]:
            return {
                "success": False,
                "message": feasibility["reason"]
            }

        completed = CompletedRecipe(
            dish_name=recipe.dish_name,
            ingredients=recipe.ingredients,
            steps=recipe.steps,
            feasible=True,
            substitutions=feasibility.get("substitutions", []),
        )
        
        recipe_dict = self._recipe_to_dict(recipe)
            
        return {
            "success": True,
            "recipe": recipe_dict,
            "substitutions": feasibility.get("substitutions", [])
        }
    
class Validator:
    def checkFeasibility(self, recipe: dict, preferences: dict):
        diet = preferences.get("diet_mode", "none")
        exclusions = [e.lower() for e in preferences.get("exclusions", [])]

        ingredient_names = [ing.name.lower() for ing in recipe.ingredients]

        # --- Check exclusions ---
        for banned in exclusions:
            for name in ingredient_names:
                if banned in name:
                    return {
                        "feasible": False,
                        "reason": f"Contains excluded ingredient: {banned}"
                    }

        # --- Diet rules ---
        restricted = {
            "vegetarian": ["chicken", "beef", "pork", "fish", "shrimp"],
            "vegan": ["chicken", "beef", "pork", "fish", "shrimp", "egg", "milk", "cheese", "butter"]
        }

        if diet in restricted:
            for bad in restricted[diet]:
                if any(bad in name for name in ingredient_names):
                    return {
                        "feasible": False,
                        "reason": f"Recipe violates {diet} diet (contains: {bad})"
                    }

        return {
            "feasible": True,
            "reason": ""
        }

class HistoryService:
    def __init__(self):
        self.history = _load_history()

        if isinstance(self.history, list):
            self.history = {}
            _save_json("data/history.json", self.history)

    def addEntry(self, username, recipe):
        if username not in self.history:
            self.history[username] = []

        self.history[username].append(recipe)
        _save_json("data/history.json", self.history)

    def getHistory(self, username):
        if isinstance(self.history, list):  
            return []
        return self.history.get(username, [])
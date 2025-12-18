from controllers import (
    AuthController,
    PreferencesController,
    RecipeController,
    HistoryController
)

class AuthView:
    """
    Handles all authentication-related user interaction (login/register)
    and delegates logic to AuthController.
    """

    def __init__(self, auth_controller: AuthController):
        self.auth = auth_controller

    def showRegistrationForm(self):
        print("\n--- Register ---")
        username = input("Username: ")
        password = input("Password: ")

        ok, msg = self.auth.handleRegistration(username, password)
        print(msg + "\n")
        return ok  

    def showLoginForm(self):
        print("\n--- Login ---")
        username = input("Username: ")
        password = input("Password: ")

        ok, msg = self.auth.handleLogin(username, password)
        print(msg + "\n")

        return ok

class PreferencesView:

    def __init__(self, pref_controller: PreferencesController):
        self.pref = pref_controller


    def showPreferencesForm(self, username):
        prefs = self.pref.getPreferences(username)

        print("\n--- Preferences ---")
        print("Current diet mode:", prefs["diet_mode"])
        print("Current exclusions:", ", ".join(prefs["exclusions"]) or "None")

        print("\nDiet options:")
        print("1) none")
        print("2) vegetarian")
        print("3) vegan")

        mode_choice = input("Select diet mode: ")

        diet_map = {"1": "none", "2": "vegetarian", "3": "vegan"}
        diet_mode = diet_map.get(mode_choice, prefs["diet_mode"])

        exclude = input("Enter exclusions (comma-separated): ")
        exclusions = [e.strip() for e in exclude.split(",")] if exclude.strip() else []

        self.pref.updatePreferences(username, diet_mode, exclusions)

        print("\nPreferences updated!\n")

    def showPreferences(self, username):
        prefs = self.pref.getPreferences(username)

        print("\n--- Current Preferences ---")
        print("Diet mode:", prefs["diet_mode"])
        exclusions = ", ".join(prefs["exclusions"]) or "None"
        print("Exclusions:", exclusions)

        input("\nPress Enter to return to the dashboard...")

class RecipeView:
    """
    Handles the UI for generating and displaying recipes.
    Delegates logic to RecipeController and HistoryController.
    """

    def __init__(self, recipe_controller: RecipeController, history_controller: HistoryController):
        self.recipe_ctrl = recipe_controller
        self.history = history_controller

    def generateRecipe(self, username: str, prefs: dict):
        dish = input("\nEnter dish name: ")

        print("\nFetching online recipe... please wait...\n")

        result = self.recipe_ctrl.generateCompliantRecipe(dish, prefs)

        if not result["success"]:
            print("Error:", result["message"], "\n")
            return

        recipe = result["recipe"]

        print("=== Recipe Found ===")
        print("Dish:", recipe["dish_name"])

        print("\nIngredients:")
        for ing in recipe["ingredients"]:
            print(" •", ing["name"])

        print("\nSteps:")
        for i, step in enumerate(recipe["steps"], 1):
            print(f" {i}. {step}")

        if result["substitutions"]:
            print("\nApplied substitutions:")
            for old, new in result["substitutions"]:
                print(f" - Replaced '{old}' with '{new}'")

        print("\nSaving to history...\n")
        self.history.addEntry(username, recipe)
        print("Saved!\n")

class HistoryView:
    """
    Handles UI for viewing a user's recipe history.
    Delegates data access to HistoryController.
    """

    def __init__(self, history_controller: HistoryController):
        self.history = history_controller

    def showHistory(self, username: str):
        print("\n--- Your History ---")
        items = self.history.getHistory(username)

        if not items:
            print("No history yet.\n")
            return

        # List the recipes
        for i, r in enumerate(items, 1):
            print(f"{i}) {r.get('dish_name', 'Unknown Dish')}")

        print("\nEnter a number to view details, or press Enter to go back.")
        choice = input("Choose: ").strip()

        if not choice:
            return

        # Validate selection
        if not choice.isdigit():
            print("Invalid choice. Must be a number.\n")
            return

        index = int(choice) - 1
        if index < 0 or index >= len(items):
            print("Selection out of range.\n")
            return

        recipe = items[index]

        # Display recipe details
        print("\n=== Saved Recipe Details ===")
        print("Dish:", recipe.get("dish_name", "Unknown Dish"))

        print("\nIngredients:")
        for ing in recipe.get("ingredients", []):
            print(" •", ing.get("name", ""))

        print("\nSteps:")
        for i, step in enumerate(recipe.get("steps", []), 1):
            print(f" {i}. {step}")

        print("\nPress Enter to return.")
        input()



# controllers.py
import json
from scraper import RecipeScraper
from services import (
    AuthService,
    PreferencesService,
    RecipeService,
    HistoryService
)
from models import RecipeRequest

# -----------------------------------------------------------
# AUTH CONTROLLER
# -----------------------------------------------------------

class AuthController:

    def __init__(self):
        self.service = AuthService()

    def handleRegistration(self, username, password):
        return self.service.registerUser(username, password)


    def handleLogin(self, username, password):
        return self.service.authenticate(username, password)

    
    @property
    def current_user(self):
        return self.service.current_user

# -----------------------------------------------------------
# PREFERENCES CONTROLLER
# -----------------------------------------------------------

class PreferencesController:

    
    def __init__(self):
        self.service = PreferencesService()

    def getPreferences(self, username):
        return self.service.viewPreferences(username)
    
    def updatePreferences(self, username, diet_mode, exclusions):
        return self.service.updatePreferences(username, diet_mode, exclusions)



# -----------------------------------------------------------
# HISTORY CONTROLLER
# -----------------------------------------------------------

class HistoryController:


    def __init__(self):
        self.service = HistoryService()

    def addEntry(self, username, recipe: dict):
        self.service.addEntry(username, recipe)

    def getHistory(self, username):
        return self.service.getHistory(username)

# -----------------------------------------------------------
# RECIPE CONTROLLER
# -----------------------------------------------------------

class RecipeController:

    """
    Delegates all recipe-related logic to RecipeService.
    """

    def __init__(self):
        self.service = RecipeService()

    def findRecipe(self, dish_name: str):
        return self.service.findRecipe(dish_name)

    def checkFeasibility(self, recipe: dict, preferences: dict):
        return self.service.validateRecipe(recipe, preferences)

    def generateCompliantRecipe(self, dish_name: str, preferences: dict):
        req = RecipeRequest(
            dish_name=dish_name,
            diet_mode=preferences.get("diet_mode", "none"),
            exclusions=preferences.get("exclusions", []),
        )
        return self.service.generateCompliantRecipe(req)

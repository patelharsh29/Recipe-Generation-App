# cli_view.py

from controllers import (
    AuthController,
    PreferencesController,
    RecipeController,
    HistoryController
)
from views import (
    AuthView,
    PreferencesView,
    RecipeView,
    HistoryView
)

class CLI:

    def __init__(self):
        self.auth = AuthController()
        self.pref = PreferencesController()
        self.recipe_ctrl = RecipeController()
        self.history = HistoryController()
        
        self.auth_view = AuthView(self.auth)
        self.pref_view = PreferencesView(self.pref)
        self.recipe_view = RecipeView(self.recipe_ctrl, self.history)
        self.history_view = HistoryView(self.history) 

    # ---------------------------------------------------------
    # LOGIN SCREEN
    # ---------------------------------------------------------
    def loginMenu(self):
        while True:
            print("========================================")
            print("Recipe Generation System (CLI)")
            print("1) Register")
            print("2) Login")
            print("0) Quit")
            choice = input("Choose: ")

            if choice == "1":
                self.auth_view.showRegistrationForm()
            elif choice == "2":
                if self.auth_view.showLoginForm():
                    return True
            elif choice == "0":
                return False
            else:
                print("Invalid choice.\n")


    # ---------------------------------------------------------
    # MAIN DASHBOARD
    # ---------------------------------------------------------
    def dashboard(self):
        user = self.auth.current_user
        while True:
            prefs = self.pref.getPreferences(user)

            print("\n--- Dashboard ---")
            print("1) Generate recipe")
            print("2) Manage preferences")
            print("3) View history")
            print("0) Logout")

            choice = input("Choose: ")

            if choice == "1":
                self.recipe_view.generateRecipe(user, prefs)
            elif choice == "2":
                self.managePreferences(user)
            elif choice == "3":
                self.history_view.showHistory(user)
            elif choice == "0":
                print("Logging out...\n")
                return
            else:
                print("Invalid choice.\n")

    # ---------------------------------------------------------
    # GENERATE RECIPE
    # ---------------------------------------------------------

    # ---------------------------------------------------------
    # PREFERENCES
    # ---------------------------------------------------------
    def managePreferences(self, username):
        while True:
            print("\n--- Manage Preferences ---")
            print("1) View preferences")
            print("2) Edit preferences")
            print("0) Back to dashboard")
            choice = input("Choose: ")

            if choice == "1":
                self.pref_view.showPreferences(username)
            elif choice == "2":
                self.pref_view.showPreferencesForm(username)
            elif choice == "0":
                return
            else:
                print("Invalid choice.\n")

    # ---------------------------------------------------------
    # HISTORY
    # ---------------------------------------------------------
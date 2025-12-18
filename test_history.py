import os
import json
import shutil
import unittest

from controllers import HistoryController  
from services import HistoryService


DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
HISTORY_PATH = os.path.join(DATA_DIR, "history.json")
HISTORY_BACKUP_PATH = os.path.join(DATA_DIR, "history_backup.json")


class TestHistoryController(unittest.TestCase):

    def setUp(self):
        """
        Runs before each test.
        - Backup the real history.json (if it exists)
        - Replace it with an empty JSON object {}
        - Create a fresh HistoryController that reads this clean file
        """
        if os.path.exists(HISTORY_PATH):
            shutil.copy(HISTORY_PATH, HISTORY_BACKUP_PATH)
        else:
            # make sure file exists so HistoryController can load it
            with open(HISTORY_PATH, "w", encoding="utf-8") as f:
                json.dump({}, f)

        # overwrite with empty dict for a clean state
        with open(HISTORY_PATH, "w", encoding="utf-8") as f:
            json.dump({}, f)

        self.history_service = HistoryController()

    def tearDown(self):
        """
        Runs after each test.
        - Restore the backup history.json (if it exists)
        """
        if os.path.exists(HISTORY_BACKUP_PATH):
            shutil.move(HISTORY_BACKUP_PATH, HISTORY_PATH)

    # -----------------------------------------
    # TC-HIST-01: get() for new user -> empty
    # -----------------------------------------
    def test_get_history_for_new_user_returns_empty_list(self):
        """
        TC-HIST-01:
        Given there is no history stored for a user,
        when we call get(username),
        then it should return an empty list.
        """
        username = "new_user"

        items = self.history_service.getHistory(username)

        self.assertIsInstance(items, list)
        self.assertEqual(len(items), 0)

    # -----------------------------------------
    # TC-HIST-02: add one recipe then get()
    # -----------------------------------------
    def test_add_single_recipe_creates_history_entry(self):
        """
        TC-HIST-02:
        When we add a recipe for a user with no prior history,
        then get(username) should return a list with that recipe.
        """
        username = "orion"
        recipe = {
            "dish_name": "Test Dish",
            "ingredients": [{"name": "water", "quantity": "1 cup"}],
            "steps": ["Boil water."]
        }

        # Act: add recipe to history
        self.history_service.addEntry(username, recipe)

        # Read back via controller
        items = self.history_service.getHistory(username)

        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["dish_name"], "Test Dish")

        # Also verify it's persisted in the file
        with open(HISTORY_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.assertIn(username, data)
        self.assertEqual(len(data[username]), 1)
        self.assertEqual(data[username][0]["dish_name"], "Test Dish")

    # -----------------------------------------
    # TC-HIST-03: add multiple recipes in order
    # -----------------------------------------
    def test_add_multiple_recipes_preserves_order(self):
        """
        TC-HIST-03:
        When multiple recipes are added for the same user,
        they should be stored in order and retrievable via get(username).
        """
        username = "test"

        r1 = {"dish_name": "First Dish", "ingredients": [], "steps": []}
        r2 = {"dish_name": "Second Dish", "ingredients": [], "steps": []}
        r3 = {"dish_name": "Third Dish", "ingredients": [], "steps": []}

        self.history_service.addEntry(username, r1)
        self.history_service.addEntry(username, r2)
        self.history_service.addEntry(username, r3)

        items = self.history_service.getHistory(username)

        self.assertEqual(len(items), 3)
        self.assertEqual(items[0]["dish_name"], "First Dish")
        self.assertEqual(items[1]["dish_name"], "Second Dish")
        self.assertEqual(items[2]["dish_name"], "Third Dish")

        # Check file content as well
        with open(HISTORY_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.assertIn(username, data)
        self.assertEqual(len(data[username]), 3)
        self.assertEqual(data[username][0]["dish_name"], "First Dish")
        self.assertEqual(data[username][1]["dish_name"], "Second Dish")
        self.assertEqual(data[username][2]["dish_name"], "Third Dish")


if __name__ == "__main__":
    unittest.main()

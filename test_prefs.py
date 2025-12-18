import os
import json
import shutil
import unittest

from controllers import PreferencesController
from services import PreferencesService


DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
PREFS_PATH = os.path.join(DATA_DIR, "preferences.json")
PREFS_BACKUP_PATH = os.path.join(DATA_DIR, "preferences_backup.json")


class TestPreferencesController(unittest.TestCase):

    def setUp(self):
        """
        Runs before each test.
        - Backup the real preferences.json (if it exists)
        - Replace it with an empty JSON object {}
        - Create a fresh PreferencesController that reads this clean file
        """
        if os.path.exists(PREFS_PATH):
            shutil.copy(PREFS_PATH, PREFS_BACKUP_PATH)
        else:
            # make sure file exists so PreferencesController can load it
            with open(PREFS_PATH, "w", encoding="utf-8") as f:
                json.dump({}, f)

        # overwrite with empty dict for a clean state
        with open(PREFS_PATH, "w", encoding="utf-8") as f:
            json.dump({}, f)

        self.prefs = PreferencesService()

    def tearDown(self):
        """
        Runs after each test.
        - Restore the backup preferences.json (if it exists)
        """
        if os.path.exists(PREFS_BACKUP_PATH):
            shutil.move(PREFS_BACKUP_PATH, PREFS_PATH)

    # -----------------------------
    # TC-PREF-01: default prefs
    # -----------------------------
    def test_get_preferences_returns_defaults_for_new_user(self):
        """
        TC-PREF-01:
        Given there are no saved preferences for a user,
        when we call get_preferences(username),
        then it should return the default diet_mode 'none' and empty exclusions.
        """
        username = "new_user"

        prefs = self.prefs.viewPreferences(username)

        # check structure
        self.assertIn("diet_mode", prefs)
        # check default values
        self.assertEqual(prefs["diet_mode"], "none")
        self.assertEqual(prefs["exclusions"], [])

    # -----------------------------
    # TC-PREF-02: update + read
    # -----------------------------
    def test_update_preferences_persists_values(self):
        """
        TC-PREF-02:
        When we update preferences for a user,
        then get_preferences should return the updated values
        and they should be saved to the JSON file.
        """
        username = "alice"
        diet_mode = "vegan"
        exclusions = ["onion", "garlic"]

        # update prefs
        self.prefs.updatePreferences(username, diet_mode, exclusions)

        # read back via controller
        prefs = self.prefs.viewPreferences(username)
        self.assertEqual(prefs["diet_mode"], "vegan")
        self.assertEqual(prefs["exclusions"], ["onion", "garlic"])

        # verify content in the file
        with open(PREFS_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.assertIn(username, data)
        self.assertEqual(data[username]["diet_mode"], "vegan")
        self.assertEqual(data[username]["exclusions"], ["onion", "garlic"])

    # -----------------------------
    # TC-PREF-03: overwrite values
    # -----------------------------
    def test_update_preferences_overwrites_old_values(self):
        """
        TC-PREF-03:
        Given a user already has saved preferences,
        when we update them again,
        then the new values should replace the old ones.
        """
        username = "alice"

        # first set of preferences
        self.prefs.updatePreferences(username, "vegetarian", ["egg"])
        # overwrite with new preferences
        self.prefs.updatePreferences(username, "none", [])

        prefs = self.prefs.viewPreferences(username)
        self.assertEqual(prefs["diet_mode"], "none")
        self.assertEqual(prefs["exclusions"], [])

        with open(PREFS_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.assertEqual(data[username]["diet_mode"], "none")
        self.assertEqual(data[username]["exclusions"], [])


if __name__ == "__main__":
    unittest.main()

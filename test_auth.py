import os
import json
import shutil
import unittest

from controllers import AuthController
from services import AuthService  


DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
USERS_PATH = os.path.join(DATA_DIR, "users.json")
USERS_BACKUP_PATH = os.path.join(DATA_DIR, "users_backup.json")


class TestAuthController(unittest.TestCase):

    def setUp(self):
        """
        Runs before each test.
        - Backup the real users.json (if it exists)
        - Replace it with an empty JSON object {}
        - Create a fresh AuthController that reads this clean file
        """
        if os.path.exists(USERS_PATH):
            shutil.copy(USERS_PATH, USERS_BACKUP_PATH)
        else:
            with open(USERS_PATH, "w", encoding="utf-8") as f:
                json.dump({}, f)

        # overwrite with empty dict for a clean state
        with open(USERS_PATH, "w", encoding="utf-8") as f:
            json.dump({}, f)

        self.auth = AuthService()

    def tearDown(self):
        """
        Runs after each test.
        - Restore the backup users.json (if it exists)
        """
        if os.path.exists(USERS_BACKUP_PATH):
            shutil.move(USERS_BACKUP_PATH, USERS_PATH)

    # register a new user
    def test_register_new_user_success(self):
        """
        TC-AUTH-01:
        Given an empty users file,
        when we register a new username,
        then it should succeed and persist the user.
        """
        ok, msg = self.auth.registerUser("alice", "secret123")

        # 1) method should report success
        self.assertTrue(ok)
        self.assertEqual("Registration successful.", msg)

        # 2) user should actually be in the users dict
        self.assertIn("alice", self.auth.users)
        self.assertEqual(self.auth.users["alice"]["password"], "secret123")

        # 3) saved to the file
        with open(USERS_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.assertIn("alice", data)
        self.assertEqual(data["alice"]["password"], "secret123")

    def test_register_duplicate_user_fails(self):
        """
        TC-AUTH-02:
        Given a user already exists,
        when we register with the same username again,
        then it should fail with 'Username already exists.'.
        """
        # registration should succeed
        ok1, msg1 = self.auth.registerUser("alice", "secret123")
        self.assertTrue(ok1)
        self.assertEqual("Registration successful.", msg1)

        # second registration with the same username should fail
        ok2, msg2 = self.auth.registerUser("alice", "newpassword")

        # 1) should report failure
        self.assertFalse(ok2)
        self.assertEqual("Username already exists.", msg2)

        # 2) password should NOT be overwritten in memory
        self.assertEqual(self.auth.users["alice"]["password"], "secret123")

        # 3) password should NOT be overwritten in the file
        with open(USERS_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.assertEqual(data["alice"]["password"], "secret123")

    def test_register_empty_username_fails(self):
        """
        TC-AUTH-03:
        Registration must fail if the username is empty or None.
        """
        ok, msg = self.auth.registerUser("", "password123")

        # 1) should return failure
        self.assertFalse(ok)
        self.assertEqual("Username / Password cannot be empty.", msg)

        # 2) no user should be added
        self.assertNotIn("", self.auth.users)

        # 3) file should not contain empty username
        with open(USERS_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.assertNotIn("", data)

    def test_register_empty_password_fails(self):
        """
        TC-AUTH-04:
        Registration must fail if the password is empty or None.
        """
        ok, msg = self.auth.registerUser("alice", "")

        # 1) should return failure
        self.assertFalse(ok)
        self.assertEqual("Username / Password cannot be empty.", msg)

        # 2) user should NOT be added
        self.assertNotIn("alice", self.auth.users)

        # 3) file should not contain an incomplete user
        with open(USERS_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.assertNotIn("alice", data)    
    
    def test_login_success_for_existing_user(self):
        """
        TC-AUTH-05:
        Given a registered user,
        when we login with the correct password,
        then it should succeed and set current_user.
        """
        # create a user using register()
        ok_reg, msg_reg = self.auth.registerUser("alice", "secret123")
        self.assertTrue(ok_reg)

        # attempt login with correct credentials
        ok, msg = self.auth.authenticate("alice", "secret123")

        # login works
        self.assertTrue(ok)
        self.assertEqual("Login successful.", msg)
        self.assertEqual(self.auth.current_user, "alice")

    def test_login_wrong_password_fails(self):
        """
        TC-AUTH-06:
        Given a registered user,
        when we login with the wrong password,
        then it should fail and not set current_user.
        """
        # register a user
        ok_reg, msg_reg = self.auth.registerUser("alice", "secret123")
        self.assertTrue(ok_reg)

        # try logging in with the wrong password
        ok, msg = self.auth.authenticate("alice", "wrongpassword")

        # login should fail
        self.assertFalse(ok)
        self.assertEqual("Incorrect password.", msg)

        # current_user should still be None
        self.assertIsNone(self.auth.current_user)

    def test_login_nonexistent_user_fails(self):
        """
        TC-AUTH-07:
        When we login with a username that does not exist,
        then it should fail with 'User does not exist.'.
        """
        # no users registered in this clean setUp state

        ok, msg = self.auth.authenticate("ghost", "whatever123")

        # login should fail
        self.assertFalse(ok)
        self.assertEqual("User does not exist.", msg)

        # current_user should still be None
        self.assertIsNone(self.auth.current_user)



if __name__ == "__main__":
    unittest.main()

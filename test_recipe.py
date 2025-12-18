import unittest

from controllers import RecipeController  # use your existing controller


class TestRecipeController(unittest.TestCase):

    def setUp(self):
        """
        Runs before each test.
        - Create a fresh RecipeController, which loads recipes.json and substitutions.json
        """
        self.recipe_ctrl = RecipeController()

    # -----------------------------------------
    # TC-REC-01: find local Poutine recipe
    # -----------------------------------------
    def test_find_recipe_returns_local(self):
        """
        TC-REC-01:
        Given recipes.json contains a recipe with dish_name 'Poutine',
        when we call find_recipe('Poutine'),
        then it should return that local recipe and not None.
        """
        recipe = self.recipe_ctrl.findRecipe("Poutine")

        # 1) should get some recipe back
        self.assertIsNotNone(recipe)

        # 2) should have a dish_name field
        self.assertIn("dish_name", recipe)

        # 3)should be exactly 'Poutine'
        self.assertEqual(recipe["dish_name"], "Poutine")

        # 4) sheck ingredients look like a list
        self.assertIn("ingredients", recipe)
        self.assertIsInstance(recipe["ingredients"], list)
        self.assertGreater(len(recipe["ingredients"]), 0)

    # -----------------------------------------
    # TC-REC-02: diet mode + violation -> infeasible
    # -----------------------------------------

    def test_generate_compliant_recipe_diet_pref_violation_infeasible(self):
        """
        TC-REC-02:
        Integration-style test.

        Given a diet mode preference and a dish with (a) violating ingredient(s),
        when we call generate_compliant_recipe(),
        then it should fail feasibility and the final error message
        should say that the recipe violates the diet mode preference (ex. vegan) and
        contains some blocked ingredient (ex. chicken).
        """
        # vegan preferences 
        prefs = {
            "diet_mode": "vegan",
            "exclusions": []
        }

        # search locally first, then call the Spoonacular API
        result = self.recipe_ctrl.generateCompliantRecipe("chicken alfredo", prefs)

        # 1) overall operation should fail (infeasible)
        self.assertFalse(result["success"])

        # 2) build the same full message the CLI prints:
        full_msg = f"Error: {result['message']}"

        # 3) Check that message is in the expected general form
        self.assertIn("Error: Recipe violates", full_msg)
        self.assertIn("(contains:", full_msg)


    # -----------------------------------------
    # TC-REC-03: diet mode + no violations -> feasible
    # -----------------------------------------

    def test_generate_compliant_recipe_diet_pref_no_violation_feasible(self):
        """
        TC-REC-03:
        Integration-style test.

        Given a diet mode preference and a dish with no violating ingredients,
        when we call generate_compliant_recipe(),
        then it should pass feasibility and the message
        should include the recipe.
        """
        # vegetarian preferences
        prefs = {
            "diet_mode": "vegetarian",
            "exclusions": []
        }

        # search locally first, then call the Spoonacular API
        result = self.recipe_ctrl.generateCompliantRecipe("potato salad", prefs)

        # result should include a recipe dict
        self.assertIn("recipe", result)
        recipe = result["recipe"]
        self.assertIsInstance(recipe, dict)

        self.assertIn("dish_name", recipe)
        self.assertIn("ingredients", recipe)
        self.assertIn("steps", recipe)

    def test_generate_compliant_recipe_excluded_ingredient_violation_infeasible(self):
        """
        TC-REC-04:
        Integration-style test.

        Given the user has exclusions and theres a dish with (a) violating ingredient(s),
        when we call generate_compliant_recipe(),
        then it should fail feasibility and the final error message
        should say that the recipe violates the excluded ingredient preference (ex. potato).
        """
        # vegetarian preferences 
        prefs = {
            "diet_mode": "vegetarian",
            "exclusions": ["potato", "potatoe"]
        }

        # search locally first, then call the Spoonacular API
        result = self.recipe_ctrl.generateCompliantRecipe("potato salad", prefs)

        # 1) overall operation should fail (infeasible)
        self.assertFalse(result["success"])

        # 2) build the same full message the CLI prints
        full_msg = f"Error: {result['message']}"

        # 3) check that message is in the expected general form
        self.assertIn("Error: Contains excluded ingredient:", full_msg)

    def test_generate_compliant_recipe_excluded_ingredient_no_violation_feasible(self):
        """
        TC-REC-05:
        Integration-style test.

        Given the user has exclusions and theres a dish with no violating ingredients,
        when we call generate_compliant_recipe(),
        then it should pass feasibility and the message should include the recipe.
        """
        # vegetarian preferences
        prefs = {
            "diet_mode": "vegetarian",
            "exclusions": ["potato", "potatoe"]
        }

        # search locally first, then call the Spoonacular API
        result = self.recipe_ctrl.generateCompliantRecipe("chickpea salad", prefs)

        # 1) Overall operation should fail (infeasible)
        self.assertTrue(result["success"])

        self.assertIn("recipe", result)
        recipe = result["recipe"]
        self.assertIsInstance(recipe, dict)

        self.assertIn("dish_name", recipe)
        self.assertIn("ingredients", recipe)
        self.assertIn("steps", recipe)

    def test_generate_compliant_recipe_no_preferences_always_feasible(self):
        """
        TC-REC-06:
        Integration-style test.

        Given the user has no preferences, the program should result in a recipe.
        """
        prefs = {
            "diet_mode": "",
            "exclusions": []
        }

        # search locally first, then call the Spoonacular API
        result = self.recipe_ctrl.generateCompliantRecipe("chickpea salad", prefs)

        # 1) overall operation should fail (infeasible)
        self.assertTrue(result["success"])

        self.assertIn("recipe", result)
        recipe = result["recipe"]
        self.assertIsInstance(recipe, dict)

        self.assertIn("dish_name", recipe)
        self.assertIn("ingredients", recipe)
        self.assertIn("steps", recipe)
    
    


if __name__ == "__main__":
    unittest.main()

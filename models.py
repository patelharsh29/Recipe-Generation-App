# models.py
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime
import hashlib
import os
import json

@dataclass
class User:
    username: str
    password: str

@dataclass
class Preferences:
    username: str
    diet_mode: str = "none"
    exclusions: List[str] = field(default_factory=list)

@dataclass
class RecipeRequest:
    dish_name: str
    diet_mode: str = "none"
    exclusions: List[str] = field(default_factory=list)

@dataclass
class Ingredient:
    name: str
    quantity: Optional[str] = None

@dataclass
class Substitution:
    originalIngredient: str
    replacementIngredient: str
    rationale: str

@dataclass
class Recipe:
    dish_name: str
    ingredients: List[Ingredient]
    steps: List[str]

@dataclass
class CompletedRecipe(Recipe):
    feasible: bool = False
    substitutions: List[Substitution] = field(default_factory=list)

@dataclass
class FeasibilityResult:
    feasible: bool
    recipe: Optional[Recipe] = None
    substitutions: List[Substitution] = field(default_factory=list)
    blockers: List[str] = field(default_factory=list)
    message: Optional[str] = None

# Authentication helpers
def hash_password(password: str, salt: str):
    return hashlib.sha256((salt + password).encode("utf-8")).hexdigest()

def gen_salt():
    return os.urandom(8).hex()



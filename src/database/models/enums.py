from enum import StrEnum

class Language(StrEnum):
    EN = "en"
    PL = "pl"

class ItemTag(StrEnum):
    BOWL = "bowl"
    POT = "pot"
    PAN = "pan"
    CUTLERY = "cutlery"
    MIXER = "mixer"
    BOARD = "board"
    KNIFE = "knife"
    OTHER = "other"

class DifficultyLevel(StrEnum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"

class IngredientAction(StrEnum):
    ADD = "add"
    BLEND = "blend"
    CHOP = "chop"
    GRATE = "grate"
    MELT = "melt"
    MINCE = "mince"
    PEEL = "peel"
    SLICE = "slice"

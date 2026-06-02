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
    BEGINNER = "Beginner"
    INTERMEDIATE = "Intermediate"
    MASTER_CHEF = "Master Chef"

class IngredientAction(StrEnum):
    ADD = "add"
    BLEND = "blend"
    CHOP = "chop"
    GRATE = "grate"
    MELT = "melt"
    MINCE = "mince"
    PEEL = "peel"
    SLICE = "slice"

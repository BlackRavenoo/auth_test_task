import enum

class ResourceType(str, enum.Enum):
    USERS = "users"
    ROLES = "roles"
    ITEMS = "items"

class ItemRarity(str, enum.Enum):
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    VERY_RARE = "very-rare"
    LEGENDARY = "legendary"
    ARTIFACT = "artifact"
    VARIES = "varies"

class ActionType(str, enum.Enum):
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
import enum


class SortOrderEnum(str, enum.Enum):
    asc = "asc"
    desc = "desc"


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    USER = "user"

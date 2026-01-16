from enum import Enum


class DBEnv(str, Enum):
    PROD = "prod"
    EXP = "exp"
    TEST = "test"

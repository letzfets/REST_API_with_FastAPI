from functools import lru_cache  # Least Recently Used Cache
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class BaseConfig(BaseSettings):
    ENV_STATE: Optional[str] = None  # set to "development", "test", or "production

    """Loads the .env file and sets the configuration variables"""
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


class GlobalConfig(BaseConfig):
    """This is the GlobalConfig class"""

    DATABASE_URL: Optional[str] = None
    DB_FORCE_ROLL_BACK: bool = False
    SECRET_KEY: Optional[str] = None
    ALGORITHM: Optional[str] = None
    ACCESS_TOKEN_EXPIRE_MINUTES: Optional[int] = 30
    MAILGUN_API_KEY: Optional[str] = None
    MAILGUN_DOMAIN: Optional[str] = None


class DevConfig(GlobalConfig):
    """This is the Development class"""

    # only uses the variables prefixed names with "DEV_"
    # stripes off the prefix and assigns the rest to the variable
    model_config = SettingsConfigDict(env_prefix="DEV_")


class TestConfig(GlobalConfig):
    """This is the Development class"""

    model_config = SettingsConfigDict(env_prefix="TEST_")
    DATABASE_URL: str = "sqlite:///test.db"
    DB_FORCE_ROLL_BACK: bool = True


class ProdConfig(GlobalConfig):
    """This is the Development class"""

    model_config = SettingsConfigDict(env_prefix="PROD_")


# cache this function, so that it never runs more than once
@lru_cache()
def get_config(env_state: str):
    configs = {"development": DevConfig, "test": TestConfig, "production": ProdConfig}
    return configs[env_state]()


# reads the .env file and ONLY gets the ENV_STATE variable
# "ENV_STATE" is outside the configuration classes,
# and therefore not prefixed with "DEV_", "TEST_" or "PROD_"
config = get_config(BaseConfig().ENV_STATE)

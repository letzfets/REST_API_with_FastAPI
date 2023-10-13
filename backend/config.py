from functools import lru_cache  # Least Recently Used Cache
from typing import Optional

from pydantic import BaseSettings
from pydantic_settings import SettingsConfigDict


class BaseConfig(BaseSettings):
    """This is the BaseConfig class"""

    class Config:
        """This is the Config class"""

        ENV_STATE: Optional[str] = None  # set to "development", "test", or "production

        env_file = ".env"


class GlobalConfig(BaseConfig):
    """This is the GlobalConfig class"""

    DATABASE_URL: Optional[str] = None
    DB_FORCE_ROLL_BACK: bool = False


class DevConfig(GlobalConfig):
    """This is the Development class"""

    # only uses the variables prefixed names with "DEV_"
    # stripes off the prefix and assigns the rest to the variable
    model_config = SettingsConfigDict(env_prefix="DEV_")


class TestConfig(GlobalConfig):
    """This is the Development class"""

    DATABASE_URL: str = "sqlite:///./test.db"
    DB_FORCE_ROLL_BACK: bool = True


class ProdConfig(GlobalConfig):
    """This is the Development class"""

    model_config = SettingsConfigDict(env_prefix="PROD_")


# cache this function, so that it never runs more than once
@lru_cache()
def get_config(env_state: str):
    configs = {"dev": DevConfig, "test": TestConfig, "production": ProdConfig}
    return configs[env_state]()


# reads the .env file and ONLY gets the ENV_STATE variable
# "ENV_STATE" is outside the configuration classes,
# and therefore not prefixed with "DEV_", "TEST_" or "PROD_"
config = get_config(BaseConfig().ENV_STATE)

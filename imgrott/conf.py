from typing import ClassVar

from pydantic import Field
from pydantic_core import PydanticUndefined
from pydantic_settings import BaseSettings, SettingsConfigDict

from imgrott.constants import (
    DEFAULT_ADDR,
    DEFAULT_PORT,
    GROWATT_SERVER_ADDR,
    GROWATT_SERVER_PORT,
)

ENV_PREFIX = "IMGROTT_"
ENV_FILE = "imgrott.env"


class ImGrottBaseSettings(BaseSettings):
    extension_name: ClassVar = ""

    @classmethod
    def from_argparser(cls, parser):
        """
        Loads configuration from Command Line Arguments
        """
        return cls(**vars(parser))

    @classmethod
    def to_argparser(cls, parser):
        """
        Converts Pydantic model to ArgumentParser.
        """
        # TODO Still need to improve this function
        fields = cls.model_fields
        for name, field in fields.items():
            required = (
                True
                if field.default in [None, PydanticUndefined] and field.default_factory is None
                else False
            )
            default = None if field.default == PydanticUndefined else field.default
            arg_name = f"--{cls.extension_name}_{name}" if cls.extension_name else f"--{name}"
            kwargs = {
                "dest": name,
                "required": required,
                "help": field.description
            }

            if field.annotation is bool:
                kwargs["action"] = "store_false" if field.default is True else "store_true"
            else:
                kwargs["type"] = field.annotation
                kwargs["default"] = default
            parser.add_argument(arg_name, **kwargs)


class Settings(ImGrottBaseSettings):
    model_config = SettingsConfigDict(env_prefix=ENV_PREFIX, env_file=ENV_FILE, extra="ignore")
    addr: str = Field(DEFAULT_ADDR)
    port: int = Field(DEFAULT_PORT)
    growatt_addr: str = Field(GROWATT_SERVER_ADDR)
    growatt_port: int = Field(GROWATT_SERVER_PORT)
    forward: bool = Field(True)
    extensions: list[str] = Field(default_factory=list)
    debug: bool = Field(False)

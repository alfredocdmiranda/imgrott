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


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix=ENV_PREFIX, env_file="imgrott.env")
    addr: str = Field(DEFAULT_ADDR)
    port: int = Field(DEFAULT_PORT)
    growatt_addr: str = Field(GROWATT_SERVER_ADDR)
    growatt_port: int = Field(GROWATT_SERVER_PORT)
    forward: bool = Field(True)
    extensions: list[str] = Field(default_factory=list)

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
                if field.default in [None, PydanticUndefined]
                and field.default_factory is None
                else False
            )
            default = None if field.default == PydanticUndefined else field.default
            parser.add_argument(
                f"--{name}",
                dest=name,
                type=field.annotation,
                default=default,
                required=required,
                help=field.description,
            )

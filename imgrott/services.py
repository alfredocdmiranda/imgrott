import argparse
import importlib
import logging

from imgrott.messages import Message

EXTENSION_MODULE = "imgrott.extensions"
logger = logging.getLogger(__name__)


class ExtensionsService:
    def __init__(self):
        self.extensions = {}

    def execute(self, message: Message | None) -> None:
        for extension_name, extension_obj in self.extensions.items():
            logger.debug(f"Executing extension [{extension_name}]")
            extension_obj.run(message)

    def load_extensions(self, list_extensions: list[str], list_args: list[str]) -> None:
        unknown = list_args
        for extension in list_extensions:
            parser = argparse.ArgumentParser()
            module = importlib.import_module(f"{EXTENSION_MODULE}.{extension}")
            module_settings = getattr(module, "Settings")
            module_settings.to_argparser(parser)
            args, unknown = parser.parse_known_args(unknown)
            settings = module_settings.from_argparser(args)
            extension_class = getattr(module, "Extension")
            self.extensions[extension] = extension_class(settings)

    def print_help(self, extension: str) -> None:
        parser = argparse.ArgumentParser()
        module = importlib.import_module(f"{EXTENSION_MODULE}.{extension}")
        module_settings = getattr(module, "Settings")
        module_settings.to_argparser(parser)
        parser.print_help()

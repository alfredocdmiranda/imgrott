from abc import ABC, abstractmethod

from imgrott.conf import ImGrottBaseSettings
from imgrott.messages import Message


class BaseExtension(ABC):
    def __init__(self, config: ImGrottBaseSettings):
        self.config = config

    @abstractmethod
    def run(self, message: Message):
        raise NotImplementedError()

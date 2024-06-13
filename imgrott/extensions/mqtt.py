import json
from typing import ClassVar

import paho.mqtt.publish as publish
from pydantic import Field
from pydantic_settings import SettingsConfigDict

from imgrott.enums import MessageType
from imgrott.extensions.base import BaseExtension
from imgrott.conf import ImGrottBaseSettings, ENV_FILE
from imgrott.messages import Message

ENV_PREFIX = "IMGROTT_MQTT_"
DEFAULT_MQTT_TOPIC = "energy/growatt"


class Settings(ImGrottBaseSettings):
    extension_name: ClassVar = "mqtt"
    model_config = SettingsConfigDict(
        env_prefix=ENV_PREFIX, env_file=ENV_FILE, extra="ignore"
    )
    addr: str = Field(description="MQTT host address")
    port: int = Field(description="MQTT host port")
    user: str = Field("", description="MQTT user")
    passwd: str = Field("", description="MQTT password")
    topic: str = Field(
        DEFAULT_MQTT_TOPIC, description="Topic where it will be published the message"
    )
    retain: bool = Field(False, description="Tell MQTT to retain message")


class Extension(BaseExtension):
    def execute(self, message: Message) -> None:
        auth = None
        if self.config.user and self.config.passwd:
            auth = {"username": self.config.user, "password": self.config.passwd}

        retain = False
        json_msg = json.dumps(self._to_json(message))
        publish.single(
            self.config.topic,
            payload=json_msg,
            qos=0,
            retain=retain,
            hostname=self.config.addr,
            port=self.config.port,
            client_id=message.datalogger_sn,
            keepalive=60,
            auth=auth,
        )

    @staticmethod
    def _to_json(message: Message) -> str:
        """
        Converts to json to be sent to MQTT. Tried to keep same format from Grott.
        """
        device_id = message.inverter_sn
        if message.type == MessageType.SmartMeterData:
            device_id = message.datalogger_sn

        values = {
            "datalogserial": message.datalogger_sn,
            "pvserial": message.inverter_sn,
            **message.data,
        }

        json_obj = {
            "device": device_id,
            "time": message.date.strftime("%Y-%m-%dT%H:%M:%S"),
            "buffered": "no",
            "values": values,
        }

        return json.dumps(json_obj)

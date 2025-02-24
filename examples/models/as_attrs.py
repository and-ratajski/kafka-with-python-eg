from datetime import datetime
from enum import Enum
from uuid import UUID, uuid4

from attrs import asdict, define, field
from typing_extensions import Optional


def serialize_value(_, __, value):
    if isinstance(value, Enum):
        return value.value
    elif isinstance(value, UUID):
        return str(value)
    elif isinstance(value, datetime):
        return int(value.timestamp() * 1000)
    return value


class Converters:

    @staticmethod
    def to_uuid(value):
        return UUID(value) if isinstance(value, str) else value

    @staticmethod
    def to_ts(value):
        return datetime.fromtimestamp(value / 1000) if isinstance(value, int) else value

    @staticmethod
    def to_subscription(value):
        return SubscriptionType(value) if isinstance(value, str) else value

    @staticmethod
    def to_envelope(value):
        return EventEnvelope(**value) if isinstance(value, dict) else value


class SubscriptionType(str, Enum):
    FREE = "FREE"
    LITE = "LITE"
    PRO = "PRO"


@define
class EventEnvelope:
    envelope_id: UUID = field(factory=uuid4, converter=Converters.to_uuid)
    parent_id: Optional[UUID] = field(default=None, converter=Converters.to_uuid)
    event_timestamp: datetime = field(factory=datetime.now, converter=Converters.to_ts)
    app_name: str = field(default="kafka_mocha_on_attrs")
    app_version: str = field(default="1.0.0")


@define
class UserRegistered:
    user_id: UUID = field(converter=Converters.to_uuid)
    user_name: str
    user_last_name: str
    is_new_user: bool
    subscription_type: SubscriptionType = field(converter=Converters.to_subscription)
    registration_timestamp: datetime = field(converter=Converters.to_ts)
    score: float
    _envelope: EventEnvelope = field(alias="_envelope", converter=Converters.to_envelope)

    @property
    def envelope(self) -> EventEnvelope:
        return self._envelope

    @envelope.setter
    def envelope(self, value: EventEnvelope | dict) -> None:
        self._envelope = EventEnvelope(**value) if isinstance(value, dict) else value

    def to_dict(self):
        return asdict(self, value_serializer=serialize_value)

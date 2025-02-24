from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4


def dict_factory(data) -> dict:
    """Converts dataclass to dictionary with custom conversion for UUID, Enum and datetime."""

    def convert(obj):
        if isinstance(obj, Enum):
            return obj.value
        elif isinstance(obj, UUID):
            return str(obj)
        elif isinstance(obj, datetime):
            return int(obj.timestamp() * 1000)
        return obj

    return {k: convert(v) for k, v in data}


class SubscriptionType(str, Enum):
    FREE = "FREE"
    LITE = "LITE"
    PRO = "PRO"


@dataclass(slots=True)
class EventEnvelope:
    envelope_id: UUID = field(default_factory=uuid4)
    parent_id: Optional[UUID] = field(default=None)
    event_timestamp: datetime = field(default_factory=datetime.now)
    app_name: str = field(default="kafka_mocha_on_dataclass")
    app_version: str = field(default="1.0.0")

    def __post_init__(self):
        self.envelope_id = UUID(self.envelope_id) if isinstance(self.envelope_id, str) else self.envelope_id
        self.parent_id = UUID(self.parent_id) if isinstance(self.parent_id, str) else self.parent_id
        if isinstance(self.event_timestamp, int):
            self.event_timestamp = datetime.fromtimestamp(self.event_timestamp / 1000)


@dataclass(slots=True)
class UserRegistered:
    user_id: UUID
    user_name: str
    user_last_name: str
    is_new_user: bool
    subscription_type: SubscriptionType
    registration_timestamp: datetime
    score: float
    _envelope: EventEnvelope

    @property
    def envelope(self) -> EventEnvelope:
        return self._envelope

    @envelope.setter
    def envelope(self, value: EventEnvelope | dict) -> None:
        self._envelope = EventEnvelope(**value) if isinstance(value, dict) else value

    def __post_init__(self):
        self.user_id = UUID(self.user_id) if isinstance(self.user_id, str) else self.user_id
        if isinstance(self.subscription_type, str):
            self.subscription_type = SubscriptionType(self.subscription_type)
        if isinstance(self.registration_timestamp, int):
            self.registration_timestamp = datetime.fromtimestamp(self.registration_timestamp / 1000)
        if isinstance(self._envelope, dict):
            self.envelope = EventEnvelope(**self._envelope)

    def to_dict(self):
        return asdict(self, dict_factory=dict_factory)

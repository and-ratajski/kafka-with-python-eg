from datetime import datetime
from enum import Enum
from uuid import UUID, uuid4


def serialize_value(value):
    if hasattr(value, "to_dict"):
        return value.to_dict()
    elif isinstance(value, Enum):
        return value.value
    elif isinstance(value, UUID):
        return str(value)
    elif isinstance(value, datetime):
        return int(value.timestamp() * 1000)
    return value


class SubscriptionType(str, Enum):
    FREE = "FREE"
    LITE = "LITE"
    PRO = "PRO"


class EventEnvelope:
    __slots__ = ("envelope_id", "event_timestamp", "app_name", "app_version")

    def __init__(self, envelope_id: UUID | str | None = None, event_timestamp: datetime | int | None = None, app_name: str = "kafka_mocha_on_vanilla", app_version: str = "1.0.0"):
        if envelope_id is None:
            self.envelope_id = uuid4()
        else:
            self.envelope_id = UUID(envelope_id) if isinstance(envelope_id, str) else envelope_id
        if event_timestamp is None:
            self.event_timestamp = datetime.now()
        else:
            self.event_timestamp = datetime.fromtimestamp(event_timestamp / 1000) if isinstance(event_timestamp, int) else event_timestamp
        self.app_name = app_name
        self.app_version = app_version

    def to_dict(self):
        return {field_name: serialize_value(self.__getattribute__(field_name)) for field_name in self.__slots__}

    def __repr__(self):
        return f"EventEnvelope(envelope_id={self.envelope_id}, event_timestamp={self.event_timestamp}, app_name={self.app_name}, app_version={self.app_version})"


class UserRegistered:
    __slots__ = ("user_id", "user_name", "user_last_name", "is_new_user", "subscription_type", "registration_timestamp", "score", "envelope")

    def __init__(self, user_id: UUID | str, user_name: str, user_last_name: str, is_new_user: bool, subscription_type: SubscriptionType | str, registration_timestamp: datetime | int, score: float, envelope: EventEnvelope | dict):
        self.user_id = UUID(user_id) if isinstance(user_id, str) else user_id
        self.user_name = user_name
        self.user_last_name = user_last_name
        self.is_new_user = is_new_user
        self.subscription_type = SubscriptionType(subscription_type) if isinstance(subscription_type, str) else subscription_type
        self.registration_timestamp = datetime.fromtimestamp(registration_timestamp / 1000) if isinstance(registration_timestamp, int) else registration_timestamp
        self.score = score
        self.envelope = EventEnvelope(**envelope) if isinstance(envelope, dict) else envelope

    def to_dict(self):
        return {field_name: serialize_value(self.__getattribute__(field_name)) for field_name in self.__slots__}

    def __repr__(self):
        return f"UserRegistered(user_id={self.user_id}, user_name={self.user_name}, user_last_name={self.user_last_name}, is_new_user={self.is_new_user}, subscription_type={self.subscription_type}, registration_timestamp={self.registration_timestamp}, score={self.score}, envelope={self.envelope})"

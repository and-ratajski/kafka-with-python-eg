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
    __slots__ = ("envelope_id", "parent_id", "event_timestamp", "app_name", "app_version")

    def __init__(
        self,
        envelope_id: UUID | str | None = None,
        parent_id: UUID | str | None = None,
        event_timestamp: datetime | int | None = None,
        app_name: str = "kafka_mocha_on_vanilla",
        app_version: str = "1.0.0",
    ):
        if envelope_id is None:
            self.envelope_id = uuid4()
        else:
            self.envelope_id = UUID(envelope_id) if isinstance(envelope_id, str) else envelope_id
        if parent_id is None:
            self.parent_id = None
        else:
            self.parent_id = UUID(parent_id) if isinstance(parent_id, str) else parent_id
        if event_timestamp is None:
            self.event_timestamp = datetime.now()
        else:
            self.event_timestamp = (
                datetime.fromtimestamp(event_timestamp / 1000) if isinstance(event_timestamp, int) else event_timestamp
            )
        self.app_name = app_name
        self.app_version = app_version

    def to_dict(self) -> dict:
        obj_dict = {}
        for field_name in self.__slots__:
            if hasattr(self, field_name):
                obj_dict[field_name] = serialize_value(self.__getattribute__(field_name))
        return obj_dict

    def __repr__(self):
        return (
            f"EventEnvelope("
            f"envelope_id={self.envelope_id}, "
            f"parent_id={self.parent_id}, "
            f"event_timestamp={self.event_timestamp}, "
            f"app_name={self.app_name}, "
            f"app_version={self.app_version})"
        )


class UserRegistered:
    __slots__ = (
        "user_id",
        "user_name",
        "user_last_name",
        "is_new_user",
        "subscription_type",
        "registration_timestamp",
        "score",
        "_envelope",
    )

    def __init__(
        self,
        user_id: UUID | str,
        user_name: str,
        user_last_name: str,
        is_new_user: bool,
        subscription_type: SubscriptionType | str,
        registration_timestamp: datetime | int,
        score: float,
        _envelope: EventEnvelope | dict,
    ):
        self.user_id = UUID(user_id) if isinstance(user_id, str) else user_id
        self.user_name = user_name
        self.user_last_name = user_last_name
        self.is_new_user = is_new_user
        self.subscription_type = (
            SubscriptionType(subscription_type) if isinstance(subscription_type, str) else subscription_type
        )
        self.registration_timestamp = (
            datetime.fromtimestamp(registration_timestamp / 1000)
            if isinstance(registration_timestamp, int)
            else registration_timestamp
        )
        self.score = score
        self._envelope = EventEnvelope(**_envelope) if isinstance(_envelope, dict) else _envelope

    @property
    def envelope(self) -> EventEnvelope:
        return self._envelope

    @envelope.setter
    def envelope(self, value: EventEnvelope | dict) -> None:
        self._envelope = EventEnvelope(**value) if isinstance(value, dict) else value

    def to_dict(self) -> dict:
        return {field_name: serialize_value(self.__getattribute__(field_name)) for field_name in self.__slots__}

    def __repr__(self):
        return (
            f"UserRegistered("
            f"user_id={self.user_id}, "
            f"user_name={self.user_name}, "
            f"user_last_name={self.user_last_name}, "
            f"is_new_user={self.is_new_user}, "
            f"subscription_type={self.subscription_type}, "
            f"registration_timestamp={self.registration_timestamp}, s"
            f"core={self.score}, "
            f"_envelope={self._envelope})"
        )

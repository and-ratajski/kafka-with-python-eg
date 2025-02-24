from datetime import datetime
from enum import Enum
from typing import Annotated, Optional
from uuid import UUID, uuid4

from pydantic import AfterValidator, BaseModel, ConfigDict, Field, PlainSerializer


class SubscriptionType(str, Enum):
    FREE = "FREE"
    LITE = "LITE"
    PRO = "PRO"


EnsuredUUID = Annotated[
    UUID, AfterValidator(lambda v: UUID(v) if isinstance(v, str) else v), PlainSerializer(lambda v: str(v))
]
EnsuredDatetime = Annotated[
    datetime,
    AfterValidator(lambda v: datetime.fromtimestamp(v / 1000) if isinstance(v, int) else v),
    PlainSerializer(lambda v: int(v.timestamp() * 1000) if isinstance(v, datetime) else v),
]
EnsuredSubscriptionType = Annotated[
    SubscriptionType,
    AfterValidator(lambda v: SubscriptionType(v) if isinstance(v, str) else v),
    PlainSerializer(lambda v: v.value if isinstance(v, Enum) else v),
]


class EventEnvelope(BaseModel):
    envelope_id: EnsuredUUID = Field(default_factory=uuid4)
    parent_id: Optional[EnsuredUUID] = Field(None)
    event_timestamp: EnsuredDatetime = Field(default_factory=datetime.now)
    app_name: str = Field(default="kafka_mocha_on_pydantic")
    app_version: str = Field(default="1.0.0")

    model_config = ConfigDict(cache_strings=False)


class UserRegistered(BaseModel):
    user_id: EnsuredUUID
    user_name: str
    user_last_name: str
    is_new_user: bool
    subscription_type: EnsuredSubscriptionType
    registration_timestamp: EnsuredDatetime
    score: float
    envelope: EventEnvelope = Field(default_factory=EventEnvelope, alias="_envelope")

    model_config = ConfigDict(cache_strings=False)

    def to_dict(self):
        return self.model_dump(by_alias=True)

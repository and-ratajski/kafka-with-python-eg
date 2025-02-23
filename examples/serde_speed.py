import matplotlib.pyplot as plt
import numpy as np
import json
import os
import time
from datetime import datetime
from uuid import uuid4

from confluent_kafka.schema_registry.avro import AvroSerializer, AvroDeserializer
from confluent_kafka.serialization import SerializationContext, MessageField

from kafka_mocha.schema_registry.mock_schema_registry_client import MockSchemaRegistryClient

from examples.models.as_vanilla_python import UserRegistered as UserRegistered__vanilla
from examples.models.as_attrs import UserRegistered as UserRegistered__attrs
from examples.models.as_dataclass import UserRegistered as UserRegistered__dataclass
from examples.models.as_pydantic import UserRegistered as UserRegistered__pydantic
from examples.models.as_vanilla_python import EventEnvelope as EventEnvelope__vanilla
from examples.models.as_attrs import EventEnvelope as EventEnvelope__attrs
from examples.models.as_dataclass import EventEnvelope as EventEnvelope__dataclass
from examples.models.as_pydantic import EventEnvelope as EventEnvelope__pydantic

LOCAL_SCHEMA = str(os.path.join(os.path.dirname(__file__), "schemas/user-registered.avsc"))
TEST_RUNS = 100_000


def serde_event(serializer: AvroSerializer, deserializer: AvroDeserializer, model_class, event) -> object:
    """Serialize and Deserialize event using AvroSerializer and AvroDeserializer for tested model."""
    avro_message = serializer(event.to_dict(), SerializationContext("user-topic", MessageField.VALUE))
    des_event = deserializer(avro_message, SerializationContext("ser-topic", MessageField.VALUE))

    return model_class(**des_event)


def check_speed():
    """Use Mock Schema Registry client to auto-register the schema, serialise and produce AVRO message.

    # >>> auto_register_schema()
    AVRO message delivered (auto.register.schemas = True)
    """
    schema_registry = MockSchemaRegistryClient({"url": "http://localhost:8081"})
    with open(LOCAL_SCHEMA, "r") as f:
        avro_schema = json.loads(f.read())
        avro_schema_str = json.dumps(avro_schema)

    avro_serializer = AvroSerializer(
        schema_registry,
        avro_schema_str,
        conf={"auto.register.schemas": True},
    )
    avro_deserializer = AvroDeserializer(
        schema_registry,
        avro_schema_str,
    )

    user_id = uuid4()
    event_van = UserRegistered__vanilla(
        user_id, "John", "Attrivani", True, "LITE", datetime.now(), 7.2, EventEnvelope__vanilla()
    )
    event_at = UserRegistered__attrs(
        user_id, "John", "Attrivani", True, "LITE", datetime.now(), 7.2, EventEnvelope__attrs()
    )
    event_dc = UserRegistered__dataclass(
        user_id, "John", "Dataclassovsky", True, "FREE", datetime.now(), 0.0, EventEnvelope__dataclass()
    )
    event_pd = UserRegistered__pydantic(
        user_id=user_id,
        user_name="John",
        user_last_name="Pydanticola",
        is_new_user=True,
        subscription_type="PRO",
        registration_timestamp=datetime.now(),
        score=7.2,
        envelope=EventEnvelope__pydantic(),
    )

    output_event = None
    serde_event(avro_serializer, avro_deserializer, UserRegistered__attrs, event_at)  # Warm-up

    start_time = time.time()
    for _ in range(TEST_RUNS):
        output_event = serde_event(avro_serializer, avro_deserializer, UserRegistered__vanilla, event_van)
    elapsed_time = time.time() - start_time
    print("\n")
    print(f"[VANILLA] Execution time (total): {elapsed_time:.5f} seconds")
    print(f"[VANILLA] Execution time (per message): {(van_time := (elapsed_time / TEST_RUNS) * 1e6):.3f} microseconds")
    print(f"[VANILLA] Maximal throughput: {(van_msgs := int(1 / (elapsed_time / TEST_RUNS)))} messages/sec\n")

    # print(event_van)
    # print(str(output_event) + "\n\n")

    start_time = time.time()
    for _ in range(TEST_RUNS):
        output_event = serde_event(avro_serializer, avro_deserializer, UserRegistered__attrs, event_at)
    elapsed_time = time.time() - start_time
    print(f"[ATTRS] Execution time (total): {elapsed_time:.5f} seconds")
    print(f"[ATTRS] Execution time (per message): {(attrs_time := (elapsed_time / TEST_RUNS) * 1e6):.3f} microseconds")
    print(f"[ATTRS] Maximal throughput: {(attrs_msgs := int(1 / (elapsed_time / TEST_RUNS)))} messages/sec\n")

    # print(event_at)
    # print(str(output_event) + "\n\n")

    start_time = time.time()
    for _ in range(TEST_RUNS):
        output_event = serde_event(avro_serializer, avro_deserializer, UserRegistered__dataclass, event_dc)
    elapsed_time = time.time() - start_time
    print(f"[DATACLASS] Execution time: {elapsed_time:.5f} seconds")
    print(f"[DATACLASS] Execution time (per message): {(dc_time := (elapsed_time / TEST_RUNS) * 1e6):.3f} microseconds")
    print(f"[DATACLASS] Maximal throughput: {(dc_msgs := int(1 / (elapsed_time / TEST_RUNS)))} messages/sec\n")

    # print(event_dc)
    # print(str(output_event) + "\n\n")

    start_time = time.time()
    for _ in range(TEST_RUNS):
        output_event = serde_event(avro_serializer, avro_deserializer, UserRegistered__pydantic, event_pd)
    elapsed_time = time.time() - start_time
    print(f"[PYDANTIC] Execution time: {elapsed_time:.5f} seconds")
    print(f"[PYDANTIC] Execution time (per message): {(pd_time := (elapsed_time / TEST_RUNS) * 1e6):.3f} microseconds")
    print(f"[PYDANTIC] Maximal throughput: {(pd_msgs := int(1 / (elapsed_time / TEST_RUNS)))} messages/sec\n")

    # print(event_pd)
    # print(str(output_event) + "\n\n")

    libraries = ["vanilla python", "attrs", "dataclass", "pydantic"]
    times = [van_time, attrs_time, dc_time, pd_time]
    messages = [van_msgs, attrs_msgs, dc_msgs, pd_msgs]

    # Calculate y positions for bars
    y_pos = np.arange(len(libraries))
    width = 0.35  # Width of bars
    y1 = y_pos - width / 2  # First set of bars
    y2 = y_pos + width / 2  # Second set of bars
    fig, ax1 = plt.subplots()

    ax1.set_xlabel("Serde time (microseconds)")
    ax1.set_ylabel("Library")
    ax1.barh(y1, times, height=0.9*width, color='blue', label='Time')
    ax1.set_yticks(y_pos)
    ax1.set_yticklabels(libraries)

    ax2 = ax1.twiny()
    ax2.set_xlabel("Maximal throughput (messages/sec)")
    ax2.barh(y2, messages, height=0.9*width, color='red', alpha=0.5, label='Throughput')

    plt.title("Library Performance Comparison")
    ax2.legend(loc='center left', bbox_to_anchor=(1.0, 0.3))
    ax1.legend(loc='center left', bbox_to_anchor=(1.0, 0.5))

    fig.tight_layout(rect=[0, 0, 0.9, 1])
    fig.tight_layout()
    plt.savefig("outputs/serde_speed.png")
    plt.show()


if __name__ == "__main__":
    check_speed()

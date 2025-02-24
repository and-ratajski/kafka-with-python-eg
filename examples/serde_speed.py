import json
import os
import time
from datetime import datetime
from uuid import uuid4

from confluent_kafka.schema_registry.avro import AvroDeserializer, AvroSerializer
from confluent_kafka.serialization import MessageField, SerializationContext
from kafka_mocha.schema_registry.mock_schema_registry_client import MockSchemaRegistryClient

from examples._argparsers import serde_speed_argparse
from examples._plotters import plot_serde_speed_chart
from examples.models.as_attrs import EventEnvelope as EventEnvelope__attrs
from examples.models.as_attrs import UserRegistered as UserRegistered__attrs
from examples.models.as_dataclass import EventEnvelope as EventEnvelope__dataclass
from examples.models.as_dataclass import UserRegistered as UserRegistered__dataclass
from examples.models.as_pydantic import EventEnvelope as EventEnvelope__pydantic
from examples.models.as_pydantic import UserRegistered as UserRegistered__pydantic
from examples.models.as_vanilla_python import EventEnvelope as EventEnvelope__vanilla
from examples.models.as_vanilla_python import UserRegistered as UserRegistered__vanilla


def serde_event(serializer: AvroSerializer, deserializer: AvroDeserializer, model_class, event) -> object:
    """Serialize and Deserialize event using AvroSerializer and AvroDeserializer for tested model."""
    ser_message = serializer(event.to_dict(), SerializationContext("input-topic", MessageField.VALUE))
    de_event = deserializer(ser_message, SerializationContext("output-topic", MessageField.VALUE))

    # Simulate minimal processing
    de_event["_envelope"]["parent_id"] = event.envelope.envelope_id
    de_event["_envelope"]["envelope_id"] = uuid4()

    return model_class(**de_event)


def check_speed(local_schema: str, test_runs: int, verbose: bool = False, gen_chart: bool = False) -> None:
    """Use Mock Schema Registry client to auto-register the schema, serialise and produce AVRO message.

    # >>> auto_register_schema()
    AVRO message delivered (auto.register.schemas = True)
    """
    libraries = ["vanilla python", "attrs", "dataclass", "pydantic"]

    schema_registry = MockSchemaRegistryClient({"url": "http://localhost:8081"})
    with open(local_schema, "r") as f:
        avro_schema = json.loads(f.read())
        avro_schema_str = json.dumps(avro_schema)

    avro_serializer = AvroSerializer(
        schema_registry,
        avro_schema_str,
        conf={"auto.register.schemas": True},
    )
    avro_deserializer = AvroDeserializer(schema_registry, avro_schema_str)

    user_id = uuid4()
    event_van = UserRegistered__vanilla(
        user_id, "John", "Vanilliana", True, "FREE", datetime.now(), 9.2, EventEnvelope__vanilla()
    )
    event_at = UserRegistered__attrs(
        user_id, "John", "Attrivani", True, "LITE", datetime.now(), 7.2, EventEnvelope__attrs()
    )
    event_dc = UserRegistered__dataclass(
        user_id, "John", "Dataclassovsky", True, "FREE", datetime.now(), 1.0, EventEnvelope__dataclass()
    )
    event_pd = UserRegistered__pydantic(
        user_id=user_id,
        user_name="John",
        user_last_name="Pydanticola",
        is_new_user=True,
        subscription_type="PRO",
        registration_timestamp=datetime.now(),
        score=9.0,
        envelope=EventEnvelope__pydantic(),
    )

    print("Staring libraries speed comparison...\n") if verbose else None
    serde_event(avro_serializer, avro_deserializer, UserRegistered__attrs, event_van)  # Warm-up

    print(f"[VANILLA] Input event : {event_van}") if verbose else None
    start_time = time.time()
    for _ in range(test_runs):
        event_van = serde_event(avro_serializer, avro_deserializer, UserRegistered__vanilla, event_van)
    elapsed_time = time.time() - start_time
    print(f"[VANILLA] Execution time (total): {elapsed_time:.5f} seconds")
    print(f"[VANILLA] Execution time (per message): {(van_time := (elapsed_time / test_runs) * 1e6):.3f} microseconds")
    print(f"[VANILLA] Maximal throughput: {(van_msgs := int(1 / (elapsed_time / test_runs)))} messages/sec")
    print(f"[VANILLA] Output event: {event_van}\n") if verbose else print("\n")

    print(f"[ATTRS] Input event : {event_at}") if verbose else None
    start_time = time.time()
    for _ in range(test_runs):
        event_at = serde_event(avro_serializer, avro_deserializer, UserRegistered__attrs, event_at)
    elapsed_time = time.time() - start_time
    print(f"[ATTRS] Execution time (total): {elapsed_time:.5f} seconds")
    print(f"[ATTRS] Execution time (per message): {(attrs_time := (elapsed_time / test_runs) * 1e6):.3f} microseconds")
    print(f"[ATTRS] Maximal throughput: {(attrs_msgs := int(1 / (elapsed_time / test_runs)))} messages/sec")
    print(f"[ATTRS] Output event: {event_at}\n") if verbose else print("\n")

    print(f"[DATACLASS] Input event : {event_dc}") if verbose else None
    start_time = time.time()
    for _ in range(test_runs):
        event_dc = serde_event(avro_serializer, avro_deserializer, UserRegistered__dataclass, event_dc)
    elapsed_time = time.time() - start_time
    print(f"[DATACLASS] Execution time: {elapsed_time:.5f} seconds")
    print(f"[DATACLASS] Execution time (per message): {(dc_time := (elapsed_time / test_runs) * 1e6):.3f} microseconds")
    print(f"[DATACLASS] Maximal throughput: {(dc_msgs := int(1 / (elapsed_time / test_runs)))} messages/sec")
    print(f"[DATACLASS] Output event: {event_dc}\n") if verbose else print("\n")

    print(f"[PYDANTIC] Input event : {event_pd}") if verbose else None
    start_time = time.time()
    for _ in range(test_runs):
        event_pd = serde_event(avro_serializer, avro_deserializer, UserRegistered__pydantic, event_pd)
    elapsed_time = time.time() - start_time
    print(f"[PYDANTIC] Execution time: {elapsed_time:.5f} seconds")
    print(f"[PYDANTIC] Execution time (per message): {(pd_time := (elapsed_time / test_runs) * 1e6):.3f} microseconds")
    print(f"[PYDANTIC] Maximal throughput: {(pd_msgs := int(1 / (elapsed_time / test_runs)))} messages/sec")
    print(f"[PYDANTIC] Output event: {event_pd}\n") if verbose else print("\n")

    times = [van_time, attrs_time, dc_time, pd_time]
    messages = [van_msgs, attrs_msgs, dc_msgs, pd_msgs]
    if gen_chart:
        plot_serde_speed_chart(libraries, times, messages)


if __name__ == "__main__":
    args = serde_speed_argparse()
    local_schema = str(os.path.join(os.path.dirname(__file__), args.schema))
    check_speed(local_schema, args.test_runs, args.verbose, args.chart)

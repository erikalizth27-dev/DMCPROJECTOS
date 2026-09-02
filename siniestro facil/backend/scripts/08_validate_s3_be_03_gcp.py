from __future__ import annotations

import os
import time
from datetime import datetime, timezone
from uuid import uuid4

from google.api_core.exceptions import NotFound
from google.cloud import pubsub_v1, tasks_v2

from siniestro_facil.infrastructure.cloud_tasks_adapter import (
    CloudTasksRetryScheduler,
)
from siniestro_facil.infrastructure.pubsub_adapter import (
    GooglePubSubTransport,
    PubSubEnvelope,
)


PROJECT_ID = os.getenv(
    "GCP_PROJECT_ID",
    "project-77c17016-86bc-4fc4-a97",
)
MAIN_TOPIC = "siniestro-asistencia-solicitudes"
DLQ_TOPIC = "siniestro-asistencia-dead-letter"
QUEUE_ID = "siniestro-asistencia-reintentos"
LOCATION = "us-central1"


publisher = pubsub_v1.PublisherClient(
    publisher_options=pubsub_v1.types.PublisherOptions(
        enable_message_ordering=True
    )
)
subscriber = pubsub_v1.SubscriberClient()
tasks = tasks_v2.CloudTasksClient()
suffix = uuid4().hex[:12]
subscription_id = f"s3-be-03-validation-{suffix}"
event_id = str(uuid4())
task_id = f"s3-be-03-validation-{suffix}"
topic_path = publisher.topic_path(PROJECT_ID, MAIN_TOPIC)
subscription_path = subscriber.subscription_path(
    PROJECT_ID,
    subscription_id,
)
task_name: str | None = None
subscription_created = False

try:
    subscriber.create_subscription(
        request={
            "name": subscription_path,
            "topic": topic_path,
            "ack_deadline_seconds": 30,
            "expiration_policy": {"ttl": {"seconds": 86400}},
        }
    )
    subscription_created = True
    print(f"Suscripción temporal creada: {subscription_id}")

    envelope = PubSubEnvelope(
        event_id=event_id,
        event_type="asistencia.validacion_sintetica",
        ordering_key="asistencia:synthetic",
        occurred_at=datetime.now(timezone.utc),
        payload={
            "synthetic": True,
            "sprint": 3,
            "increment": "S3-BE-03",
        },
    )
    transport = GooglePubSubTransport(
        project_id=PROJECT_ID,
        topic_id=MAIN_TOPIC,
        dead_letter_topic_id=DLQ_TOPIC,
        client=publisher,
    )
    message_id = transport.publish(envelope)
    print(f"Mensaje Pub/Sub publicado: {message_id}")

    received = False
    deadline = time.monotonic() + 30
    while time.monotonic() < deadline and not received:
        response = subscriber.pull(
            request={
                "subscription": subscription_path,
                "max_messages": 10,
            },
            timeout=10,
        )
        ack_ids: list[str] = []
        for item in response.received_messages:
            attributes = dict(item.message.attributes)
            if attributes.get("event_id") == event_id:
                ack_ids.append(item.ack_id)
                received = True
        if ack_ids:
            subscriber.acknowledge(
                request={
                    "subscription": subscription_path,
                    "ack_ids": ack_ids,
                }
            )
        if not received:
            time.sleep(1)

    if not received:
        raise RuntimeError("No se recibió el mensaje sintético")
    print("Publicación y consumo Pub/Sub: OK")

    scheduler = CloudTasksRetryScheduler(
        project_id=PROJECT_ID,
        location=LOCATION,
        queue_id=QUEUE_ID,
        target_url=(
            "https://example.invalid/"
            "siniestro-facil/validacion-reintento"
        ),
        client=tasks,
    )
    task_name = scheduler.schedule(
        task_id=task_id,
        payload={"event_id": event_id, "synthetic": True},
        delay_seconds=300,
    )
    created = tasks.get_task(request={"name": task_name})
    if created.name != task_name:
        raise RuntimeError("Cloud Tasks devolvió una tarea inesperada")
    print(f"Tarea Cloud Tasks programada: {task_name}")
    print("Programación Cloud Tasks: OK")
finally:
    if task_name is not None:
        try:
            tasks.delete_task(request={"name": task_name})
            print("Tarea temporal eliminada: OK")
        except NotFound:
            pass
    if subscription_created:
        try:
            subscriber.delete_subscription(
                request={"subscription": subscription_path}
            )
            print("Suscripción temporal eliminada: OK")
        except NotFound:
            pass
    publisher.stop()
    subscriber.close()
    tasks.close()

print("LIMPIEZA GCP: OK")
print("VALIDACIÓN REAL S3-BE-03 COMPLETADA")

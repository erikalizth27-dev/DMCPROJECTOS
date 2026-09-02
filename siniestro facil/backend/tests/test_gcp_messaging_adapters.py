from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from siniestro_facil.application.publish_assistance_outbox import (
    PublishAssistanceOutbox,
)
from siniestro_facil.infrastructure.cloud_tasks_adapter import (
    CloudTasksRetryScheduler,
)
from siniestro_facil.infrastructure.pubsub_adapter import (
    GooglePubSubTransport,
    PubSubEnvelope,
)
from siniestro_facil.persistence.outbox_repository import OutboxRecord


class FakePublisher:
    def topic_path(self, project: str, topic: str) -> str:
        return f"projects/{project}/topics/{topic}"

    def publish(self, topic: str, data: bytes, **attributes: str) -> Mock:
        future = Mock()
        future.result.return_value = "message-123"
        self.last = (topic, data, attributes)
        return future


class FakeTasks:
    def queue_path(self, project: str, location: str, queue: str) -> str:
        return f"projects/{project}/locations/{location}/queues/{queue}"

    def task_path(
        self,
        project: str,
        location: str,
        queue: str,
        task: str,
    ) -> str:
        return f"{self.queue_path(project, location, queue)}/tasks/{task}"

    def create_task(self, *, request: dict[str, object]) -> object:
        self.request = request
        return SimpleNamespace(name=request["task"]["name"])


def envelope() -> PubSubEnvelope:
    return PubSubEnvelope(
        event_id="event-123",
        event_type="asistencia.reintento_solicitado",
        ordering_key="asistencia:41",
        occurred_at=datetime.now(timezone.utc),
        payload={"id_asistencia": 41},
    )


def test_google_pubsub_transport_publishes_canonical_envelope() -> None:
    client = FakePublisher()
    transport = GooglePubSubTransport(
        project_id="project-test",
        topic_id="main",
        dead_letter_topic_id="dead",
        client=client,
    )

    assert transport.publish(envelope()) == "message-123"
    assert client.last[0].endswith("/topics/main")
    assert client.last[2]["event_id"] == "event-123"
    assert client.last[2]["ordering_key"] == "asistencia:41"


def test_google_pubsub_transport_routes_dead_letter() -> None:
    client = FakePublisher()
    transport = GooglePubSubTransport(
        project_id="project-test",
        topic_id="main",
        dead_letter_topic_id="dead",
        client=client,
    )

    transport.dead_letter(envelope(), reason="tercer fallo")

    assert client.last[0].endswith("/topics/dead")
    assert client.last[2]["dead_letter_reason"] == "tercer fallo"


@pytest.mark.parametrize("delay", [30, 120, 300])
def test_cloud_tasks_uses_approved_delays(delay: int) -> None:
    client = FakeTasks()
    scheduler = CloudTasksRetryScheduler(
        project_id="project-test",
        location="us-central1",
        queue_id="retry",
        target_url="https://worker.example/retry",
        client=client,
    )

    name = scheduler.schedule(
        task_id=f"event-{delay}",
        payload={"delay": delay},
        delay_seconds=delay,
    )

    assert name.endswith(f"/tasks/event-{delay}")
    task = client.request["task"]
    assert task["dispatch_deadline"] == {"seconds": 15}


def test_cloud_tasks_rejects_unapproved_delay() -> None:
    scheduler = CloudTasksRetryScheduler(
        project_id="project-test",
        location="us-central1",
        queue_id="retry",
        target_url="https://worker.example/retry",
        client=FakeTasks(),
    )

    with pytest.raises(ValueError, match="S3-DEC-03"):
        scheduler.schedule(
            task_id="invalid",
            payload={},
            delay_seconds=60,
        )


def test_outbox_publisher_marks_success_and_failure() -> None:
    now = datetime.now(timezone.utc)
    records = (
        OutboxRecord(
            event_id="ok",
            aggregate_type="asistencia",
            aggregate_id=1,
            event_type="retry",
            payload={},
            attempts=1,
            occurred_at=now,
            available_at=now,
        ),
        OutboxRecord(
            event_id="fail",
            aggregate_type="asistencia",
            aggregate_id=2,
            event_type="retry",
            payload={},
            attempts=1,
            occurred_at=now,
            available_at=now,
        ),
    )
    repository = Mock()
    repository.claim_batch.return_value = records
    transport = Mock()
    transport.publish.side_effect = ["message-ok", RuntimeError("fallo")]

    result = PublishAssistanceOutbox(repository, transport).run()

    assert result.published == 1
    assert result.failed == 1
    repository.mark_published.assert_called_once_with("ok", "message-ok")
    repository.mark_failed.assert_called_once()

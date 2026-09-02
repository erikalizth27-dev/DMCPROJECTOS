from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from typing import Protocol


class CloudTasksClient(Protocol):
    def queue_path(
        self,
        project: str,
        location: str,
        queue: str,
    ) -> str: ...

    def task_path(
        self,
        project: str,
        location: str,
        queue: str,
        task: str,
    ) -> str: ...

    def create_task(self, *, request: dict[str, object]) -> object: ...


class CloudTasksRetryScheduler:
    def __init__(
        self,
        *,
        project_id: str,
        location: str,
        queue_id: str,
        target_url: str,
        service_account_email: str | None = None,
        client: CloudTasksClient | None = None,
    ) -> None:
        if client is None:
            from google.cloud import tasks_v2

            client = tasks_v2.CloudTasksClient()
        self._client = client
        self._project_id = project_id
        self._location = location
        self._queue_id = queue_id
        self._target_url = target_url
        self._service_account_email = service_account_email

    def schedule(
        self,
        *,
        task_id: str,
        payload: dict[str, object],
        delay_seconds: int,
    ) -> str:
        if delay_seconds not in {30, 120, 300}:
            raise ValueError("delay_seconds no pertenece a S3-DEC-03")
        normalized_task_id = task_id.strip()
        if not normalized_task_id:
            raise ValueError("task_id es obligatorio")

        parent = self._client.queue_path(
            self._project_id,
            self._location,
            self._queue_id,
        )
        task_name = self._client.task_path(
            self._project_id,
            self._location,
            self._queue_id,
            normalized_task_id,
        )
        request: dict[str, object] = {
            "http_method": 1,
            "url": self._target_url,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(
                payload,
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=False,
            ).encode("utf-8"),
        }
        if self._service_account_email:
            request["oidc_token"] = {
                "service_account_email": self._service_account_email
            }

        scheduled_at = datetime.now(timezone.utc) + timedelta(
            seconds=delay_seconds
        )
        task = {
            "name": task_name,
            "http_request": request,
            "schedule_time": scheduled_at,
            "dispatch_deadline": {"seconds": 10},
        }
        response = self._client.create_task(
            request={"parent": parent, "task": task}
        )
        return str(getattr(response, "name", task_name))

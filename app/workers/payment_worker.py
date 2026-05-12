"""
Temporal worker — registers activities and workflow, then polls the task queue.
Run with:  python -m workers.payment_worker
"""
from __future__ import annotations
import asyncio
from temporalio.client import Client
from temporalio.worker import Worker
from shared.config import get_settings
from shared.logger import setup_logging, get_logger
from workflows.payment_workflow import PaymentWorkflow
from workflows.activities import (
    collect_context,
    validate_policy,
    optimize_route,
    validate_layer4,
    execute_payment,
    update_layer4,
    record_feedback,
)

log = get_logger("workers.payment_worker")


async def main() -> None:
    setup_logging()
    settings = get_settings()

    client = await Client.connect(
        settings.temporal_host,
        namespace=settings.temporal_namespace,
    )

    worker = Worker(
        client,
        task_queue=settings.temporal_task_queue_payments,
        workflows=[PaymentWorkflow],
        activities=[
            collect_context,
            validate_policy,
            optimize_route,
            validate_layer4,
            execute_payment,
            update_layer4,
            record_feedback,
        ],
    )

    log.info(
        "worker.started",
        namespace=settings.temporal_namespace,
        task_queue=settings.temporal_task_queue_payments,
    )
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())

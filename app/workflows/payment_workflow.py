from __future__ import annotations
from datetime import timedelta
from temporalio import workflow
from temporalio.common import RetryPolicy

with workflow.unsafe.imports_passed_through():
    from workflows.activities import (
        collect_context,
        validate_policy,
        optimize_route,
        validate_layer4,
        execute_payment,
        update_layer4,
        record_feedback,
    )

_RETRY = RetryPolicy(maximum_attempts=3, initial_interval=timedelta(seconds=2))


@workflow.defn(name="PaymentWorkflow")
class PaymentWorkflow:
    """
    Temporal durable workflow for payment processing.
    Mirrors the LangGraph DAG but with retries, timeouts, and durability.
    """

    @workflow.run
    async def run(self, initial_state: dict) -> dict:
        state = initial_state

        state = await workflow.execute_activity(
            collect_context, state,
            start_to_close_timeout=timedelta(seconds=30),
            retry_policy=_RETRY,
        )

        state = await workflow.execute_activity(
            validate_policy, state,
            start_to_close_timeout=timedelta(seconds=30),
            retry_policy=_RETRY,
        )

        if state.get("compliance_status") != "APPROVED":
            return state

        state = await workflow.execute_activity(
            optimize_route, state,
            start_to_close_timeout=timedelta(seconds=30),
            retry_policy=_RETRY,
        )

        state = await workflow.execute_activity(
            validate_layer4, state,
            start_to_close_timeout=timedelta(seconds=30),
            retry_policy=_RETRY,
        )

        if state.get("layer4_validation_status") != "APPROVED":
            return state

        state = await workflow.execute_activity(
            execute_payment, state,
            start_to_close_timeout=timedelta(seconds=60),
            retry_policy=_RETRY,
        )

        state = await workflow.execute_activity(
            update_layer4, state,
            start_to_close_timeout=timedelta(seconds=30),
            retry_policy=_RETRY,
        )

        state = await workflow.execute_activity(
            record_feedback, state,
            start_to_close_timeout=timedelta(seconds=30),
            retry_policy=_RETRY,
        )

        return state

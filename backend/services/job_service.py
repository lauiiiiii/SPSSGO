# -*- coding: utf-8 -*-
"""Compatibility facade for job orchestration."""

from backend.services.jobs.control import (
    cancel_job_for_user,
    download_job_output,
    get_job_detail_for_user,
    list_active_jobs_for_session,
    list_sandbox_runs_for_user,
    retry_job_for_user,
    stream_job_events,
)
from backend.services.jobs.runner import run_job
from backend.services.jobs.submission import (
    stream_execute_plan_job_events,
    submit_ai_interpret_job,
    submit_ai_plan_job,
    submit_execute_method_job,
    submit_execute_plan_job,
    submit_generate_report_job,
    submit_process_job,
    submit_upload_job,
)

__all__ = [
    "cancel_job_for_user",
    "download_job_output",
    "get_job_detail_for_user",
    "list_active_jobs_for_session",
    "list_sandbox_runs_for_user",
    "retry_job_for_user",
    "run_job",
    "stream_execute_plan_job_events",
    "stream_job_events",
    "submit_ai_interpret_job",
    "submit_ai_plan_job",
    "submit_execute_method_job",
    "submit_execute_plan_job",
    "submit_generate_report_job",
    "submit_process_job",
    "submit_upload_job",
]

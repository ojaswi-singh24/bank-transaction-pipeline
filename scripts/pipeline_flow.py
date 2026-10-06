"""
pipeline_flow.py

Purpose: Orchestrate the full pipeline (extract -> dbt run -> dbt test)
as a single Prefect flow. This turns our manually-run steps into one
automated, trackable, failure-aware pipeline.

Run this from the project root folder with:
    python scripts/pipeline_flow.py
"""

import subprocess
import sys
from pathlib import Path

from prefect import flow, task

PROJECT_ROOT = Path(__file__).parent.parent
DBT_PROJECT_DIR = PROJECT_ROOT / "dbt_project" / "bank_pipeline"


@task
def extract_and_load_task():
    """Run our existing extract_load.py script as a subprocess."""
    print("Running extract_load.py ...")
    result = subprocess.run(
        [sys.executable, str(PROJECT_ROOT / "scripts" / "extract_load.py")],
        capture_output=True,
        text=True,
    )
    print(result.stdout)
    if result.returncode != 0:
        print(result.stderr)
        raise RuntimeError("extract_load.py failed")
    print("extract_load.py completed successfully.")


@task
def dbt_run_task():
    """Run 'dbt run' to build all models."""
    print("Running dbt run ...")
    result = subprocess.run(
        ["dbt", "run"],
        cwd=str(DBT_PROJECT_DIR),
        capture_output=True,
        text=True,
    )
    print(result.stdout)
    if result.returncode != 0:
        print(result.stderr)
        raise RuntimeError("dbt run failed")
    print("dbt run completed successfully.")


@task
def dbt_test_task():
    """Run 'dbt test' to validate all models."""
    print("Running dbt test ...")
    result = subprocess.run(
        ["dbt", "test"],
        cwd=str(DBT_PROJECT_DIR),
        capture_output=True,
        text=True,
    )
    print(result.stdout)
    if result.returncode != 0:
        print(result.stderr)
        raise RuntimeError("dbt test failed")
    print("dbt test completed successfully.")


@flow(name="bank_transaction_pipeline")
def run_pipeline():
    """The full pipeline: extract -> load -> transform -> test."""
    extract_and_load_task()
    dbt_run_task()
    dbt_test_task()
    print("Pipeline completed successfully end to end.")


if __name__ == "__main__":
    run_pipeline()
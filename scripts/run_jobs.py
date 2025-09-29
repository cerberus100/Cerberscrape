"""Scheduled job runner for DataForge."""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

from core.pipeline.business import run_business_pipeline
from core.pipeline.rfp import run_rfp_pipeline
from core.schemas import BusinessPullRequest, RFPPullRequest

logger = logging.getLogger(__name__)


def biz_daily_job():
    """Daily business data refresh job."""
    logger.info("Starting daily business data refresh")
    
    # Example configuration - customize as needed
    payload = BusinessPullRequest(
        states=["CA", "TX", "NY", "FL"],
        naics=["621111", "541511"],  # Healthcare and IT services
        limit=1000,
        enable_geocoder=True
    )
    
    try:
        result = run_business_pipeline(payload)
        logger.info(f"Daily business job completed: {result.message}")
    except Exception as exc:
        logger.error(f"Daily business job failed: {exc}")


def rfp_hourly_job():
    """Hourly RFP refresh job."""
    logger.info("Starting hourly RFP refresh")
    
    # Look for RFPs posted in the last hour
    since = datetime.utcnow() - timedelta(hours=1)
    
    payload = RFPPullRequest(
        states=["CA", "TX", "NY", "FL"],
        naics=["621111", "541511"],
        posted_from=since.date(),
        limit=500
    )
    
    try:
        result = run_rfp_pipeline(payload)
        logger.info(f"Hourly RFP job completed: {result.message}")
    except Exception as exc:
        logger.error(f"Hourly RFP job failed: {exc}")


def main():
    """Start the scheduler."""
    logging.basicConfig(level=logging.INFO)
    
    scheduler = BlockingScheduler()
    
    # Schedule jobs
    scheduler.add_job(
        biz_daily_job,
        CronTrigger(hour=2, minute=0),  # 2 AM daily
        id='biz_daily',
        name='Daily Business Data Refresh'
    )
    
    scheduler.add_job(
        rfp_hourly_job,
        CronTrigger(minute=0),  # Every hour
        id='rfp_hourly',
        name='Hourly RFP Refresh'
    )
    
    logger.info("DataForge scheduler started")
    try:
        scheduler.start()
    except KeyboardInterrupt:
        logger.info("Scheduler stopped")
        scheduler.shutdown()


if __name__ == "__main__":
    main()


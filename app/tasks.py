from apscheduler.schedulers.background import (
    BackgroundScheduler,  # runs tasks in the background
)
from apscheduler.triggers.interval import IntervalTrigger
from sqlmodel import Session

from . import utils
from .routers.auctions import process_finished_auctions


def process_finished_auctions_with_session():
    utils.pretty_print("task", "Fetching finished auctions...")
    with Session(utils.engine) as session:
        process_finished_auctions(session)
        session.commit()


# Set up the scheduler
scheduler = BackgroundScheduler()
# trigger = CronTrigger(hour=13, minute=32)  # run every day on 13:32
trigger_2 = IntervalTrigger(hours=6)  # run every 6 hours
scheduler.add_job(process_finished_auctions_with_session, trigger_2)

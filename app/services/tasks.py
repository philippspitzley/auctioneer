from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from sqlmodel import Session

from .. import db

from .. import utils
from ..routers.auctions import process_finished_auctions


def process_finished_auctions_with_session():
    utils.pretty_print("task", "Start Fetching finished auctions...")
    with Session(db.engine) as session:
        process_finished_auctions(session)
    utils.pretty_print("task", "End Fetching finished auctions...\n")


# Set up the scheduler
scheduler = BackgroundScheduler()
trigger = IntervalTrigger(minutes=15)
scheduler.add_job(process_finished_auctions_with_session, trigger)

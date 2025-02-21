from apscheduler.schedulers.background import BackgroundScheduler
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
trigger = IntervalTrigger(minutes=5)
scheduler.add_job(process_finished_auctions_with_session, trigger)


# def schedule_one_time_task(func, seconds_from_now: int = 1, **kwargs):
#     run_time = datetime.now(timezone.utc) + timedelta(seconds=seconds_from_now)

#     scheduler.add_job(
#         func,
#         kwargs=kwargs,
#         trigger="date",
#         run_date=run_time,
#         id=f"one_time_task_{run_time.timestamp()}",
#         replace_existing=True,  # Avoid duplicate jobs with same ID
#     )
#     print(f"Task {func.__name__} scheduled to run at {run_time}")

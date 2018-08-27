from WorkerSchedule import WorkerSchedule
from ScheduleAssignment import ScheduleAssignment


class Worker:
    def __init__(self, first_name, last_name, normal_hours=None, remaining_hours=None, jobs=None, prefered_bakery=None):
        self.first_name = first_name
        self.last_name = last_name
        self.normal_hours = normal_hours
        self.remaining_hours = remaining_hours
        self.jobs = jobs
        self.preferred_bakery = prefered_bakery
        self.schedule = WorkerSchedule()

    def add_task(self, assignment: ScheduleAssignment):
        self.schedule.add_task(assignment)
        self.remaining_hours -= assignment.end - assignment.start

from WorkerSchedule import WorkerSchedule
from ScheduleAssignment import ScheduleAssignment


class Worker:
    def __init__(self, first_name, last_name, normal_hours=None, remaining_hours=None, jobs=None, store=None, scheduled_time_off=None):
        self.first_name = first_name
        self.last_name = last_name
        self.normal_hours = normal_hours
        self.remaining_hours = remaining_hours
        self.overtime_counter = remaining_hours - normal_hours
        self.jobs = jobs
        self.store = store
        self.schedule = WorkerSchedule()
        self.scheduled_time_off = scheduled_time_off

    def add_task(self, assignment: ScheduleAssignment):
        self.schedule.add_task(assignment)
        self.remaining_hours -= assignment.end - assignment.start

    def remove_task(self, assignment: ScheduleAssignment):
        self.schedule.remove_task(assignment)
        self.remaining_hours += assignment.end - assignment.start

    def has_24_hr_rest(self):
        return self.schedule.has_24_hr_gap()

    def get_11_hr_gap_count(self):
        return self.schedule.get_11_hr_gap_count()

    def get_3_hr_gap_count(self):
        return self.schedule.get_3_hr_gap_count()

    def get_hours_count(self, days):
        return self.schedule.get_hours_count(days)

    def get_hours_over_8_count(self):
        return self.schedule.get_hours_over_8_count()

    def get_overtime(self):
        # can be negative
        return self.get_hours_count(['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']) - self.normal_hours

    def works_different_shops_same_day(self):
        return self.schedule.works_different_shops_same_day()

    def get_tasks_overlap_count(self):
        return self.schedule.get_tasks_overlap_count()

    def get_scheduled_time_off_error_count(self):
        return self.schedule.get_scheduled_time_off_error_count(self.scheduled_time_off)

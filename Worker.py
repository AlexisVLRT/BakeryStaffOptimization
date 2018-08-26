from WorkerSchedule import WorkerSchedule


class Worker:
    def __init__(self, first_name, last_name, normal_hours=None, remaining_hours=None, jobs=None, prefered_bakery=None):
        self.first_name = first_name
        self.last_name = last_name
        self.normal_hours = normal_hours
        self.remaining_hours = remaining_hours
        self.jobs = jobs
        self.preferred_bakery = prefered_bakery
        self.schedule = WorkerSchedule()

    def add_task(self, job, day, start, end):
        self.schedule.add_task(job, day, start, end)
        self.remaining_hours -= end - start
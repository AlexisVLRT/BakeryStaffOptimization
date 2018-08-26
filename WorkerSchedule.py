class WorkerSchedule:
    def __init__(self):
        self._schedule = {
            "mon": [],
            "tue": [],
            "wed": [],
            "thu": [],
            "fri": [],
            "sat": [],
            "sun": [],
        }

    def add_task(self, job, day, start, end):
        self._schedule[day].append([job, start, end])

    def is_busy(self, day, start, end):
        busy = False
        for task in self._schedule[day]:
            if task[1] < start < task[2] or task[1] < end < task[2] or start < task[1] < end or start < task[2] < end:
                busy = True
        return busy

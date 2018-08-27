from ScheduleAssignment import ScheduleAssignment


class WorkerSchedule:
    def __init__(self):
        self._schedule = []

    def add_task(self, assignment: ScheduleAssignment):
        self._schedule.append(assignment)

    def is_busy(self, day, start, end):
        busy = False
        for task in self._schedule:
            if task.day == day and (task.start < start < task.end or task.start < end < task.end or start < task.start < end or start < task.end < end):
                busy = True
        return busy

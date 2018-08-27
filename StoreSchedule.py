from ScheduleAssignment import ScheduleAssignment


class StoreSchedule:
    def __init__(self):
        self.schedule = {
            "mon": [],
            "tue": [],
            "wed": [],
            "thu": [],
            "fri": [],
            "sat": [],
            "sun": [],
        }

    def assign(self, assignment: ScheduleAssignment):
        self.schedule[assignment.day].append(assignment)
        assignment.worker.add_task(assignment)

    def get_fitness(self):
        return 0

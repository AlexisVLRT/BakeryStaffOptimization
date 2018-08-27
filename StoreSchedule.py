from ScheduleAssignment import ScheduleAssignment
from Constants import Constants


class StoreSchedule:
    def __init__(self):
        self.schedule = []

    def assign(self, assignment: ScheduleAssignment):
        self.schedule.append(assignment)
        assignment.worker.add_task(assignment)

    def get_assignments_day(self, day):
        return [assignment for assignment in self.schedule if assignment.day == day]

    def mutate(self):
        mutation_rate = Constants.mutation_rate

    def get_fitness(self):
        return 0

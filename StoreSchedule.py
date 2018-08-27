from ScheduleAssignment import ScheduleAssignment
from Constants import Constants
import random
from typing import List
from Workforce import Workforce


class StoreSchedule:
    def __init__(self):
        self.schedule = []  # type: List[ScheduleAssignment]
        self.visualizer_col_number = None

    def assign(self, assignment: ScheduleAssignment):
        self.schedule.append(assignment)
        assignment.worker.add_task(assignment)

    def get_assignments_day(self, day):
        return [assignment for assignment in self.schedule if assignment.day == day]

    def mutate(self, workforce: Workforce):
        mutation_rate = Constants().mutation_rate
        print(mutation_rate, len(self.schedule))
        mutations = ['extend', 'reduce', 'split', 'merge', 'swap workers', 'change worker']
        mutations = ['split']

        for assignment in self.schedule:
            if mutation_rate >= random.random():
                mutation = mutations[random.randint(0, len(mutations)-1)]
                print(mutation)

                if mutation == 'extend':
                    # an assignment starts earlier or ends later, 15 minutes.
                    if random.randint(0, 1):
                        assignment.end += 0.25
                    else:
                        assignment.start -= 0.25

                elif mutation == 'reduce':
                    # an assignment starts later or ends earlier, 15 minutes..
                    if random.randint(0, 1):
                        assignment.start += 0.25
                    else:
                        assignment.end -= 0.25

                elif mutation == 'split':
                    # an assignment is split in 2 down the middle
                    second_half = ScheduleAssignment(
                        assignment.worker,
                        assignment.job,
                        assignment.day,
                        assignment.start + (assignment.end - assignment.start) / 2,
                        assignment.end,
                        assignment.visualizer_id
                    )
                    self.schedule.append(second_half)
                    assignment.end = assignment.start + (assignment.end - assignment.start) / 2

                elif mutation == 'merge':
                    # Two assignments are merged together.
                    # The day, job, and worker must be the sames
                    # One has to be directly after the other
                    # Otherwise no mutation happens
                    for second_assignment in self.schedule:
                        if second_assignment != assignment and second_assignment.day == assignment.day and second_assignment.worker == assignment.worker:
                            if second_assignment.start == assignment.end:
                                assignment.end = second_assignment.end
                            elif second_assignment.end == assignment.start:
                                assignment.start = second_assignment.start
                            del self.schedule[self.schedule.index(second_assignment)]
                            break

                elif mutation == 'swap workers':
                    # two assignments swap workers
                    second_assignment = self.schedule[random.randint(0, len(self.schedule)-1)]
                    second_assignment.worker, assignment.worker = assignment.worker, second_assignment.worker

                elif mutation == 'change worker':
                    # an assignment changes worker
                    assignment.worker = workforce.workers[random.randint(0, len(workforce.workers)-1)]

    def get_fitness(self):
        return 0

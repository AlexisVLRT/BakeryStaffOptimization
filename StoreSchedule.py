from ScheduleAssignment import ScheduleAssignment
from Constants import Constants
import random
from typing import List
from Workforce import Workforce
from copy import deepcopy
from Constants import Constants


class StoreSchedule:
    def __init__(self):
        self.desired_schedule = []  # type: List[ScheduleAssignment]
        self.schedule = []  # type: List[ScheduleAssignment]
        self.visualizer_col_number = None
        self.constants = Constants()

    def assign(self, assignment: ScheduleAssignment):
        self.schedule.append(assignment)
        assignment.worker.add_task(assignment)

    def get_assignments_day(self, day):
        return [assignment for assignment in self.schedule if assignment.day == day]

    def get_job_scheduling_errors(self):
        """
        works out the number of unassigned necessary hours, unassigned recommended hours, and over assigned hours for the week
        :return:
        """
        days = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']
        repr = {day: {} for day in days}
        for assignment in self.schedule:
            assignment_as_minutes = [int(assignment.end * 60 >= minute > assignment.start * 60) for minute in range(1440)]
            if assignment.job in repr[assignment.day].keys():
                repr[assignment.day][assignment.job] = [assignment_as_minutes[minute] + repr[assignment.day][assignment.job][minute] for minute in range(1440)]
            else:
                repr[assignment.day][assignment.job] = assignment_as_minutes

        repr_desired = {day: {'necessary': {}, 'recommended': {}} for day in days}
        for assignment in self.desired_schedule:
            assignment_as_minutes = [int(assignment.end * 60 >= minute > assignment.start * 60) for minute in range(1440)]
            if assignment.job in repr_desired[assignment.day][assignment.importance].keys():
                repr_desired[assignment.day][assignment.importance][assignment.job] = [assignment_as_minutes[minute] + repr_desired[assignment.day][assignment.importance][assignment.job][minute] for minute in range(1440)]
            else:
                repr_desired[assignment.day][assignment.importance][assignment.job] = assignment_as_minutes

        necessary_hours_not_filled = 0
        recommended_hours_not_filled = 0
        overfilled = 0
        for day, staffing in repr.items():
            for job_name, scheduling in staffing.items():
                necessary_hours_not_filled -= sum([min(0, repr[day][job_name][minute] - (repr_desired[day]['necessary'][job_name][minute] if job_name in repr_desired[day]['necessary'].keys() else 0)) for minute in range(1440)])
                recommended_hours_not_filled -= sum([min(0, repr[day][job_name][minute] - (repr_desired[day]['necessary'][job_name][minute] if job_name in repr_desired[day]['necessary'].keys() else 0) - (repr_desired[day]['recommended'][job_name][minute] if job_name in repr_desired[day]['recommended'].keys() else 0)) for minute in range(1440)])
                overfilled += sum([max(0, repr[day][job_name][minute] - (repr_desired[day]['necessary'][job_name][minute] if job_name in repr_desired[day]['necessary'].keys() else 0) - (repr_desired[day]['recommended'][job_name][minute] if job_name in repr_desired[day]['recommended'].keys() else 0)) for minute in range(1440)])
        return necessary_hours_not_filled / 60, recommended_hours_not_filled / 60, overfilled / 60

    def mutate(self, workforce: Workforce):
        mutation_rate = Constants().mutation_rate
        print(mutation_rate, len(self.schedule))
        mutations = ['extend', 'reduce', 'split', 'merge', 'swap workers', 'change worker']

        for assignment in self.schedule:
            if mutation_rate >= random.random():
                mutation = mutations[random.randint(0, len(mutations)-1)]
                # print(mutation)

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
                        assignment.store,
                        assignment.job,
                        assignment.day,
                        assignment.start + (assignment.end - assignment.start) / 2,
                        assignment.end,
                        assignment.visualizer_id
                    )
                    self.schedule.append(second_half)
                    second_half.worker.add_task(second_half)
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
                            second_assignment.worker.remove_task(second_assignment)
                            del self.schedule[self.schedule.index(second_assignment)]
                            break

                elif mutation == 'swap workers':
                    # two assignments swap workers
                    second_assignment = self.schedule[random.randint(0, len(self.schedule)-1)]

                    assignment.worker.add_task(second_assignment)
                    assignment.worker.remove_task(assignment)
                    second_assignment.worker.add_task(assignment)
                    second_assignment.worker.remove_task(second_assignment)
                    second_assignment.worker, assignment.worker = assignment.worker, second_assignment.worker

                elif mutation == 'change worker':
                    # an assignment changes worker
                    new_worker = workforce.workers[random.randint(0, len(workforce.workers)-1)]
                    assignment.worker.remove_task(assignment)
                    assignment.worker = new_worker
                    assignment.worker.add_task(assignment)

    def get_fitness(self, workforce: Workforce):
        score = 0
        warnings = []

        # A worker has to work a task he is qualified for
        for assignment in self.schedule:
            if assignment.job not in assignment.worker.jobs:
                score -= self.constants.unqualified
                warnings.append('{} {} est assigné au poste {} {} à {}h, mais n\'en possède pas la compétence'.format(assignment.worker.first_name, assignment.worker.last_name, assignment.job, assignment.day, assignment.start))

        # A least 24 consecutive hours unscheduled per week
        for worker in workforce.workers:
            if not worker.has_24_hr_rest():
                score -= self.constants.weekly_rest
                warnings.append('{} {} n\'a pas 24h de repos consécutif dans la semaine'.format(worker.first_name, worker.last_name))

        # A worker can not be scheduled in 2 different tasks at the same time
        for worker in workforce.workers:
            overlap_count = worker.get_tasks_overlap_count()
            if overlap_count:
                warnings.append('{} {} est assigné à deux postes en même temps'.format(worker.first_name, worker.last_name))
            score -= self.constants.task_overlap * overlap_count

        # A shop must at least have the minimal required personnel
        # A shop must have the recommended personnel
        necessary_hours_not_filled, recommended_hours_not_filled, overfilled = self.get_job_scheduling_errors()
        if necessary_hours_not_filled:
            warnings.append('{}h nécessaires non assignés'.format(necessary_hours_not_filled))
        score -= necessary_hours_not_filled * self.constants.necessary_hours

        if recommended_hours_not_filled:
            warnings.append('{}h recommendées non assignés'.format(recommended_hours_not_filled))
        score -= recommended_hours_not_filled * self.constants.recommended_hours

        if overfilled:
            warnings.append('{}h sur-assignés'.format(overfilled))
        score -= overfilled * self.constants.overfilling

        # A worker's scheduled days off must be respected
        for worker in workforce.workers:
            errors = worker.get_scheduled_time_off_error_count()
            if errors:
                warnings.append('{} {} est assigné pendant son congé {} fois'.format(worker.first_name, worker.last_name, errors))
            score -= errors * self.constants.scheduled_on_time_off

        # A worker can not have more than 3h of downtime between assignments
        for worker in workforce.workers:
            errors = worker.get_3_hr_gap_count()
            if errors:
                warnings.append('{} {} a {} trous de plus de 3h dans son emploi du temps'.format(worker.first_name, worker.last_name, errors))
            score -= errors * self.constants.day_gap

        # At least 11 consecutive hours unscheduled per day
        for worker in workforce.workers:
            # TODO warning
            print(worker.get_11_hr_gap_count())
            score += worker.get_11_hr_gap_count() * self.constants.daily_rest

        # A worker should be scheduled in their store in priority
        for assignment in self.schedule:
            if assignment.store != assignment.worker.store:
                score -= self.constants.wrong_store
                warnings.append('{} {} est assigné au magasin {} qui n\'est pas son magasin prioritaire ({}) {} à {}h'.format(assignment.worker.first_name, assignment.worker.last_name, assignment.store, assignment.worker.store, assignment.day, assignment.start))

        # No more than 46 weekly hours
        for worker in workforce.workers:
            hour_count = worker.get_hours_count(['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun'])
            if hour_count > 46:
                score -= (46 - hour_count) * self.constants.above_46
                warnings.append('{} {} travaille plus de 46h (hebdomadaire)'.format(worker.first_name, worker.last_name))

        # No more than 42 hours from mon to fri
        for worker in workforce.workers:
            hour_count = worker.get_hours_count(['mon', 'tue', 'wed', 'thu', 'fri'])
            if hour_count > 42:
                score -= (42 - hour_count) * self.constants.above_42
                warnings.append('{} {} travaille plus de 42h entre lundi et vendredi'.format(worker.first_name, worker.last_name))

        # Least possible overtime
        for worker in workforce.workers:
            if not worker.overtime_counter:
                # No past overtime to catch up to
                overtime = worker.get_overtime()
                if overtime:
                    warnings.append('{} {} réalise {}h supplémentaires'.format(worker.first_name, worker.last_name, overtime))
                score -= abs(overtime) * self.constants.overtime
            else:
                # Past overtime is to be caught up to at a rate of 15% of the normal hours per week
                if worker.overtime_counter and worker.get_overtime():
                    warnings.append('{} {} avait {}h supplémentaires, et en effectue {}h'.format(worker.first_name, worker.last_name, worker.overtime_counter, worker.get_overtime()))
                score += worker.get_overtime() * self.constants.overtime_dec
                score -= (worker.get_overtime() - worker.overtime_counter) * self.constants.overtime
                score -= max(0, worker.get_overtime() - 0.15*worker.normal_hours) * self.constants.too_much_overtime_dec

        # No multi-site scheduling on the same day
        for worker in workforce.workers:
            occurrences, insufficient_commute_time = worker.works_different_shops_same_day()
            if occurrences:
                warnings.append('{} {} est affecté {} fois sur des sites différents, {} fois avec un temps insuffisant de trajet'.format(worker.first_name, worker.last_name, occurrences, insufficient_commute_time))
            score -= occurrences * self.constants.multiple_shops
            score -= insufficient_commute_time * self.constants.commuting

        return score, warnings

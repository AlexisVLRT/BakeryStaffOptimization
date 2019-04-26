from ScheduleAssignment import ScheduleAssignment
import random
from typing import List
from Worker import Worker
from Workforce import Workforce
from Constants import Constants


class StoreSchedule:
    """
    A Store's schedule.
    This is what we are trying to optimize, so a StoreSchedule instance is an individual of the population.
    """
    def __init__(self, input_data, visualizer_col_number=None):
        self.input_data = input_data
        self.desired_schedule = []  # type: List[ScheduleAssignment]
        self.schedule = []  # type: List[ScheduleAssignment]

        self.workforce = Workforce()
        for worker in self.input_data['workers']:
            self.workforce.add_worker(
                Worker(self.input_data['workers'].index(worker),
                       worker['first name'],
                       worker['last name'],
                       worker['normal hours'],
                       worker['hours left'],
                       worker['jobs'],
                       worker['store'],
                       worker['rest'])
            )

        self.visualizer_col_number = visualizer_col_number
        self.constants = Constants()
        self.fitness = None
        self.warnings = None

    def json_repr(self):
        """
        Generates a dict (basically a json) representation of the StoreSchedule. It contains all the assignments, the score of the schedule and all the warnings about broken rules
        :return: dict
        """
        score, warnings = self.get_fitness()
        schedule = {
            'Score': score,
            'Assignments': [assignment.json_repr() for assignment in self.schedule],
            'Warnings': warnings
        }
        return schedule

    def assign(self, assignment: ScheduleAssignment):
        """
        Assigns a task and a worker
        :param assignment: a ScheduleAssignment object
        :return:
        """
        self.schedule.append(assignment)
        assignment.worker.add_task(assignment)

    def get_assignments_day(self, day):
        """
        Returns the assignments on the schedule for the day
        :param day: day of the week
        :return: a list of ScheduleAssignment objects
        """
        return [assignment for assignment in self.schedule if assignment.day == day]

    def get_job_scheduling_errors(self):
        """
        Works out the number of unassigned necessary hours, unassigned recommended hours, and over assigned hours for the week
        This is the most expensive function. Finding a way to optimize it would greatly improve performance
        :return: necessary hours not filled, recommended hours not filled, overfilled
        """
        days = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']
        repr = {day: {} for day in days}

        # Using 12 min blocks for performance increase
        for assignment in self.schedule:
            assignment_as_minutes = [int(assignment.end * 12 >= minutes > assignment.start * 12) for minutes in range(288)]
            if assignment.job in repr[assignment.day].keys():
                repr[assignment.day][assignment.job] = [assignment_as_minutes[minutes] + repr[assignment.day][assignment.job][minutes] for minutes in range(288)]
            else:
                repr[assignment.day][assignment.job] = assignment_as_minutes

        repr_desired = {day: {'necessary': {}, 'recommended': {}} for day in days}
        for assignment in self.desired_schedule:
            assignment_as_minutes = [int(assignment.end * 12 >= minutes > assignment.start * 12) for minutes in range(288)]
            if assignment.job in repr_desired[assignment.day][assignment.importance].keys():
                repr_desired[assignment.day][assignment.importance][assignment.job] = [assignment_as_minutes[minute] + repr_desired[assignment.day][assignment.importance][assignment.job][minute] for minute in range(288)]
            else:
                repr_desired[assignment.day][assignment.importance][assignment.job] = assignment_as_minutes

        necessary_hours_not_filled = 0
        recommended_hours_not_filled = 0
        overfilled = 0
        for day, staffing in repr.items():
            for job_name, scheduling in staffing.items():
                necessary_hours_not_filled -= sum([min(0, repr[day][job_name][minute] - (repr_desired[day]['necessary'][job_name][minute] if job_name in repr_desired[day]['necessary'].keys() else 0)) for minute in range(288)])
                recommended_hours_not_filled -= sum([min(0, repr[day][job_name][minute] - (repr_desired[day]['necessary'][job_name][minute] if job_name in repr_desired[day]['necessary'].keys() else 0) - (repr_desired[day]['recommended'][job_name][minute] if job_name in repr_desired[day]['recommended'].keys() else 0)) for minute in range(288)])
                overfilled += sum([max(0, repr[day][job_name][minute] - (repr_desired[day]['necessary'][job_name][minute] if job_name in repr_desired[day]['necessary'].keys() else 0) - (repr_desired[day]['recommended'][job_name][minute] if job_name in repr_desired[day]['recommended'].keys() else 0)) for minute in range(288)])
        return necessary_hours_not_filled / 12, recommended_hours_not_filled / 12, overfilled / 12

    def mutate(self, rate=None):
        """
        The mutation method. Different types of mutations are implemented
        :param rate: probability that an assignment is mutated
        :return:
        """
        mutations = ['extend', 'reduce', 'split', 'merge', 'swap workers', 'change worker']
        mutation_rate = rate if rate is not None else self.constants.mutation_rate

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
                    self.assign(second_half)
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
                                second_assignment.worker.remove_task(second_assignment)
                                self.schedule.remove(second_assignment)
                            elif second_assignment.end == assignment.start:
                                assignment.start = second_assignment.start
                                second_assignment.worker.remove_task(second_assignment)
                                self.schedule.remove(second_assignment)
                            break

                elif mutation == 'swap workers':
                    # two assignments swap workers
                    second_assignment = self.schedule[random.randint(0, len(self.schedule)-1)]
                    if assignment != second_assignment:
                        assignment.worker.add_task(second_assignment)
                        assignment.worker.remove_task(assignment)
                        second_assignment.worker.add_task(assignment)
                        second_assignment.worker.remove_task(second_assignment)
                        second_assignment.worker, assignment.worker = assignment.worker, second_assignment.worker

                elif mutation == 'change worker':
                    # an assignment changes worker
                    new_worker = self.workforce.workers[random.randint(0, len(self.workforce.workers)-1)]
                    assignment.worker.remove_task(assignment)
                    assignment.worker = new_worker
                    assignment.worker.add_task(assignment)

    def mate(self, second_schedule: "StoreSchedule"):
        """
        Fuses two schedules to create two more
        :param second_schedule: the second parent
        :return: 2 'child' StoreSchedule objects
        """
        days = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']
        days_to_swap = [random.randint(0, 1) for _ in range(7)]
        child1, child2 = StoreSchedule(self.input_data, self.visualizer_col_number), StoreSchedule(self.input_data, self.visualizer_col_number)

        for day in days:
            assignments_1 = [assignment.json_repr() for assignment in self.get_assignments_day(day)]
            assignments_1 = [ScheduleAssignment(self.workforce.get_worker_by_id(assignment_json['Worker']['Id']), assignment_json['Store'], assignment_json['JobName'], assignment_json['WeekDay'], assignment_json['StartTime'], assignment_json['EndTime'], assignment_json['VizualizerId'], assignment_json['Importance']) for assignment_json in assignments_1]
            assignments_2 = [assignment.json_repr() for assignment in second_schedule.get_assignments_day(day)]
            assignments_2 = [ScheduleAssignment(self.workforce.get_worker_by_id(assignment_json['Worker']['Id']), assignment_json['Store'], assignment_json['JobName'], assignment_json['WeekDay'], assignment_json['StartTime'], assignment_json['EndTime'], assignment_json['VizualizerId'], assignment_json['Importance']) for assignment_json in assignments_2]

            if days_to_swap[days.index(day)]:
                for assignment in assignments_1:
                    assignment.worker = child1.workforce.get_worker_by_id(assignment.worker.worker_id)
                    child1.assign(assignment)
                for assignment in assignments_2:
                    assignment.worker = child2.workforce.get_worker_by_id(assignment.worker.worker_id)
                    child2.assign(assignment)
            else:
                for assignment in assignments_1:
                    assignment.worker = child1.workforce.get_worker_by_id(assignment.worker.worker_id)
                    child2.assign(assignment)
                for assignment in assignments_2:
                    assignment.worker = child2.workforce.get_worker_by_id(assignment.worker.worker_id)
                    child1.assign(assignment)
        return child1, child2

    def get_fitness(self):
        """
        Fitness function calculator. The calculation is worked out according to the client's specifications and rules
        The weights of each rules are set in the config file
        :return: the fitness score of the individual
        """
        score = 0
        warnings = []

        # A worker has to work a task he is qualified for
        for assignment in self.schedule:
            if assignment.job not in assignment.worker.jobs:
                score -= self.constants.unqualified
                warnings.append('{} {} est assigné au poste {} {} à {}h, mais n\'en possède pas la compétence'.format(assignment.worker.first_name, assignment.worker.last_name, assignment.job, assignment.day, assignment.start))

        # A least 24 consecutive hours unscheduled per week
        for worker in self.workforce.workers:
            if not worker.has_24_hr_rest():
                score -= self.constants.weekly_rest
                warnings.append('{} {} n\'a pas 24h de repos consécutif dans la semaine'.format(worker.first_name, worker.last_name))

        # A worker can not be scheduled in 2 different tasks at the same time
        for worker in self.workforce.workers:
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
        for worker in self.workforce.workers:
            errors = worker.get_scheduled_time_off_error_count()
            if errors:
                warnings.append('{} {} est assigné pendant son congé {} fois'.format(worker.first_name, worker.last_name, errors))
            score -= errors * self.constants.scheduled_on_time_off

        # A worker can not have more than 3h of downtime between assignments
        for worker in self.workforce.workers:
            errors = worker.get_3_hr_gap_count()
            if errors:
                warnings.append('{} {} a {} trous de plus de 3h dans son emploi du temps'.format(worker.first_name, worker.last_name, errors))
            score -= errors * self.constants.day_gap

        # Max 8 hours scheduled daily
        for worker in self.workforce.workers:
            hours_over = worker.get_hours_over_8_count()
            if hours_over:
                warnings.append('{} {} Cumule {} heures au delas des 8 journalières sur la semaine'.format(worker.first_name, worker.last_name, hours_over))
            score -= max(0, hours_over) * self.constants.more_8_daily_hours

        # At least 11 consecutive hours unscheduled per day
        for worker in self.workforce.workers:
            # TODO warning
            score += worker.get_11_hr_gap_count() * self.constants.daily_rest

        # A worker should be scheduled in their store in priority
        for assignment in self.schedule:
            if assignment.store != assignment.worker.store:
                score -= self.constants.wrong_store
                warnings.append('{} {} est assigné au magasin {} qui n\'est pas son magasin prioritaire ({}) {} à {}h'.format(assignment.worker.first_name, assignment.worker.last_name, assignment.store, assignment.worker.store, assignment.day, assignment.start))

        # No more than 46 weekly hours
        for worker in self.workforce.workers:
            hour_count = worker.get_hours_count(['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun'])
            if hour_count > 46:
                score -= (46 - hour_count) * self.constants.above_46
                warnings.append('{} {} travaille plus de 46h (hebdomadaire)'.format(worker.first_name, worker.last_name))

        # No more than 42 hours from mon to fri
        for worker in self.workforce.workers:
            hour_count = worker.get_hours_count(['mon', 'tue', 'wed', 'thu', 'fri'])
            if hour_count > 42:
                score -= (42 - hour_count) * self.constants.above_42
                warnings.append('{} {} travaille plus de 42h entre lundi et vendredi'.format(worker.first_name, worker.last_name))

        # Least possible overtime
        for worker in self.workforce.workers:
            if not worker.overtime_counter:
                # No past overtime to catch up to
                overtime = worker.get_overtime()
                if overtime:
                    warnings.append('{} {} réalise {}h supplémentaires'.format(worker.first_name, worker.last_name, round(overtime, 2)))
                score -= abs(overtime) * self.constants.overtime
            else:
                # Past overtime is to be caught up to at a rate of 15% of the normal hours per week
                if worker.overtime_counter and worker.get_overtime():
                    warnings.append('{} {} avait {}h supplémentaires, et en effectue {}h'.format(worker.first_name, worker.last_name, round(worker.overtime_counter), round(worker.get_overtime(), 2)))
                score += worker.get_overtime() * self.constants.overtime_dec
                score -= (worker.get_overtime() - worker.overtime_counter) * self.constants.overtime
                score -= max(0, worker.get_overtime() - 0.15*worker.normal_hours) * self.constants.too_much_overtime_dec

        # No multi-site scheduling on the same day
        for worker in self.workforce.workers:
            occurrences, insufficient_commute_time = worker.works_different_shops_same_day()
            if occurrences:
                warnings.append('{} {} est affecté {} fois sur des sites différents, {} fois avec un temps insuffisant de trajet'.format(worker.first_name, worker.last_name, occurrences, insufficient_commute_time))
            score -= occurrences * self.constants.multiple_shops
            score -= insufficient_commute_time * self.constants.commuting

        self.fitness = score
        self.warnings = warnings
        return score, warnings
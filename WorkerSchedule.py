from ScheduleAssignment import ScheduleAssignment
from typing import List
from Constants import Constants


class WorkerSchedule:
    """
    Defines the schedule of the worker
    """
    def __init__(self):
        self._schedule = []  # type: List[ScheduleAssignment]

    def add_task(self, assignment: ScheduleAssignment):
        self._schedule.append(assignment)

    def remove_task(self, assignment: ScheduleAssignment):
        del self._schedule[self._schedule.index(assignment)]

    def is_busy(self, day, start, end):
        """
        Whether or not a worker is busy at a certain time of the day
        :param day: weekday
        :param start: hour of start
        :param end: hour of finishing
        :return: True if the worker is already doing something that day between start and end, false otherwise
        """
        busy = False
        for task in self._schedule:
            if task.day == day and (task.start < start < task.end or task.start < end < task.end or start < task.start < end or start < task.end < end):
                busy = True
        return busy

    def get_day_ending_hour(self, day):
        """
        Returns the time at which the last assignment finishes
        :param day: weekday
        :return: hour (float)
        """
        ending_hour = -1
        for assignment in self._schedule:
            if assignment.day == day and assignment.end > ending_hour:
                ending_hour = assignment.end
        return ending_hour

    def get_day_starting_hour(self, day):
        """
        Returns the time at which the fisrt assignment starts
        :param day: weekday
        :return: hour (float)
        """
        starting_hour = 25
        for assignment in self._schedule:
            if assignment.day == day and assignment.start < starting_hour:
                starting_hour = assignment.start
        return starting_hour

    def has_24_hr_gap(self):
        """
        Whether or not a worker has a day off
        :return: Boolean
        """
        days_worked = set([])
        for assignment in self._schedule:
            days_worked.add(assignment.day)

        if len(days_worked) == 7:
            return False
        return True

    def get_11_hr_gap_count(self):
        """
        Counts the number of 11 hours gaps between the worker's assignments. (a good night of sleep)
        :return: number of times in the week it happens
        """
        n_gaps = 0
        days = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']
        for i in range(1, len(days)):
            if (24 - self.get_day_ending_hour(days[i-1]) + self.get_day_starting_hour(days[i])) >= 11:
                n_gaps += 1
        return n_gaps

    def get_3_hr_gap_count(self):
        """
        Counts the number of 3 hours gaps between the worker's assignments. (A break that is too long)
        :return: number of times in the week it happens
        """
        n_gaps = 0
        for day in ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']:
            day_assignments = [assignment for assignment in self._schedule if assignment.day == day]
            day_assignments.sort(key=lambda assignment: assignment.start)

            for i in range(len(day_assignments) - 1):
                if day_assignments[i + 1].start - day_assignments[i].end > 3:
                    n_gaps += 1
        return n_gaps

    def get_hours_over_8_count(self):
        """
        For each day, count the number of hours worked above 8 hours. Sum that over the week
        :return: number of overworked hours in the week
        """
        count = 0
        for day in ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']:
            day_count = 0
            for assignment in self._schedule:
                if assignment.day == day:
                    day_count += assignment.end - assignment.start
            count += max(0, day_count - 8)
        return count

    def get_hours_count(self, days):
        """
        Total hours worked in the week
        :param days:
        :return:
        """
        hours_count = 0
        for assignment in self._schedule:
            if assignment.day in days:
                hours_count += assignment.end - assignment.start
        return hours_count

    def works_different_shops_same_day(self):
        """
        Whether of not a worker is assigned to different shops the same day
        :return: Boolean
        """
        occurrences = 0
        insufficient_commute_time = 0
        for day in ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']:
            day_assignments = [assignment for assignment in self._schedule if assignment.day == day]
            day_assignments.sort(key=lambda assignment: assignment.start)

            for i in range(len(day_assignments) - 1):
                if day_assignments[i].store != day_assignments[i + 1].store:
                    occurrences += 1
                    if day_assignments[i + 1].start - day_assignments[i].end < Constants().commute_time:
                        insufficient_commute_time += 1
        return occurrences, insufficient_commute_time

    def get_tasks_overlap_count(self):
        """
        Number of times a workers is assigned two tasks at the same time
        :return: number of times that happens
        """
        overlap_count = 0
        for day in ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']:
            day_assignments = [assignment for assignment in self._schedule if assignment.day == day]
            day_assignments.sort(key=lambda assignment: assignment.start)

            for i in range(len(day_assignments) - 1):
                if day_assignments[i + 1].start < day_assignments[i].end:
                    overlap_count += 1
        return overlap_count

    def get_scheduled_time_off_error_count(self, time_off):
        """
        Number of hours scheduled on the worker's time off
        :param time_off: list of requested time off, e.g. [(mon, 8, 17), (wen, 12, 17), ...]
        :return: Number of times that happens
        """
        count = 0
        for day, start, end in time_off:
            for assignment in self._schedule:
                if assignment.day == day and (assignment.start < start < assignment.end or assignment.start < end < assignment.end or start < assignment.start < end or start < assignment.end < end):
                    count += 1
        return count

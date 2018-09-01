import json
import random
from Worker import Worker
from Workforce import Workforce
from StoreSchedule import StoreSchedule
from ScheduleAssignment import ScheduleAssignment
from Visualizer import Visualizer
from Constants import Constants
from typing import List


class Scheduler:
    def __init__(self, input_data=None):
        self.input_data = input_data

        self.constants = Constants()
        self.workforce = Workforce()
        for worker in self.input_data['workers']:
            self.workforce.add_worker(
                Worker(worker['first name'],
                       worker['last name'],
                       worker['normal hours'],
                       worker['hours left'],
                       worker['jobs'],
                       worker['store'],
                       worker['rest'])
            )

        self.initial_schedule = StoreSchedule()
        self.generate_initial_schedule()
        # self.initial_schedule.mutate(self.workforce)
        self.population = []  # type: List[StoreSchedule]

    def generate_initial_schedule(self):
        visualizer_id = 0
        for day, day_schedule in self.input_data['schedule'].items():
            for job, start, end, store, importance in day_schedule:
                self.initial_schedule.desired_schedule.append(ScheduleAssignment(None, store, job, day, start, end, visualizer_id, importance))
                selected_worker = self.workforce.get_best_worker_for_job(job, day, start, end)
                self.initial_schedule.assign(ScheduleAssignment(selected_worker, store, job, day, start, end, visualizer_id))
                visualizer_id += 1
        self.initial_schedule.visualizer_col_number = visualizer_id

    def crossover(self):
        for individual in self.population:
            individual.crossover(self.population[random.randint(0, len(self.population)-1)])

    def mutate(self):
        for individual in self.population:
            individual.mutate(self.workforce)


if __name__ == '__main__':
    with open('testDataIn.json', 'r') as f:
        data_in = json.load(f)
        scheduler = Scheduler(data_in)
        print(scheduler.initial_schedule.get_fitness(scheduler.workforce))
        visu = Visualizer(scheduler.initial_schedule.desired_schedule, scheduler.initial_schedule)

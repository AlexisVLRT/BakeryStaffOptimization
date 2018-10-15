import json
import random
from StoreSchedule import StoreSchedule
from ScheduleAssignment import ScheduleAssignment
from Visualizer import Visualizer
from Constants import Constants
from typing import List
from copy import deepcopy
import sys
import time
import matplotlib.pyplot as plt
import numpy as np
from sklearn.linear_model import LinearRegression
import json


class Scheduler:
    def __init__(self, input_data=None):
        self.input_data = input_data
        self.constants = Constants()

        self.initial_schedule = StoreSchedule(self.input_data)
        self.generate_initial_schedule()
        self.population = []  # type: List[StoreSchedule]
        self.new_generation = []  # type: List[StoreSchedule]
        self.generate_initial_population()

    def generate_initial_schedule(self):
        visualizer_id = 0
        for day, day_schedule in self.input_data['schedule'].items():
            for job, start, end, store, importance in day_schedule:
                self.initial_schedule.desired_schedule.append(ScheduleAssignment(None, store, job, day, start, end, visualizer_id, importance))
                selected_worker = self.initial_schedule.workforce.get_best_worker_for_job(job, day, start, end)
                self.initial_schedule.assign(ScheduleAssignment(selected_worker, store, job, day, start, end, visualizer_id))
                visualizer_id += 1
        self.initial_schedule.visualizer_col_number = visualizer_id

    def generate_initial_population(self):
        print('Generating initial population...')
        for _ in range(self.constants.population_size):
            self.population.append(deepcopy(self.initial_schedule))
        for _ in range(50):
            self.mutate(rate=20)
        print('Done')

    def mate(self):
        while len(self.new_generation):
            individual, mating_partner = self.new_generation[0], self.new_generation[random.randint(1, len(self.new_generation)-1)]
            child1, child2 = individual.mate(mating_partner)

            self.population.extend((child1, child2, individual, mating_partner))
            self.new_generation.remove(individual)
            self.new_generation.remove(mating_partner)

    def mutate(self, rate=None):
        for individual in self.population:
            individual.mutate(rate)

    def selection(self):
        # tournament selection
        while len(self.population):
            individual, opponent = self.population[0], self.population[random.randint(1, len(self.population)-1)]
            self.new_generation.append(individual) if individual.fitness > opponent.fitness else self.new_generation.append(opponent)
            self.population.remove(individual)
            self.population.remove(opponent)

    def get_population_stats(self):
        print('Calculating population stats...')
        best = -sys.maxsize - 1, None
        worst = sys.maxsize, None
        average = 0
        start = time.time()
        for individual in self.population:
            fitness, warnings = individual.get_fitness()
            best = (int(fitness), individual, warnings) if fitness > best[0] else best
            worst = (int(fitness), individual, warnings) if fitness < worst[0] else worst
            average += fitness/len(self.population)
        print('Done in ' + str(round(time.time() - start, 1)) + 's')
        return best, worst, int(average), len(self.population)


if __name__ == '__main__':
    plots = False

    with open('testDataIn.json', 'r') as f:
        data_in = json.load(f)

    scheduler = Scheduler(data_in)
    bests, worsts, averages = [], [], []
    best_individual = [-1000000]
    for generation in range(300):
        best, worst, average, pop_size = scheduler.get_population_stats()
        print('Generation {} : Best : {}, Worst : {}, Average : {}, Pop size : {}'.format(generation, best[0], worst[0], average, pop_size))
        bests.append(best[0])
        worsts.append(worst[0])
        averages.append(average)
        if best[0] >= best_individual[0]:
            best_individual = best

        if plots:
            plt.clf()
            plt.plot(np.array([bests, worsts, averages]).T)
            plt.pause(0.00001)

        trend_window = 10
        if len(averages) > trend_window:
            model = LinearRegression()
            X = [i for i in range(trend_window)]
            X = np.reshape(X, (len(X), 1))
            model.fit(X, averages[-trend_window:])
            trend = model.predict(X)
            if trend[0] > trend[-1]:
                print("Stopping early")
                break

        scheduler.mutate()
        scheduler.selection()
        scheduler.mate()

    best, worst, average, pop_size = scheduler.get_population_stats()
    print(best_individual[0], worst[0], average, pop_size, best[-1])
    with open('TestJson.json', 'w', encoding='utf8') as f:
        json.dump(best_individual[1].json_repr(), f, ensure_ascii=False, separators=(',', ':'), indent=4)
    # visu = Visualizer(scheduler.initial_schedule.desired_schedule, best_individual[1])

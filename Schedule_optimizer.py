import json
from Worker import Worker
from Workforce import Workforce
from StoreSchedule import StoreSchedule


class Scheduler:
    def __init__(self, input_data=None):
        self.input_data = input_data

        self.workforce = Workforce()

        for worker in self.input_data['workers']:
            self.workforce.add_worker(
                Worker(worker['first name'],
                       worker['last name'],
                       worker['normal hours'],
                       worker['hours left'],
                       worker['jobs'])
            )

        self.initial_schedule = StoreSchedule()
        self.generate_initial_schedule()

    def generate_initial_schedule(self):
        for day, day_schedule in self.input_data['schedule'].items():
            for job, start, end in day_schedule:
                selected_worker = self.workforce.get_best_worker_for_job(job, day, start, end)
                self.initial_schedule.assign(selected_worker, job, day, start, end)


if __name__ == '__main__':
    with open('testDataIn.json', 'r') as f:
        data_in = json.load(f)
        scheduler = Scheduler(data_in)
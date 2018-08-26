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

    def assign(self, worker, job, day, start, end):
        self.schedule[day].append([worker, job, start, end])
        worker.add_task(job, day, start, end)

    def get_fitness(self):
        return 0

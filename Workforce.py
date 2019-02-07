class Workforce:
    """
    A collection of workers
    """
    def __init__(self):
        self.workers = []

    def add_worker(self, worker):
        self.workers.append(worker)

    def get_best_worker_for_job(self, job, day, start, end):
        job_matching_importance = 1
        hours_worked_importance = 1

        scores = [0]*len(self.workers)
        for worker in self.workers:
            scores[self.workers.index(worker)] += worker.remaining_hours/worker.normal_hours*job_matching_importance
            if job in worker.jobs:
                scores[self.workers.index(worker)] += hours_worked_importance/(worker.jobs.index(job)+1)
            scores[self.workers.index(worker)] = 0 if worker.schedule.is_busy(day, start, end) else scores[self.workers.index(worker)]
            # print(worker.first_name, scores[self.workers.index(worker)])
        return self.workers[scores.index(max(scores))]

    def get_worker_by_id(self, worker_id):
        for worker in self.workers:
            if worker.worker_id == worker_id:
                return worker

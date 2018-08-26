class Workforce:
    def __init__(self):
        self._workers = []

    def add_worker(self, worker):
        self._workers.append(worker)

    def get_best_worker_for_job(self, job, day, start, end):
        job_matching_importance = 1
        hours_worked_importance = 1

        scores = [0]*len(self._workers)
        for worker in self._workers:
            scores[self._workers.index(worker)] += worker.remaining_hours/worker.normal_hours*job_matching_importance
            if job in worker.jobs:
                scores[self._workers.index(worker)] += hours_worked_importance/(worker.jobs.index(job)+1)
            scores[self._workers.index(worker)] = 0 if worker.schedule.is_busy(day, start, end) else scores[self._workers.index(worker)]
            # print(worker.first_name, scores[self._workers.index(worker)])
        return self._workers[scores.index(max(scores))]

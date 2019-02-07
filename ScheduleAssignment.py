class ScheduleAssignment:
    """
    A task for the schedule
    """
    def __init__(self, worker, store, job, day, start, end, visualizer_id, importance='recommended'):
        self.worker = worker
        self.store = store
        self.job = job
        self.day = day
        self.start = start
        self.end = end
        self.visualizer_id = visualizer_id
        self.importance = importance

    def json_repr(self):
        assignment = {
            'Worker': {'Id': self.worker.worker_id, 'FirstName': self.worker.first_name, 'LastName': self.worker.last_name},
            'Store': self.store,
            'JobName': self.job,
            'WeekDay': self.day,
            'StartTime': self.start,
            'EndTime': self.end,
            'Importance': self.importance
        }
        return assignment

    def __repr__(self):
        return '\nDay : {} | Start : {} | End : {} | Job : {}'.format(self.day, self.start, self.end, self.job)

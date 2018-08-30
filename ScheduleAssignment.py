class ScheduleAssignment:
    def __init__(self, worker, store, job, day, start, end, visualizer_id, importance='recommended'):
        self.worker = worker
        self.store = store
        self.job = job
        self.day = day
        self.start = start
        self.end = end
        self.visualizer_id = visualizer_id
        self.importance = importance

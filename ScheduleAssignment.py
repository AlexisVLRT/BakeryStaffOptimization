class ScheduleAssignment:
    def __init__(self, worker, job, day, start, end, visualizer_id):
        self.worker = worker
        self.job = job
        self.day = day
        self.start = start
        self.end = end
        self.visualizer_id = visualizer_id

from tkinter import *
from StoreSchedule import StoreSchedule
import json
import time


class Visualizer:
    def __init__(self, blank_schedule, full_schedule):
        self.blank_schedule = blank_schedule
        self.full_schedule = full_schedule

        self.tk = Tk()
        self.tk.title('Visualizer')
        self.frame = Frame(self.tk)
        self.frame.pack()
        self.canvas = Canvas(self.frame, height=500, width=800, bg='#bbbbbb')
        self.canvas.pack()
        self.display_blank(self.blank_schedule)
        self.tk.after(3000, self.display_full, self.full_schedule)
        # self.display_full(self.full_schedule)
        self.tk.mainloop()

    def display_blank(self, blank_schedule: StoreSchedule):
        schedule_data = blank_schedule.schedule
        days = ['mon', 'tue', 'wen', 'thu', 'fri', 'sat', 'sun']
        y = 0
        for i in range(5, 22):
            self.canvas.create_text(25, y+100, text=str(i))
            self.canvas.create_line(35, y+100, 37, y+100)
            y += 20

        x = 0
        for day in days:
            self.canvas.create_text(100+x, 80, text=day)
            self.canvas.create_line(50+x, 90, 50+x, 450)
            x += 100
        self.canvas.create_line(750, 90, 750, 450)

        for day, jobs in schedule_data.items():
            for job in jobs:
                job_name, start, end = job
                offset = (jobs.index(job)+1) * 80/len(jobs) - (40/len(jobs)) - 40
                self.add_task(offset, 80//len(jobs), job_name, day, start, end, True)

    def display_full(self, filled_schedule: StoreSchedule):
        for day in ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']:
            assignments = filled_schedule.get_assignments_day(day)
            for assignment in assignments:
                offset = (assignment.visualizer_id % 7 + 1) * 7*80/filled_schedule.visualizer_col_number - (7*40/filled_schedule.visualizer_col_number) - 40
                self.add_task(offset, 80//len(assignments), assignment.job, day, assignment.start, assignment.end, name=assignment.worker.first_name)

    def add_task(self, offset, width, job, day, start, end, bg=False, name=None):
        days = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']
        jobs = ['snack', 'vente', 'drive-pizza']
        colors = ['red', 'blue', 'green', 'yellow', 'pink', 'orange']
        start_px = (start - 5) * 20 + 100
        end_px = (end - 5) * 20 + 100
        x = 100 + days.index(day) * 100
        if bg:
            self.canvas.create_line(x + offset, start_px, x + offset, end_px, width=width, fill='dark ' + colors[jobs.index(job)])
        else:
            self.canvas.create_line(x + offset, start_px, x + offset, end_px, width=width*0.5, fill=colors[jobs.index(job)])
            self.canvas.create_text(x + offset, (start_px + end_px)/2, text=name, angle=90, fill='white')


if __name__ == '__main__':
    with open('testDataIn.json', 'r') as f:
        data_in = json.load(f)['schedule']
    schedule = StoreSchedule()
    schedule.schedule = data_in
    Visualizer(schedule)
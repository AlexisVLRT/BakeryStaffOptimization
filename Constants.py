class Constants:
    def __init__(self):
        config_contents = {}
        with open('config.txt', 'r') as f:
            config = f.readlines()
        for line in config:
            if '#' not in line and line.strip() != '':
                config_contents[line.split(':')[0].strip()] = line.split(':')[1].strip()

        self.mutation_rate = float(config_contents['mutation rate'].replace('%', ''))/100
        self.crossover_rate = float(config_contents['crossover rate'].replace('%', ''))/100
        self.commute_time = float(config_contents['commute time (hours)'])
        self.unqualified = float(config_contents['penalty unqualified'])
        self.weekly_rest = float(config_contents['penalty 24h rest'])
        self.daily_rest = float(config_contents['bonus per 11h break'])
        self.task_overlap = float(config_contents['penalty task overlap'])
        self.scheduled_on_time_off = float(config_contents['penalty scheduled on time off'])
        self.day_gap = float(config_contents['penalty 3h gap'])
        self.wrong_store = float(config_contents['penalty wrong store'])
        self.multiple_shops = float(config_contents['penalty multiple shops same day'])
        self.commuting = float(config_contents['penalty commuting not respected'])
        self.more_8_daily_hours = float(config_contents['penalty >8 hours in an day'])
        self.above_46 = float(config_contents['penalty >46 hours'])
        self.above_42 = float(config_contents['penalty >42 hours'])
        self.overtime = float(config_contents['penalty overtime'])
        self.overtime_dec = float(config_contents['bonus overtime reduction'])
        self.too_much_overtime_dec = float(config_contents['penalty >15% overtime reduction'])
        self.necessary_hours = float(config_contents['penalty necessary hours'])
        self.recommended_hours = float(config_contents['penalty recommended hours'])
        self.overfilling = float(config_contents['penalty overscheduling'])

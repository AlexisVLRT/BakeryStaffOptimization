class Constants:
    def __init__(self):
        config_contents = {}
        with open('config.txt', 'r') as f:
            config = f.readlines()
        for line in config:
            config_contents[line.split(':')[0].strip()] = line.split(':')[1].strip()

        self.mutation_rate = float(config_contents['mutation rate'].replace('%', ''))/100

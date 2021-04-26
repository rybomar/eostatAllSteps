from pathlib import Path
from Configuration import Configuration
from StatsCreator import StatsCreator


def loadConfiguration(args) -> Configuration:
    conf = Configuration(args)
    return conf


def prepareS1Stats(conf: Configuration):
    print('prepareS1Stats')
    statsCreator = StatsCreator(conf)
    statsCreator.doAllS1Steps()

def prepareS2Stats(conf: Configuration):
    print('prepareS1Stats')
    statsCreator = StatsCreator(conf)
    statsCreator.doAllS2Steps()


if __name__ == '__main__':
    args = 'args.txt'
    config = loadConfiguration(args)
    if Path(config.S1ProcessedDir).is_dir():
        prepareS1Stats(config)
    else:
        print('S1ProcessedDir does not exist, skipping it')
    if Path(config.S2ProcessedDir).is_dir():
        prepareS2Stats(config)
    else:
        print('S2ProcessedDir does not exist, skipping it')

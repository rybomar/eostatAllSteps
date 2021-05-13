from ClassificationProcess import ClassificationProcess
from Configuration import Configuration
from Configuration import ConfigurationArgs
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
    args = 'configurationArgsFilled.json'
    configArgs = ConfigurationArgs()
    configArgs.saveJSON('configurationEmpty.json')
    config = loadConfiguration(args)

    statsCreator = StatsCreator(config)
    statsCreator.doAllSteps()
    cl = ClassificationProcess(config)
    cl.prepareTraining()
    cl.doClassificationForAllObjects()

    # if Path(config.S1ProcessedDir).is_dir():
    #     prepareS1Stats(config)
    # else:
    #     print('S1ProcessedDir does not exist, skipping it')
    # if Path(config.S2ProcessedDir).is_dir():
    #     prepareS2Stats(config)
    # else:
    #     print('S2ProcessedDir does not exist, skipping it')

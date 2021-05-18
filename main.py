import sys

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


def main(argv):
    args = 'configurationFile.json'
    if len(argv) > 1:
        args = argv
    # configArgs = ConfigurationArgs()
    # configArgs.saveJSON('configurationEmpty.json')
    config = loadConfiguration(args)

    statsCreator = StatsCreator(config)
    statsCreator.doAllSteps()
    cl = ClassificationProcess(config)
    cl.prepareTraining()
    cl.doClassificationForAllObjects()


if __name__ == '__main__':
    main(sys.argv[1:])

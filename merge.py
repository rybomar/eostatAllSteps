import sys
from Configuration import Configuration
from MergeCreator import MergeCreator


def loadConfiguration(args) -> Configuration:
    conf = Configuration(args)
    return conf


def runMerge(argv):
    args = 'configurationFile.json'
    if len(argv) > 1:
        args = argv
    if len(args) == 0:
        print("Usage:\n")
        print("python eostatMerge.py configurationFile.json\n\n")
        print("(use the same config file like in eostatAllSteps)")
    else:
        config = loadConfiguration(args)
        mcreator = MergeCreator(config)
        mcreator.createMerge()

if __name__ == '__main__':
    runMerge(sys.argv[1:])

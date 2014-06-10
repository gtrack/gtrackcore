import random
import numpy.random

from gtrackcore_compressed.util.CustomExceptions import ShouldNotOccurError

class HbRandom(random.Random):
    _seed = None
    _storedStates = None

random = HbRandom()

def setManualSeed(seed):
    random._seed = seed
    
    if seed is None:
        seed = getRandomSeed()
        
    random.seed(seed)
    numpy.random.seed(seed)
    from gtrackcore_compressed.application.RSetup import r
    r('function(seed) {set.seed(seed)}')(seed)
    
def getManualSeed():
    return random._seed

def initSeed():
    setManualSeed(None)
    
def getRandomSeed():
    return random.randint(0, 2**31-1)    
    
def returnToStoredState():
    if random._storedStates is None:
        return ShouldNotOccurError('Tried to return to previous random state without a stored state.')
    
    random.setstate(random._storedStates[0])
    numpy.random.set_state(random._storedStates[1])
    from gtrackcore_compressed.application.RSetup import r
    r('function(state) {.Random.seed <- state}')(random._storedStates[2])

def storeState():
    from gtrackcore_compressed.application.RSetup import r
    r('runif(1)')
    random._storedStates = [random.getstate(), numpy.random.get_state(), r('.Random.seed')]
    

import random



class Roulette:
    '''
    Non-Lethal, Non-Weapon roulette game
    
    GAME DESCRIPTION HERE
    '''
    __STARTINGHEALTH = 3
    __SHELLMIN = 4
    __SHELLMAX = 8

    __chamber = []    #0 represent a blank, 1 represents live
    __turn = 0    #the turn of the player
    __hp = [__STARTINGHEALTH, __STARTINGHEALTH] #represents the hp of the two players

    def __init__(self):
        self.reset()

    def reset(self):
        '''
        load and reset the chamber
        '''    
        for x in range(random.randint(self.__SHELLMIN, self.__SHELLMAX)):
            self.__chamber.append(random.randint(0,1))

    
    def attack(self, attacker:int, target:int) -> int:
        '''
        attacker - the number of the player using the weapon
        target - the target of the weapon, relative to the attacker
                0 is self, 1 is opponent
        returns 1 if hit, 0 if blank
        '''
        fired = self.__chamber.pop(0) #the shell to be fired
        self.__turn += target #if attack target is self, do not change turns
        self.__hp[(attacker+target)%2] -= fired #remove hp from the target. If the shell is blank, 0 hp is removed
        return fired





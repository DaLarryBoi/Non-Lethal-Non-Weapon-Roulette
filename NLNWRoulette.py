import random


class Roulette:
    '''
    Non-Lethal, Non-Weapon roulette game
    
    GAME DESCRIPTION HERE
    '''
    __STARTINGHEALTH = 3
    
    __shells = 5

    __chamber = []    #0 represent a blank, 1 represents live
    __turn = 0    #the turn of the player
                    #player 0 starts, player 1 goes afterwards
                    #use turn%2 to find the current player
    
    __hp = [__STARTINGHEALTH, __STARTINGHEALTH] #represents the hp of the two players

    def __init__(self):
        self.reset()

    def reset(self):
        '''
        load and reset the chamber
        '''    
        self.__chamber = [0, 1]
        for x in range(self.__shells - 2):
            self.__chamber.append(random.randint(0,1))
        random.shuffle(self.__chamber)
        

    def attack(self, attacker:int, target:int) -> int:
        '''
        attacker - the number of the player using the weapon
        target - the number of the player being attacked
        returns 1 if hit, 0 if blank
        '''
        fired = self.__chamber.pop(0) #the shell to be fired
        self.__turn += (attacker != target) #if attack target is self, do not change turns
        self.__hp[target] -= fired #remove hp from the target. If the shell is blank, 0 hp is removed
        return fired
    def shellCount(self) -> tuple:
        '''
        return (blank, live) shells
        '''
        live = sum(self.__chamber)
        return (len(self.__chamber) - live, live)





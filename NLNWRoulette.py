import random



class Roulette:
    '''
    Non-Lethal, Non-Weapon roulette game
    
    GAME DESCRIPTION HERE
    '''
    STARTINGHEALTH = 3
    SHELLMIN = 4
    SHELLMAX = 8
    running = True
    chamber = []    #0 represent a blank, 1 represents live
    turn = 1    #the turn of the player
    p1HP = STARTINGHEALTH
    p2HP = STARTINGHEALTH

    def __init__(self):
        self.reset()

    def reset(self):
        '''
        load and reset the chamber
        '''    
        for x in range(random.randint(self.SHELLMIN, self.SHELLMAX)):
            self.chamber.append(random.randint(0,1))

    
    def attack(self, attacker:int, target:int) -> int:
        '''
        attacker - the number of the player using the weapon
        target - the target of the weapon
        returns 1 if hit, 0 if blank
        '''
        

    def __check(self) -> int:
        '''
        check the currently loaded round of the weapon
        if the current round is live, return 1
        if the current round is blank, return 0
        '''
        return self.chamber[0]


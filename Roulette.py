import random


class Roulette:
    '''
    Non-Lethal, Non-Weapon roulette game
    
    GAME DESCRIPTION HERE
    '''
    __PLAYERS = []
    __STARTINGHEALTH = 3
    
    __shells = 5

    __chamber = []    #0 represent a blank, 1 represents live
    __turn = 1    #the turn of the player
                    #player 1 starts, player 2 goes afterwards
                    #use turn%2 to find the current player
    
    __hp = [__STARTINGHEALTH, __STARTINGHEALTH] #represents the hp of the two players
                                                #hp[0] is player 1, hp[1] is player 2

    def __init__(self, p1, p2):
        self.reset()
        self.__PLAYERS = [p1,p2]

    def reset(self):
        '''
        load and reset the chamber
        '''    
        self.__chamber = [0, 1]
        for x in range(self.__shells - 2):
            self.__chamber.append(random.randint(0,1))
        random.shuffle(self.__chamber)
        

    def attack(self, attacker:int, target:int) -> tuple:
        '''
        attacker - the number of the player using the weapon
        target - the number of the player being attacked
        first variable 1 if live, 0 if blank
        second variable 0 if game is continuing, 1 if player 1 wins, 2 if player 2 wins
        returns in the format (hit, gameover)
        '''
        fired = self.__chamber.pop(0) #the shell to be fired
        self.__turn += (attacker != target) #if attack target is self, do not change turns
        self.__hp[target - 1] -= fired #remove hp from the target. If the shell is blank, 0 hp is removed
        gameover = 0
        if self.__hp[0] <= 0:
            #player 1 is out of hp
            #player 2 wins
            gameover = 2
        elif self.__hp[1] <= 0:
            #player 2 is out of hp
            #player 1 wins
            gameover = 1
        if fired == 1:
            #shell was a hit:
            self.reset()
        return (fired, gameover)
    def shellCount(self) -> tuple:
        '''
        return (blank, live) shells
        '''
        live = sum(self.__chamber)
        return (len(self.__chamber) - live, live)
    def players(self) -> tuple:
        '''
        return username of (p1, p2)
        '''
        return self.__PLAYERS
    def debug(self):
        '''
        DELETE THIS ONCE COMPLETE
        '''
        print("hp: ",self.__hp)
        print("chamber: ",self.__chamber)
        print("turn: ",self.__turn) 

# foo = Roulette()
# foo.debug()
# while True:
#     print("HIT:", foo.attack(1, 2))
#     print("BLAM")
#     foo.debug()
#     print("HIT:", foo.attack(1, 2))
#     print("BLAM")
#     foo.debug()
#     input("continue")





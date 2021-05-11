# -*- coding: utf-8 -*-

'''
Módulo para os estados.
'''

from enum import Enum

class InterfaceState(Enum):

    '''
    Estados das interfaces
    '''

    MAIN_MENU = 1
    MODIFICATION = 2
    GAMEPLAY = 3
    PAUSE = 4
    GAMEOVER = 5

class InterfaceEvent(Enum):

    '''
    Eventos da interface
    '''

    MODIFY = 1
    PLAY = 2
    EXIT = 3
    PAUSE = 4
    RESUME = 5
    RESTART = 6
    RETURN_TO_MENU = 7

class GameState(Enum):

    '''
    Estados do jogo
    '''

    MENU = 1
    GAMEPLAY = 2
    PAUSE = 3
    GAMEOVER = 4
    EXIT = 5

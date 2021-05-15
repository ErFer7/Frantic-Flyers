# -*- coding: utf-8 -*-

'''
Módulo para os estados.
'''

from enum import Enum


class Event(Enum):

    '''
    Eventos do jogo
    '''

    UI_MODIFY = 1
    UI_RETURN_TO_MENU = 2
    UI_PLAY = 3
    UI_EXIT = 4
    UI_PAUSE = 5
    UI_RESUME = 6
    UI_RESTART = 7
    GP_LOST = 8


class State(Enum):

    '''
    Estados do jogo
    '''

    MAIN_MENU = 1
    MODIFICATION_MENU = 2
    GAMEPLAY = 3
    PAUSE = 4
    GAMEOVER = 5
    RESTART = 6
    EXIT = 7

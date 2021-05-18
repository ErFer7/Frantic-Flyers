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
    UI_REDUCE_VELOCITY = 3
    UI_INCREASE_VELOCITY = 4
    UI_REDUCE_DAMAGE = 5
    UI_INCREASE_DAMAGE = 6
    UI_REDUCE_FIRERATE = 7
    UI_INCREASE_FIRERATE = 8
    UI_REDUCE_ARMOR = 9
    UI_INCREASE_ARMOR = 10
    UI_REDUCE_BULLET_TYPE = 11
    UI_INCREASE_BULLET_TYPE = 12
    UI_PLAY = 13
    UI_EXIT = 14
    UI_PAUSE = 15
    UI_RESUME = 16
    UI_RESTART = 17
    GP_GAMEOVER = 18


class State(Enum):

    '''
    Estados do jogo
    '''

    MAIN_MENU = 1
    MODIFICATION_MENU = 2
    GAMEPLAY = 3
    PAUSE = 4
    GAMEOVER = 5
    EXIT = 6

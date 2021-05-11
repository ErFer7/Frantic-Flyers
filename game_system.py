# -*- coding: utf-8 -*-

'''
Módulo para o gerenciador de jogo.
'''

import sys

from random import seed
from time import time_ns

import pygame

from states import GameState
from user_interface import UserInterfaceManager

class GameManager():

    '''
    Classe que gerencia o funcionamento do jogo
    '''

    clock: pygame.time.Clock
    display: pygame.display.set_mode
    music_channel: pygame.mixer.Channel
    sound_effects_channel: pygame.mixer.Channel
    state: GameState
    user_interface: UserInterfaceManager

    def __init__(self, version):

        seed(time_ns())

        pygame.display.init()
        pygame.font.init()
        pygame.mixer.init()

        self.clock = pygame.time.Clock()
        self.display = pygame.display.set_mode(flags=pygame.FULLSCREEN)
        self.music_channel = pygame.mixer.Channel(0)
        self.sound_effects_channel = pygame.mixer.Channel(1)

        self.state = GameState.MENU

        self.user_interface = UserInterfaceManager((self.display.get_width(),
                                                    self.display.get_height()),
                                                    version)

    def run_game(self, fps):

        '''
        Roda o jogo
        '''

        while self.state != GameState.EXIT:

            # Atualizar o gameplay

            # Atualizar os gráficos

            self.user_interface.update_interface(self.state,
                                                 pygame.event.get(),
                                                 pygame.mouse.get_pos())

            interface_state = self.user_interface.get_state()
            # Obter estado de gameplay

            # Calcular qual será o próximo estado do jogo e fazer as operações

            self.display.update()
            self.clock.tick(fps)

        pygame.quit()
        sys.exit()

class GameplayManager():

    '''
    Classe que gerencia o gameplay
    '''

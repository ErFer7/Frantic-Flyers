# -*- coding: utf-8 -*-

'''
Módulo para o gerenciador de jogo.
'''

import sys

from random import seed
from time import time_ns

import pygame

from states import Event, State
from entities import EntityManager
from physics import PhysicsManager
from graphics import GraphicsManager
from user_interface import UserInterfaceManager

class GameManager():

    '''
    Classe que gerencia o funcionamento do jogo
    '''

    clock: pygame.time.Clock
    display: pygame.display.set_mode
    music_channel: pygame.mixer.Channel
    sound_effects_channel: pygame.mixer.Channel
    state: State
    events: list
    gameplay: None
    entities: EntityManager
    physics: PhysicsManager
    graphics: GraphicsManager
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

        self.state = State.MAIN_MENU
        self.events = []

        self.gameplay = GameplayManager()
        self.entities = EntityManager()
        self.physics = PhysicsManager()
        self.graphics = GraphicsManager()
        self.user_interface = UserInterfaceManager((self.display.get_width(),
                                                    self.display.get_height()),
                                                    version)

    def run_game(self, fps):

        '''
        Roda o jogo
        '''

        while self.state != State.EXIT:

            # Atualiza cada sistema
            self.gameplay.update_gameplay()
            self.entities.update_entities()
            self.physics.update_physics()
            self.graphics.update_graphics()
            self.user_interface.update_interface(self.state,
                                                 self.display,
                                                 pygame.event.get(),
                                                 pygame.mouse.get_pos())

            # Obtém os eventos do jogo
            self.events.append(self.user_interface.get_event())

            for event in self.events:

                if event is not None:

                    if event == Event.UI_MODIFY:

                        self.state = State.MODIFICATION_MENU
                    elif event == Event.UI_RETURN_TO_MENU:

                        self.state = State.MAIN_MENU
                    elif event == Event.UI_PLAY:

                        self.state = State.GAMEPLAY
                    elif event == Event.UI_EXIT:

                        self.state = State.EXIT
                    elif event == Event.UI_PAUSE:

                        self.state = State.PAUSE
                    elif event == Event.UI_RESUME:

                        self.state = State.GAMEOVER
                    elif event == Event.UI_RESTART:

                        self.state = State.RESTART
                    elif event == Event.GP_LOST:

                        self.state = State.GAMEOVER

            self.events.clear()

            pygame.display.update()
            self.clock.tick(fps)

        pygame.quit()
        sys.exit()

class GameplayManager():

    '''
    Classe que gerencia o gameplay
    '''

    def update_gameplay(self):
        '''
        Atualiza o gameplay
        '''

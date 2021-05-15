# -*- coding: utf-8 -*-

'''
Módulo para o gerenciador de jogo.
'''

import sys
import os

from random import seed
from time import time_ns

import pygame

from states import Event, State
from file_system import FileSystem
from entities import EntityManager
from physics import PhysicsManager
from graphics import GraphicsManager
from user_interface import UserInterfaceManager


class GameManager():

    '''
    Classe que gerencia o funcionamento do jogo e armazena dados do jogador.
    '''

    clock: pygame.time.Clock
    display: pygame.display.set_mode
    music_channel: pygame.mixer.Channel
    sound_effects_channel: pygame.mixer.Channel
    state: State
    events: list
    file_system: FileSystem
    data: dict
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
        #self.display = pygame.display.set_mode(flags=pygame.FULLSCREEN)
        self.display = pygame.display.set_mode(flags=pygame.RESIZABLE)
        self.music_channel = pygame.mixer.Channel(0)
        self.sound_effects_channel = pygame.mixer.Channel(1)

        self.state = State.MAIN_MENU
        self.events = []

        self.file_system = FileSystem(os.path.join("Data", "Player Data.json"))

        # Inicializa o jogo com os dados padrões e depois verifica se é necessário
        # Carregar os dados da memória permanente.
        self.data = {"Modification Points": 0,
                     "Agility": 0,
                     "Damage": 0,
                     "Fire Rate": 0,
                     "Armor": 0}

        if len(self.file_system.get_data()) > 0:

            self.data = self.file_system.get_data()

        self.gameplay = GameplayManager()
        self.entities = EntityManager()
        self.physics = PhysicsManager()
        self.graphics = GraphicsManager()
        self.user_interface = UserInterfaceManager((self.display.get_width(),
                                                    self.display.get_height()),
                                                   version)

    def run_game(self, fps):
        '''
        Roda o jogo.
        '''

        while self.state != State.EXIT:

            # Atualiza cada sistema
            self.gameplay.update_gameplay()
            self.entities.update_entities()
            self.physics.update_physics()
            self.graphics.update_graphics()
            self.user_interface.update_interface(self.state,
                                                 self.display,
                                                 pygame.event.get())

            # Obtém os eventos do jogo
            self.events.append(self.user_interface.get_event())

            for event in self.events:

                if event is not None:

                    if event == Event.UI_MODIFY:

                        self.state = State.MODIFICATION_MENU
                        # Tocar o áudio do botão aqui
                    elif event == Event.UI_RETURN_TO_MENU:

                        self.state = State.MAIN_MENU
                        # Tocar o áudio do botão aqui
                    elif event == Event.UI_PLAY:

                        self.state = State.GAMEPLAY
                        # Tocar o áudio do botão aqui
                    elif event == Event.UI_EXIT:

                        self.state = State.EXIT
                        # Tocar o áudio do botão aqui
                    elif event == Event.UI_PAUSE:

                        self.state = State.PAUSE
                        # Tocar o áudio do botão aqui
                    elif event == Event.UI_RESUME:

                        self.state = State.GAMEOVER
                        # Tocar o áudio do botão aqui
                    elif event == Event.UI_RESTART:

                        self.state = State.RESTART
                        # Tocar o áudio do botão aqui
                    elif event == Event.GP_LOST:

                        self.state = State.GAMEOVER

            self.events.clear()

            pygame.display.update()
            self.clock.tick(fps)

        pygame.quit()
        sys.exit()


class GameplayManager():

    '''
    Classe que gerencia o gameplay.
    '''

    def update_gameplay(self):
        '''
        Atualiza o gameplay.
        '''

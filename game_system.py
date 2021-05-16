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
                     "Velocity": 25,
                     "Damage": 25,
                     "Firerate": 25,
                     "Armor": 25}

        if len(self.file_system.get_data()) > 0:

            self.data = self.file_system.get_data()
        else:

            self.file_system.set_data(self.data)

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
            self.entities.update()
            self.physics.update()
            self.graphics.update()
            self.user_interface.update(self.state,
                                       self.display,
                                       pygame.event.get(),
                                       self.data,
                                       self.entities.get_player_score(),
                                       self.entities.get_player_life())

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
                    elif event == Event.UI_REDUCE_VELOCITY:

                        self.change_modifiers("Velocity", False)
                        # Tocar o áudio do botão aqui
                    elif event == Event.UI_INCREASE_VELOCITY:

                        self.change_modifiers("Velocity", True)
                        # Tocar o áudio do botão aqui
                    elif event == Event.UI_REDUCE_DAMAGE:

                        self.change_modifiers("Damage", False)
                        # Tocar o áudio do botão aqui
                    elif event == Event.UI_INCREASE_DAMAGE:

                        self.change_modifiers("Damage", True)
                        # Tocar o áudio do botão aqui
                    elif event == Event.UI_REDUCE_FIRERATE:

                        self.change_modifiers("Firerate", False)
                        # Tocar o áudio do botão aqui
                    elif event == Event.UI_INCREASE_FIRERATE:

                        self.change_modifiers("Firerate", True)
                        # Tocar o áudio do botão aqui
                    elif event == Event.UI_REDUCE_ARMOR:

                        self.change_modifiers("Armor", False)
                        # Tocar o áudio do botão aqui
                    elif event == Event.UI_INCREASE_ARMOR:

                        self.change_modifiers("Armor", True)
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

                        self.state = State.GAMEPLAY
                        # Tocar o áudio do botão aqui
                    elif event == Event.UI_RESTART:

                        # Resetar o gameplay aqui

                        self.state = State.GAMEPLAY
                        # Tocar o áudio do botão aqui
                    elif event == Event.GP_GAMEOVER:

                        # Operações finais aqui

                        self.state = State.GAMEOVER

                    break

            self.events.clear()

            pygame.display.update()
            self.clock.tick(fps)

        pygame.quit()
        sys.exit()

    def change_modifiers(self, modifier, increase):
        '''
        Muda os modificadores.
        '''

        if increase:

            if self.data[modifier] < 100 and self.data["Modification Points"] > 0:

                self.data[modifier] += 1
                self.data["Modification Points"] -= 1
        else:

            if self.data[modifier] > 0:

                self.data[modifier] -= 1
                self.data["Modification Points"] += 1

        self.file_system.write_file()

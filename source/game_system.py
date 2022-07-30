# -*- coding: utf-8 -*-

'''
Módulo para o gerenciador de jogo.
'''

import sys

from random import seed
from time import time_ns
from os.path import join

import pygame

from source.states import Event, State
from source.file_system import FileSystem, AssetContainer
from source.entities import EntityManager
from source.physics import PhysicsManager
from source.graphics import GraphicsManager
from source.user_interface import UserInterfaceManager


class GameManager():

    '''
    Classe que gerencia o funcionamento do jogo e armazena dados do jogador.
    '''

    clock: pygame.time.Clock  # CLock para o fps
    display: pygame.display.set_mode  # Display da tela
    music_channel: pygame.mixer.Channel  # Canal de música
    state: State  # Estado do jogo
    events: list  # Lista de eventos
    asset_container: AssetContainer
    file_system: FileSystem  # Sistema de arquivos
    data: dict  # Dados
    entities: EntityManager  # Sistema de entidades
    physics: PhysicsManager  # Sistema de física
    graphics: GraphicsManager  # Sistema gráfico
    user_interface: UserInterfaceManager  # Sistema de interface

    def __init__(self, version):

        seed(time_ns())  # Inicializa o RNG

        # Inicializa o pygame
        pygame.display.init()
        pygame.font.init()
        pygame.mixer.init()

        self.clock = pygame.time.Clock()
        self.display = pygame.display.set_mode(flags=pygame.FULLSCREEN)

        # Serialization
        self.asset_container = AssetContainer()

        self.music_channel = pygame.mixer.Channel(0)
        self.music = pygame.mixer.Sound(self.asset_container.get_audio("music", "Music 1.wav"))
        self.music_channel.play(self.music, loops=-1)

        self.state = State.MAIN_MENU
        self.events = []

        self.file_system = FileSystem(join("Data", "Player Data.json"))

        # Inicializa o jogo com os dados padrões e depois verifica se é necessário
        # Carregar os dados da memória permanente.

        self.data = {"Modification Points": 0,
                     "Velocity": 25,
                     "Damage": 25,
                     "Firerate": 25,
                     "Armor": 25,
                     "Bullet Type": 0}

        if len(self.file_system.get_data()) > 0:

            self.data = self.file_system.get_data()
        else:

            self.file_system.set_data(self.data)

        # Obtém o tamanho da tela
        screen_size = (self.display.get_width(), self.display.get_height())

        self.entities = EntityManager(screen_size, 100, 10, 5, self.asset_container)
        self.physics = PhysicsManager()
        self.graphics = GraphicsManager((92, 184, 230))
        self.user_interface = UserInterfaceManager(screen_size, version, self.asset_container)

    def run_game(self, tick):
        '''
        Roda o jogo.
        '''

        while self.state != State.EXIT:  # Enquando o jogo não for encerrado

            events = pygame.event.get()  # Obtém os eventos (teclado e mouse)

            # Atualiza cada sistema
            self.entities.update(self.state, events, tick)
            self.physics.update(self.state, tick, self.entities.get_entities(True))
            self.graphics.update(self.state, self.display, self.entities.get_entities(False))
            self.user_interface.update(self.state,
                                       self.display,
                                       events,
                                       self.data,
                                       self.entities.get_score(),
                                       self.entities.get_player_life())

            # Obtém os eventos de cada sistema
            self.events.append(self.entities.get_event())
            self.events.append(self.user_interface.get_event())

            # Para cada evento determina o próximo estado e operações a serem feitas
            for event in self.events:

                if event is not None:

                    if event == Event.UI_MODIFY:

                        self.state = State.MODIFICATION_MENU
                    elif event == Event.UI_RETURN_TO_MENU:

                        self.state = State.MAIN_MENU
                    elif event == Event.UI_REDUCE_VELOCITY:

                        self.change_modifiers("Velocity", False)
                    elif event == Event.UI_INCREASE_VELOCITY:

                        self.change_modifiers("Velocity", True)
                    elif event == Event.UI_REDUCE_DAMAGE:

                        self.change_modifiers("Damage", False)
                    elif event == Event.UI_INCREASE_DAMAGE:

                        self.change_modifiers("Damage", True)
                    elif event == Event.UI_REDUCE_FIRERATE:

                        self.change_modifiers("Firerate", False)
                    elif event == Event.UI_INCREASE_FIRERATE:

                        self.change_modifiers("Firerate", True)
                    elif event == Event.UI_REDUCE_ARMOR:

                        self.change_modifiers("Armor", False)
                    elif event == Event.UI_INCREASE_ARMOR:

                        self.change_modifiers("Armor", True)
                    elif event == Event.UI_REDUCE_BULLET_TYPE:

                        self.change_modifiers("Bullet Type", False)
                    elif event == Event.UI_INCREASE_BULLET_TYPE:

                        self.change_modifiers("Bullet Type", True)
                    elif event == Event.UI_PLAY:

                        self.entities.update_player_modifiers(self.data)
                        self.entities.reset()
                        self.state = State.GAMEPLAY
                    elif event == Event.UI_EXIT:

                        self.state = State.EXIT
                    elif event == Event.UI_PAUSE:

                        self.state = State.PAUSE
                    elif event == Event.UI_RESUME:

                        self.state = State.GAMEPLAY
                    elif event == Event.UI_RESTART:

                        self.entities.reset()
                        self.state = State.GAMEPLAY
                    elif event == Event.GP_GAMEOVER:

                        self.data["Modification Points"] += self.entities.get_score() // 500
                        self.state = State.GAMEOVER

                    self.user_interface.play_sound()  # Toca o som da interface
                    break

            self.events.clear()

            pygame.display.update()  # Atualiza o display
            self.clock.tick(tick)  # Espera o clock

        # Salva os dados e encerra o jogo
        self.file_system.write_file()
        pygame.quit()
        sys.exit()

    def change_modifiers(self, modifier, increase):
        '''
        Muda os modificadores. Limita cada modificador a um intervalo de 0 a 100. Cada modificação
        é salva na memória permanente.
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

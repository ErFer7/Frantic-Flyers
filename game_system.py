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
    sfx_channel: pygame.mixer.Channel
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
        self.display = pygame.display.set_mode(flags=pygame.FULLSCREEN)

        self.music_channel = pygame.mixer.Channel(0)
        self.music = pygame.mixer.Sound(os.path.join("Audio", "Music", "Music 1.wav"))
        self.music_channel.play(self.music, loops=-1)

        self.state = State.MAIN_MENU
        self.events = []

        self.file_system = FileSystem(os.path.join("Data", "Player Data.json"))

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

        screen_size = (self.display.get_width(), self.display.get_height())

        self.entities = EntityManager(screen_size, 100, 10, 5)
        self.physics = PhysicsManager()
        self.graphics = GraphicsManager((92, 184, 230))
        self.user_interface = UserInterfaceManager(screen_size, version)

    def run_game(self, tick):
        '''
        Roda o jogo.
        '''

        while self.state != State.EXIT:

            events = pygame.event.get()

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

            # Obtém os eventos do jogo
            self.events.append(self.entities.get_event())
            self.events.append(self.user_interface.get_event())

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

                    self.user_interface.play_sound()
                    break

            self.events.clear()

            pygame.display.update()
            self.clock.tick(tick)

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

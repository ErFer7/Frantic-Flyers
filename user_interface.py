# -*- coding: utf-8 -*-

'''
Módulo para o sistema de interfaces.
'''

import os

from enum import Enum
from math import ceil

import pygame

import graphics

class UserInterfaceManager():

    '''
    Gerencia as interfaces
    '''

class Alignment(Enum):

    '''
    Alinhamento do elemento da UI
    '''

    CENTER = 1
    TOP_LEFT = 2
    TOP_RIGHT = 3

class UserInterface():

    '''
    Define a base de uma tela
    '''

    position: list  # Posição
    screen_size: list  # Tamanho da tela
    texts: list  # textos
    buttons: dict  # Botões
    surface: pygame.Surface  # Superfície
    selection_sound: pygame.mixer.Sound  # Som de seleção

    def __init__(self, position, size, screen_size):

        self.position = position[:]
        self.screen_size = screen_size[:]
        self.texts = []
        self.buttons = {}
        self.surface = pygame.Surface(size)
        self.selection_sound = pygame.mixer.Sound(os.path.join("Audio", "Selection.wav"))

    def update(self, display):
        '''
        Atualiza e renderiza a interface
        '''

        self.surface.fill((20, 20, 20))

        for key in self.buttons:

            self.buttons[key].sprites.draw(self.surface)

        for text in self.texts:

            self.surface.blit(text.text, text.position)

        display.blit(self.surface, self.position)

        pygame.display.update()

    def check_buttons(self, click_position):
        '''
        Checa qual botão está sendo pressionado
        '''

        for key in self.buttons:

            if self.buttons[key].is_clicked(click_position):

                return key

    def delete(self):
        '''
        Libera os sprites dos botões
        '''

        for button in self.buttons:

            self.buttons[button].delete()

class Button():

    '''
    Define um botão
    '''

    position: list  # Posição
    size: list  # Tamanho
    sprites: pygame.sprite.RenderPlain()  # Sprites

    def __init__(self, alignment, position, size, screen_size):

        self.position = [0, 0]
        self.size = size[:]
        self.sprites = pygame.sprite.RenderPlain()

        # Calcula a posiçõa com base no alinhamento
        if alignment == Alignment.TOP_LEFT:

            self.position = position[:]
        elif alignment == Alignment.TOP_RIGHT:

            self.position = (screen_size[0] - position[0], position[1])
        else:

            self.position = ((screen_size[0] - size[0]) / 2 + position[0],
                             (screen_size[1] - size[1]) / 2 - position[1])

        self.sprites.add(graphics.RectangleSprite(self.position, size, (255, 223, 0)))
        self.sprites.add(graphics.RectangleSprite((self.position[0] + 10, self.position[1] + 10),
                                                  (size[0] - 20, size[1] - 20),
                                                  (20, 20, 20)))

    def is_clicked(self, click_position):
        '''
        Checa se o botão foi clicado
        '''

        if click_position[0] >= self.position[0]                         \
                and click_position[0] <= self.position[0] + self.size[0] \
                and click_position[1] >= self.position[1]                \
                and click_position[1] <= self.position[1] + self.size[1]:

            return True
        else:

            return False

    def delete(self):
        '''
        Libera os sprites
        '''

        self.sprites.empty()

class Text():

    '''
    Define o elemento de texto
    '''

    size: int  # Tamanho
    position: list  # Posição
    font: pygame.font.Font  # Fonte
    text: pygame.font.Font.render  # Superfície renderizada
    color: pygame.color.Color  # Cor

    def __init__(self, text, alignment, position, size, color, screen_size, font="joystix monospace.ttf"):

        self.size = size
        self.position = [0, 0]
        self.color = pygame.color.Color(color)
        self.font = pygame.font.Font(os.path.join("Fonts", font), self.size)
        self.text = self.font.render(text, False, self.color)

        # Calcula a posição com base no alinhamento
        if alignment == Alignment.TOP_LEFT:

            self.position = position[:]
        elif alignment == Alignment.TOP_RIGHT:

            self.position = (screen_size[0] - position[0], position[1])
        else:

            self.position = ((screen_size[0] - self.text.get_rect().width) / 2 + position[0],
                             (screen_size[1] - self.text.get_rect().height) / 2 - position[1])

    def update(self, text):
        '''
        Atualiza o texto
        '''

        self.text = self.font.render(text, False, self.color)

# class Background():

#     '''
#     Define o plano de fundo com sprites
#     '''

#     sprites: pygame.sprite.RenderPlain  # Sprites

#     def __init__(self, size):

#         self.sprites = pygame.sprite.RenderPlain()

#         # Preenche o tamanho especificado com sprites
#         for i in range(ceil(size[1] / 256.0)):

#             for j in range(ceil(size[0] / 256.0)):

#                 self.sprites.add(graphics.BackgroundSprite((j * 256.0, i * 256.0)))

#     def delete(self):
#         '''
#         Libera os sprites
#         '''

#         self.sprites.empty()

class Bar():

    '''
    Define uma barra
    '''

    position: list  # Posição
    sprites: pygame.sprite.RenderPlain  # Sprites

    def __init__(self, alignment, position, size, border_color, color, screen_size):

        self.position = [0, 0]
        self.size = size
        self.sprites = pygame.sprite.RenderPlain()

        # Define a posição com base no alinhamento
        if alignment == Alignment.TOP_LEFT:

            self.position = position[:]
        elif alignment == Alignment.TOP_RIGHT:

            self.position = (screen_size[0] - position[0], position[1])
        else:

            self.position = ((screen_size[0] - self.size[0]) / 2 + position[0],
                             (screen_size[1] - self.size[1]) / 2 - position[1])

        self.sprites.add(graphics.RectangleSprite((self.position[0] - 5, self.position[1] - 5),
                                                  (self.size[0] + 10, self.size[1] + 10),
                                                  border_color))
        self.sprites.add(graphics.RectangleSprite(self.position, self.size, color))

    def update(self, value):
        '''
        Atualiza o tamanho da barra com base em um valor de 0 a 100 (percentual)
        '''

        self.sprites.sprites()[1].update(self.position, [int((self.size[0] / 100.0) * value), 35])

    def delete(self):
        '''
        Libera os sprites
        '''

        self.sprites.empty()

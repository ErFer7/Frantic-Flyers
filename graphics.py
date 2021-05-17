# -*- coding: utf-8 -*-

'''
Módulo para o sistema gráfico.
'''

import pygame

from states import State


class GraphicsManager():

    '''
    Gerencia os graficos
    '''

    render_group: pygame.sprite.RenderPlain
    background_color: pygame.color.Color

    def __init__(self, background_color):

        self.render_group = pygame.sprite.RenderPlain()
        self.background_color = pygame.color.Color(background_color)

    def update(self, state, display, entities):
        '''
        Atualiza os gráficos.
        '''
        if state == State.GAMEPLAY:

            display.fill(self.background_color)

            for entity in entities:

                self.render_group.add(entity.get_sprite())

            self.render_group.draw(display)
            self.render_group.empty()


class CustomSprite(pygame.sprite.Sprite):

    '''
    Define um sprite retangular
    '''

    def __init__(self, position, size, image_path=None, color=None):

        super().__init__()

        # Inicializa as variáveis

        if image_path is not None:

            self.image = pygame.transform.scale(pygame.image.load(image_path).convert_alpha(),
                                                size)
        else:

            self.image = pygame.Surface(size)
        self.rect = self.image.get_rect()
        self.rect.x = position[0]
        self.rect.y = position[1]

        if color is not None:

            self.image.fill(color)

    def update(self, position, size=None):
        '''
        Redefine o tamanho do sprite
        '''

        if size is not None:

            self.image = pygame.transform.scale(self.image, size)

        self.rect.x = position[0]
        self.rect.y = position[1]

# -*- coding: utf-8 -*-

'''
Módulo para o sistema gráfico.
'''

import pygame

class RectangleSprite(pygame.sprite.Sprite):

    '''
    Define um sprite retangular
    '''

    def __init__(self, position, size, *color):

        super().__init__()

        # Inicializa as variáveis
        self.image = pygame.Surface(size)
        self.rect = self.image.get_rect()
        self.rect.x = position[0]
        self.rect.y = position[1]
        self.image.fill(color)

    def update(self, position, size):
        '''
        Redefine o tamanho do sprite
        '''

        if size[0] == 0:

            size[0] = 1

        if size[1] == 0:

            size[1] = 1

        self.image = pygame.transform.scale(self.image, size)
        self.rect.x = position[0]
        self.rect.y = position[1]

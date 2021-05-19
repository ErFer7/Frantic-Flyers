# -*- coding: utf-8 -*-

'''
Módulo para o sistema gráfico.
'''

import pygame

from states import State


class GraphicsManager():

    '''
    Gerencia os graficos durante o gameplay.
    '''

    render_group: pygame.sprite.RenderPlain  # Grupo de sprites
    background_color: pygame.color.Color  # Cor do plano de fundo

    def __init__(self, background_color):

        self.render_group = pygame.sprite.RenderPlain()
        self.background_color = pygame.color.Color(background_color)

    def update(self, state, display, entities):
        '''
        Atualiza os gráficos.
        '''

        if state == State.GAMEPLAY:  # Se for o gameplay

            display.fill(self.background_color)  # Preenche a tela com a cor do plano de fundo

            # Adiciona o sprite de cada entidade no grupo de sprites
            for entity in entities:

                self.render_group.add(entity.get_sprite())

            self.render_group.draw(display)  # Renderiza o grupo de sprites
            self.render_group.empty()  # Limpa o grupo de sprites


class CustomSprite(pygame.sprite.Sprite):

    '''
    Define um sprite.
    '''

    def __init__(self, position, size, image_path=None, color=None, angle=0.0):

        super().__init__()

        # Carrega uma imagem se tiver ou desenha um retângulo
        if image_path is not None:

            self.image = pygame.transform.scale(pygame.image.load(image_path).convert_alpha(),
                                                size)
            self.image = pygame.transform.rotate(self.image, angle)
        else:

            self.image = pygame.Surface(size)

        # Define os atributos do sprite
        self.rect = self.image.get_rect()
        self.rect.x = position[0]
        self.rect.y = position[1]

        if color is not None:  # Preenche com uma cor caso tenha

            self.image.fill(color)

    def update(self, position, size=None):
        '''
        Redefine a posição e tamanho do sprite.
        '''

        if size is not None:

            self.image = pygame.transform.scale(self.image, size)

        self.rect.x = int(position[0])
        self.rect.y = int(position[1])


class CustomAnimatedSprite(pygame.sprite.Sprite):

    '''
    Sprite que pode ser animado.
    '''

    images: list  # Imagens
    animating: bool  # Define se está animando ou não
    step: int  # Frame da animação

    def __init__(self, position, size, path_list):

        super().__init__()

        self.images = []
        self.animating = False
        self.step = 0

        # Para cada caminho carrega uma imagem
        for path in path_list:

            self.images.append(pygame.transform.scale(pygame.image.load(path).convert_alpha(),
                                                      size))

        # Define os atributos do sprite
        self.image = self.images[0]
        self.rect = self.image.get_rect()
        self.rect.x = position[0]
        self.rect.y = position[1]

    def start_animation(self):
        '''
        Inicia a animação.
        '''

        self.animating = True

    def animate_frame(self):
        '''
        Anima um frame. Troca a imagem atual caso a animação ainda não tenha acabado.
        '''

        if self.animating and self.step < len(self.images):

            self.image = self.images[self.step]
            self.step += 1
        else:

            self.step = 0
            self.animating = False

    def is_animating(self):
        '''
        Retorna verdadeiro caso o sprite esteja sendo animado.
        '''

        return self.animating

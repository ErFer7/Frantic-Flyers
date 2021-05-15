# -*- coding: utf-8 -*-

'''
Módulo para o sistema de interfaces.
'''

import os

from enum import Enum

import pygame

import graphics  # Usar from
from states import Event, State


class UserInterfaceManager():

    '''
    Gerencia as interfaces
    '''

    user_interface_event: Event
    main_menu: None
    modification_menu: None

    def __init__(self, screen_size, version):

        self.user_interface_event = None
        self.main_menu = MainMenu(screen_size, version, (92, 184, 230))
        self.modification_menu = ModificationMenu(screen_size, (92, 184, 230))

    def update_interface(self, state, display, events):
        '''
        Atualiza os eventos e gráficos da interface
        '''

        # Atualiza os eventos
        for event in events:

            self.user_interface_event = None

            if state == State.MAIN_MENU:

                self.user_interface_event = self.main_menu.check_buttons(event)
                self.main_menu.update(display)
            elif state == State.MODIFICATION_MENU:

                self.user_interface_event = self.modification_menu.check_buttons(event)
                self.modification_menu.update(display)

    def get_event(self):
        '''
        Retorna o estado.
        '''

        return self.user_interface_event


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

    position: tuple  # Posição
    screen_size: tuple  # Tamanho da tela
    texts: list  # textos
    buttons: list  # Botões
    surface: pygame.Surface  # Superfície
    background: None
    background_color: pygame.color.Color
    selection_sound: pygame.mixer.Sound  # Som de seleção

    def __init__(self, position, size, screen_size, background_color):

        self.position = position
        self.screen_size = screen_size
        self.texts = []
        self.buttons = []
        self.surface = pygame.Surface(size)
        self.background = None
        self.background_color = pygame.color.Color(background_color)
        self.selection_sound = pygame.mixer.Sound(os.path.join("Audio", "Selection.wav"))

    def update(self, display):
        '''
        Atualiza e renderiza a interface
        '''

        self.surface.fill(self.background_color)

        if self.background is not None:

            self.background.sprites.draw(self.surface)

        for button in self.buttons:

            button.render(self.surface)

        for text in self.texts:

            self.surface.blit(text.get_render(), text.get_position())

        display.blit(self.surface, self.position)

    def check_buttons(self, event):
        '''
        Checa qual botão está sendo pressionado
        '''

        user_interface_event = None

        for button in self.buttons:

            if button.is_pressed(event):

                user_interface_event = button.get_event()
                break

        return user_interface_event


class Button():

    '''
    Define um botão
    '''

    position: tuple  # Posição
    size: tuple  # Tamanho
    event: Event
    key: None
    sprites: pygame.sprite.RenderPlain()  # Sprites

    def __init__(self,
                 alignment,
                 position,
                 size,
                 event,
                 key,
                 screen_size,
                 background,
                 foreground):

        self.position = None
        self.size = size
        self.event = event
        self.key = key
        self.sprites = pygame.sprite.RenderPlain()

        # Calcula a posiçõa com base no alinhamento
        if alignment == Alignment.TOP_LEFT:

            self.position = position
        elif alignment == Alignment.TOP_RIGHT:

            self.position = (screen_size[0] - position[0], position[1])
        else:

            self.position = ((screen_size[0] - size[0]) / 2 + position[0],
                             (screen_size[1] - size[1]) / 2 - position[1])

        self.sprites.add(graphics.RectangleSprite(self.position, size, foreground))
        self.sprites.add(graphics.RectangleSprite((self.position[0] + 10, self.position[1] + 10),
                                                  (size[0] - 20, size[1] - 20),
                                                  background))

    def is_pressed(self, event):
        '''
        Checa se o botão foi clicado
        '''

        is_clicked = False
        key_is_pressed = False

        if event is not None:

            if event.type == pygame.MOUSEBUTTONDOWN:

                is_clicked = event.pos[0] >= self.position[0] and       \
                    event.pos[0] <= self.position[0] + self.size[0] and \
                    event.pos[1] >= self.position[1] and                \
                    event.pos[1] <= self.position[1] + self.size[1]
            elif event.type == pygame.KEYDOWN:

                key_is_pressed = self.key == event.key

        if is_clicked or key_is_pressed:

            return True
        else:

            return False

    def get_event(self):
        '''
        Retorna o evento causado pelo botão
        '''

        return self.event

    def render(self, surface):
        '''
        Renderiza o botão
        '''

        self.sprites.draw(surface)


class Text():

    '''
    Define o elemento de texto
    '''

    size: int  # Tamanho
    position: tuple  # Posição
    font: pygame.font.Font  # Fonte
    text: pygame.font.Font.render  # Superfície renderizada
    color: pygame.color.Color  # Cor
    has_shadow: bool
    shadow_color: pygame.color.Color
    shadow_text: pygame.font.Font.render
    merged_surface: pygame.Surface

    def __init__(self,
                 text,
                 alignment,
                 position,
                 size,
                 color,
                 screen_size,
                 shadow,
                 shadow_color = None):

        self.size = size
        self.position = None
        self.color = pygame.color.Color(color)
        self.font = pygame.font.Font(os.path.join("Fonts", "joystix monospace.ttf"), self.size)
        self.text = self.font.render(text, False, self.color)
        self.has_shadow = shadow
        self.shadow_color = None

        self.merged_surface = pygame.Surface((self.text.get_rect().width,
                                              self.text.get_rect().height),
                                              pygame.SRCALPHA)

        if self.has_shadow:

            self.shadow_color = pygame.color.Color(shadow_color)
            self.shadow_text = self.font.render(text, False, self.shadow_color)
            self.merged_surface.blit(self.shadow_text, (self.size // 8, 0))

        self.merged_surface.blit(self.text, (0, 0))

        # Calcula a posição com base no alinhamento
        if alignment == Alignment.TOP_LEFT:

            self.position = position
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

        if self.has_shadow:

            self.shadow_text = self.font.render(text, False, self.shadow_color)
            self.merged_surface.blit(self.shadow_text, (-10, 0))

        self.merged_surface.blit(self.text, (0, 0))

    def get_render(self):
        '''
        Retorna a superfície do texto
        '''

        return self.merged_surface

    def get_position(self):
        '''
        Retorna a posição
        '''

        return self.position


class Background():

    '''
    Define o plano de fundo com sprites
    '''

    sprites: pygame.sprite.RenderPlain  # Sprites

    def __init__(self, size):

        self.sprites = pygame.sprite.RenderPlain()
        self.sprites.add(graphics.BackgroundSprite((size[0] / 2 - 512, size[1] / 2 - 512),
                                                   (1024, 1024)))


class Bar():

    '''
    Define uma barra
    '''

    position: tuple  # Posição
    sprites: pygame.sprite.RenderPlain  # Sprites

    def __init__(self, alignment, position, size, border_color, color, screen_size):

        self.position = None
        self.size = size
        self.sprites = pygame.sprite.RenderPlain()

        # Define a posição com base no alinhamento
        if alignment == Alignment.TOP_LEFT:

            self.position = position
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
        Atualiza o tamanho da barra com base em um valor de 0 a 100 (percentual).
        '''

        self.sprites.sprites()[1].update(self.position, [int((self.size[0] / 100.0) * value), 35])


class MainMenu(UserInterface):

    '''
    Define o menu.
    '''

    background: Background  # Plano de fundo

    def __init__(self, screen_size, version, background_color):

        super().__init__((0, 0), screen_size, screen_size, background_color)

        # Inicializa o plano de fundo, botões e textos

        self.background = Background(screen_size)

        self.buttons.append(Button(Alignment.CENTER,
                                   (0, 0),
                                   (400, 100),
                                   Event.UI_MODIFY,
                                   pygame.K_RETURN,
                                   screen_size,
                                   (108, 155, 179),
                                   (138, 200, 230)))

        self.buttons.append(Button(Alignment.CENTER,
                                   (0, -200),
                                   (400, 100),
                                   Event.UI_EXIT,
                                   pygame.K_ESCAPE,
                                   screen_size,
                                   (108, 155, 179),
                                   (138, 200, 230)))

        self.texts.append(Text(f"{version}",
                               Alignment.TOP_LEFT,
                               [0, 0],
                               15,
                               (255, 255, 255),
                               screen_size,
                               False))

        self.texts.append(Text("FRANTIC FLYERS",
                               Alignment.CENTER,
                               (0, 200),
                               80,
                               (77, 111, 128),
                               screen_size,
                               True,
                               (138, 200, 230)))

        self.texts.append(Text("JOGAR",
                               Alignment.CENTER,
                               (0, 0),
                               40,
                               (230, 230, 230),
                               screen_size,
                               False))

        self.texts.append(Text("SAIR",
                               Alignment.CENTER,
                               (0, -200),
                               40,
                               (230, 230, 230),
                               screen_size,
                               False))


class ModificationMenu(UserInterface):

    '''
    Define o menu de modificação.
    '''

    background: Background  # Plano de fundo

    def __init__(self, screen_size, background_color):

        super().__init__((0, 0), screen_size, screen_size, background_color)

        # Inicializa o plano de fundo, botões e textos

        self.background = Background(screen_size)

        self.buttons.append(Button(Alignment.TOP_LEFT,
                                   (25, 25),
                                   (100, 100),
                                   Event.UI_RETURN_TO_MENU,
                                   pygame.K_ESCAPE,
                                   screen_size,
                                   (108, 155, 179),
                                   (138, 200, 230)))

        self.buttons.append(Button(Alignment.CENTER,
                                   (0, -200),
                                   (400, 100),
                                   Event.UI_PLAY,
                                   pygame.K_RETURN,
                                   screen_size,
                                   (108, 155, 179),
                                   (138, 200, 230)))

        self.texts.append(Text("MODIFICAR",
                               Alignment.CENTER,
                               (0, 300),
                               80,
                               (77, 111, 128),
                               screen_size,
                               True,
                               (138, 200, 230)))

        self.texts.append(Text('<',
                               Alignment.TOP_LEFT,
                               (50, 40),
                               50,
                               (230, 230, 230),
                               screen_size,
                               False))

        self.texts.append(Text("PONTOS:",
                               Alignment.CENTER,
                               (-400, 200),
                               40,
                               (77, 111, 128),
                               screen_size,
                               True,
                               (138, 200, 230)))

        self.texts.append(Text("XXX",
                               Alignment.CENTER,
                               (-225, 200),
                               40,
                               (77, 111, 128),
                               screen_size,
                               True,
                               (138, 200, 230)))

        self.texts.append(Text("JOGAR",
                               Alignment.CENTER,
                               (0, -200),
                               40,
                               (230, 230, 230),
                               screen_size,
                               False))

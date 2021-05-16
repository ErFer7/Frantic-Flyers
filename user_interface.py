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
    gameplay_interface: None
    pause_interface: None

    def __init__(self, screen_size, version):

        self.user_interface_event = None
        self.main_menu = MainMenu(screen_size, version, (92, 184, 230))
        self.modification_menu = ModificationMenu(screen_size, (92, 184, 230))
        self.gameplay_interface = GameplayInterface(screen_size, (0, 0, 0, 0))
        self.pause_interface = PauseInterface(screen_size, (92, 184, 230))

    def update(self, state, display, events, modification_data, score, life):
        '''
        Atualiza os eventos e gráficos da interface
        '''

        self.user_interface_event = None

        # Atualiza os eventos
        for event in events:

            if state == State.MAIN_MENU:

                self.user_interface_event = self.main_menu.check_buttons(event)
                self.main_menu.render(display)
            elif state == State.MODIFICATION_MENU:

                self.modification_menu.update(modification_data)
                self.user_interface_event = self.modification_menu.check_buttons(event)
                self.modification_menu.render(display)
            elif state == State.GAMEPLAY:

                self.gameplay_interface.update(score, life)
                self.user_interface_event = self.gameplay_interface.check_buttons(event)
                self.gameplay_interface.render(display)
            elif state == State.PAUSE:

                self.user_interface_event = self.pause_interface.check_buttons(event)
                self.pause_interface.render(display)

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
    TOP = 4
    LEFT = 5
    RIGHT = 6
    BOTTOM_LEFT = 7
    BOTTOM_RIGHT = 8
    BOTTOM = 9


class UserInterface():

    '''
    Define a base de uma tela
    '''

    position: tuple  # Posição
    screen_size: tuple  # Tamanho da tela
    texts: dict  # textos
    buttons: dict  # Botões
    bars: dict
    surface: pygame.Surface  # Superfície
    background: None
    background_color: pygame.color.Color

    def __init__(self, position, size, screen_size, background_color):

        self.position = position
        self.screen_size = screen_size
        self.texts = {}
        self.buttons = {}
        self.bars = {}
        self.surface = pygame.Surface(size, pygame.SRCALPHA)
        self.background = None
        self.background_color = pygame.color.Color(background_color)

    def render(self, display):
        '''
        Atualiza e renderiza a interface
        '''

        self.surface.fill(self.background_color)

        if self.background is not None:

            self.background.sprites.draw(self.surface)

        for key in self.buttons:

            self.buttons[key].render(self.surface)

        for key in self.bars:

            self.bars[key].render(self.surface)

        for key in self.texts:

            self.surface.blit(self.texts[key].get_render(), self.texts[key].get_position())

        display.blit(self.surface, self.position)

    def check_buttons(self, event):
        '''
        Checa qual botão está sendo pressionado
        '''

        user_interface_event = None

        for key in self.buttons:

            if self.buttons[key].is_pressed(event):

                user_interface_event = self.buttons[key].get_event()
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

        self.position = UserInterfaceUtillities.calculate_position(alignment,
                                                                   position,
                                                                   size,
                                                                   screen_size)

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

                is_clicked = self.sprites.sprites()[0].rect.collidepoint(event.pos)
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

        self.position = UserInterfaceUtillities.calculate_position(alignment,
                                                                   position,
                                                                   (self.text.get_rect().width,
                                                                   self.text.get_rect().height),
                                                                   screen_size)

    def update(self, text):
        '''
        Atualiza o texto
        '''

        self.merged_surface.fill((0, 0, 0, 0))

        self.text = self.font.render(text, False, self.color)

        if self.has_shadow:

            self.shadow_text = self.font.render(text, False, self.shadow_color)
            self.merged_surface.blit(self.shadow_text, (self.size // 8, 0))

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
    internal_bar_position: tuple
    size: tuple
    internal_bar_size: tuple
    sprites: pygame.sprite.RenderPlain  # Sprites

    def __init__(self, alignment, position, size, border_color, color, screen_size):

        self.position = None
        self.internal_bar_position = None
        self.size = size
        self.internal_bar_size = (size[0] - 10, size[1] - 10)
        self.sprites = pygame.sprite.RenderPlain()

        self.position = UserInterfaceUtillities.calculate_position(alignment,
                                                                   position,
                                                                   size,
                                                                   screen_size)

        self.internal_bar_position = (self.position[0] + 5,
                                      self.position[1] + 5)

        self.sprites.add(graphics.RectangleSprite(self.position,
                                                  self.size,
                                                  border_color))
        self.sprites.add(graphics.RectangleSprite(self.internal_bar_position,
                                                  self.internal_bar_size,
                                                  color))

    def update(self, value):
        '''
        Atualiza o tamanho da barra com base em um valor de 0 a 100 (percentual).
        '''

        self.sprites.sprites()[1].update(self.internal_bar_position,
                                         (int((self.internal_bar_size[0] / 100.0) * value),
                                          self.internal_bar_size[1]))

    def render(self, surface):
        '''
        Renderiza a barra
        '''

        self.sprites.draw(surface)


class UserInterfaceUtillities():

    '''
    Utilidades do sistema de interface.
    '''

    @staticmethod
    def calculate_position(alignment, position, size, screen_size):
        '''
        Calcula a posição com base no alinhamento.
        '''

        calculated_position = ()

        if alignment ==Alignment.CENTER:

            calculated_position = ((screen_size[0] - size[0]) / 2 + position[0],
                                  (screen_size[1] - size[1]) / 2 - position[1])
        elif alignment == Alignment.TOP_LEFT:

            calculated_position = position
        elif alignment == Alignment.TOP_RIGHT:

            calculated_position = (screen_size[0] - position[0], position[1])
        elif alignment == Alignment.TOP:

            calculated_position = ((screen_size[0] - size[0]) / 2 + position[0], position[1])
        elif alignment == Alignment.LEFT:

            calculated_position = (position[0], (screen_size[1] - size[1]) / 2 - position[1])
        elif alignment == Alignment.RIGHT:

            calculated_position = (screen_size[0] - position[0],
                                  (screen_size[1] - size[1]) / 2 - position[1])
        elif alignment == Alignment.BOTTOM_LEFT:

            calculated_position = (position[0],
                                  (screen_size[1] - size[1]) - position[1])
        elif alignment == Alignment.BOTTOM_RIGHT:

            calculated_position = (screen_size[0] - position[0],
                                  (screen_size[1] - size[1]) - position[1])
        else:

            calculated_position = ((screen_size[0] - size[0]) / 2 + position[0],
                                  (screen_size[1] - size[1]) - position[1])

        return calculated_position


class MainMenu(UserInterface):

    '''
    Define o menu.
    '''

    background: Background  # Plano de fundo

    def __init__(self, screen_size, version, background_color):

        super().__init__((0, 0), screen_size, screen_size, background_color)

        # Inicializa o plano de fundo, botões e textos

        self.background = Background(screen_size)

        self.buttons["Modify"] = Button(Alignment.CENTER,
                                        (0, 0),
                                        (400, 100),
                                        Event.UI_MODIFY,
                                        pygame.K_RETURN,
                                        screen_size,
                                        (108, 155, 179),
                                        (138, 200, 230))

        self.buttons["Quit"] = Button(Alignment.CENTER,
                                      (0, -200),
                                      (400, 100),
                                      Event.UI_EXIT,
                                      pygame.K_ESCAPE,
                                      screen_size,
                                      (108, 155, 179),
                                      (138, 200, 230))

        self.texts["Version"] = Text(f"{version}",
                                     Alignment.TOP_LEFT,
                                     [0, 0],
                                     15,
                                     (255, 255, 255),
                                     screen_size,
                                     False)

        self.texts["Title"] = Text("FRANTIC FLYERS",
                                   Alignment.TOP,
                                   (0, 100),
                                   80,
                                   (77, 111, 128),
                                   screen_size,
                                   True,
                                   (138, 200, 230))

        self.texts["Modify"] = Text("JOGAR",
                                    Alignment.CENTER,
                                    (0, 0),
                                    40,
                                    (230, 230, 230),
                                    screen_size,
                                    False)

        self.texts["Quit"] = Text("SAIR",
                                  Alignment.CENTER,
                                  (0, -200),
                                  40,
                                  (230, 230, 230),
                                  screen_size,
                                  False)


class ModificationMenu(UserInterface):

    '''
    Define o menu de modificação.
    '''

    background: Background  # Plano de fundo

    def __init__(self, screen_size, background_color):

        super().__init__((0, 0), screen_size, screen_size, background_color)

        # Inicializa o plano de fundo, botões e textos

        self.background = Background(screen_size)

        self.buttons["Return"] = Button(Alignment.TOP_LEFT,
                                        (25, 25),
                                        (100, 100),
                                        Event.UI_RETURN_TO_MENU,
                                        pygame.K_ESCAPE,
                                        screen_size,
                                        (108, 155, 179),
                                        (138, 200, 230))

        self.buttons["Play"] = Button(Alignment.BOTTOM,
                                      (0, 100),
                                      (400, 100),
                                      Event.UI_PLAY,
                                      pygame.K_RETURN,
                                      screen_size,
                                      (108, 155, 179),
                                      (138, 200, 230))

        self.texts["Title"] = Text("MODIFICAR",
                                    Alignment.TOP,
                                    (0, 25),
                                    80,
                                    (77, 111, 128),
                                    screen_size,
                                    True,
                                    (138, 200, 230))

        self.texts["Return"] = Text('<',
                                    Alignment.TOP_LEFT,
                                    (50, 40),
                                    50,
                                    (230, 230, 230),
                                    screen_size,
                                    False)

        self.texts["Points"] = Text("PONTOS:",
                                    Alignment.LEFT,
                                    (100, 200),
                                    40,
                                    (77, 111, 128),
                                    screen_size,
                                    True,
                                    (138, 200, 230))

        self.texts["Point Number"] = Text("XXX",
                                          Alignment.LEFT,
                                          (350, 200),
                                          40,
                                          (77, 111, 128),
                                          screen_size,
                                          False)

        self.texts["Velocity"] = Text("VELOCIDADE:",
                                      Alignment.LEFT,
                                      (100, 125),
                                      40,
                                      (77, 111, 128),
                                      screen_size,
                                      True,
                                      (138, 200, 230))

        self.texts["Velocity Number"] = Text("XXX",
                                             Alignment.LEFT,
                                             (685, 125),
                                             30,
                                             (230, 230, 230),
                                             screen_size,
                                             False)

        self.bars["Velocity"] = Bar(Alignment.LEFT,
                                    (475, 120),
                                    (500, 50),
                                    (108, 155, 179),
                                    (138, 200, 230),
                                    screen_size)

        self.buttons["Reduce Velocity"] = Button(Alignment.RIGHT,
                                                 (350, 125),
                                                 (100, 50),
                                                 Event.UI_REDUCE_VELOCITY,
                                                 pygame.K_y,
                                                 screen_size,
                                                 (108, 155, 179),
                                                 (138, 200, 230))

        self.texts["Velocity Minus"] = Text('-',
                                            Alignment.RIGHT,
                                            (317, 125),
                                            40,
                                            (230, 230, 230),
                                            screen_size,
                                            False)

        self.buttons["Increase Velocity"] = Button(Alignment.RIGHT,
                                                   (200, 125),
                                                   (100, 50),
                                                   Event.UI_INCREASE_VELOCITY,
                                                   pygame.K_h,
                                                   screen_size,
                                                   (108, 155, 179),
                                                   (138, 200, 230))

        self.texts["Velocity Plus"] = Text('+',
                                            Alignment.RIGHT,
                                            (167, 125),
                                            40,
                                            (230, 230, 230),
                                            screen_size,
                                            False)

        self.texts["Damage"] = Text("DANO:",
                                    Alignment.LEFT,
                                    (100, 50),
                                    40,
                                    (77, 111, 128),
                                    screen_size,
                                    True,
                                    (138, 200, 230))

        self.texts["Damage Number"] = Text("XXX",
                                           Alignment.LEFT,
                                           (685, 50),
                                           30,
                                           (230, 230, 230),
                                           screen_size,
                                           False)

        self.bars["Damage"] = Bar(Alignment.LEFT,
                                  (475, 45),
                                  (500, 50),
                                  (108, 155, 179),
                                  (138, 200, 230),
                                  screen_size)

        self.buttons["Reduce Damage"] = Button(Alignment.RIGHT,
                                               (350, 50),
                                               (100, 50),
                                               Event.UI_REDUCE_DAMAGE,
                                               pygame.K_u,
                                               screen_size,
                                               (108, 155, 179),
                                               (138, 200, 230))

        self.texts["Damage Minus"] = Text('-',
                                          Alignment.RIGHT,
                                          (317, 50),
                                          40,
                                          (230, 230, 230),
                                          screen_size,
                                          False)

        self.buttons["Increase Damage"] = Button(Alignment.RIGHT,
                                                 (200, 50),
                                                 (100, 50),
                                                 Event.UI_INCREASE_DAMAGE,
                                                 pygame.K_j,
                                                 screen_size,
                                                 (108, 155, 179),
                                                 (138, 200, 230))

        self.texts["Damage Plus"] = Text('+',
                                         Alignment.RIGHT,
                                         (167, 50),
                                         40,
                                         (230, 230, 230),
                                         screen_size,
                                         False)

        self.texts["Firerate"] = Text("CADÊNCIA:",
                                       Alignment.LEFT,
                                       (100, -25),
                                       40,
                                       (77, 111, 128),
                                       screen_size,
                                       True,
                                       (138, 200, 230))

        self.texts["Firerate Number"] = Text("XXX",
                                             Alignment.LEFT,
                                             (685, -25),
                                             30,
                                             (230, 230, 230),
                                             screen_size,
                                             False)

        self.bars["Firerate"] = Bar(Alignment.LEFT,
                                     (475, -30),
                                     (500, 50),
                                     (108, 155, 179),
                                     (138, 200, 230),
                                     screen_size)

        self.buttons["Reduce Firerate"] = Button(Alignment.RIGHT,
                                                 (350, -25),
                                                 (100, 50),
                                                 Event.UI_REDUCE_FIRERATE,
                                                 pygame.K_i,
                                                 screen_size,
                                                 (108, 155, 179),
                                                 (138, 200, 230))

        self.texts["Firerate Minus"] = Text('-',
                                            Alignment.RIGHT,
                                            (317, -25),
                                            40,
                                            (230, 230, 230),
                                            screen_size,
                                            False)

        self.buttons["Increase Firerate"] = Button(Alignment.RIGHT,
                                                   (200, -25),
                                                   (100, 50),
                                                   Event.UI_INCREASE_FIRERATE,
                                                   pygame.K_k,
                                                   screen_size,
                                                   (108, 155, 179),
                                                   (138, 200, 230))

        self.texts["Firerate Plus"] = Text('+',
                                           Alignment.RIGHT,
                                           (167, -25),
                                           40,
                                           (230, 230, 230),
                                           screen_size,
                                           False)

        self.texts["Armor"] = Text("ARMADURA:",
                                   Alignment.LEFT,
                                   (100, -100),
                                   40,
                                   (77, 111, 128),
                                   screen_size,
                                   True,
                                   (138, 200, 230))

        self.texts["Armor Number"] = Text("XXX",
                                          Alignment.LEFT,
                                          (685, -100),
                                          30,
                                          (230, 230, 230),
                                          screen_size,
                                          False)

        self.bars["Armor"] = Bar(Alignment.LEFT,
                                 (475, -105),
                                 (500, 50),
                                 (108, 155, 179),
                                 (138, 200, 230),
                                 screen_size)

        self.buttons["Reduce Armor"] = Button(Alignment.RIGHT,
                                              (350, -100),
                                              (100, 50),
                                              Event.UI_REDUCE_ARMOR,
                                              pygame.K_o,
                                              screen_size,
                                              (108, 155, 179),
                                              (138, 200, 230))

        self.texts["Armor Minus"] = Text('-',
                                         Alignment.RIGHT,
                                         (317, -100),
                                         40,
                                         (230, 230, 230),
                                         screen_size,
                                         False)

        self.buttons["Increase Armor"] = Button(Alignment.RIGHT,
                                                (200, -100),
                                                (100, 50),
                                                Event.UI_INCREASE_ARMOR,
                                                pygame.K_l,
                                                screen_size,
                                                (108, 155, 179),
                                                (138, 200, 230))

        self.texts["Armor Plus"] = Text('+',
                                        Alignment.RIGHT,
                                        (167, -100),
                                        40,
                                        (230, 230, 230),
                                        screen_size,
                                        False)

        self.texts["Play"] = Text("JOGAR",
                                  Alignment.BOTTOM,
                                  (0, 130),
                                  40,
                                  (230, 230, 230),
                                  screen_size,
                                  False)

    def update(self, modification_data):
        '''
        Atualiza os dados dos componentes da interface.
        '''

        self.texts["Point Number"].update(str(modification_data["Modification Points"]))
        self.texts["Velocity Number"].update(str(modification_data["Velocity"]))
        self.bars["Velocity"].update(modification_data["Velocity"])
        self.texts["Damage Number"].update(str(modification_data["Damage"]))
        self.bars["Damage"].update(modification_data["Damage"])
        self.texts["Firerate Number"].update(str(modification_data["Firerate"]))
        self.bars["Firerate"].update(modification_data["Firerate"])
        self.texts["Armor Number"].update(str(modification_data["Armor"]))
        self.bars["Armor"].update(modification_data["Armor"])


class GameplayInterface(UserInterface):

    '''
    Interface do gameplay.
    '''

    def __init__(self, screen_size, background_color):

        super().__init__((0, 0), screen_size, screen_size, background_color)

        self.bars["Life"] = Bar(Alignment.BOTTOM_LEFT,
                                (25, 25),
                                (400, 50),
                                (40, 0, 0),
                                (100, 0, 0),
                                screen_size)

        self.texts["Life"] = Text("XXX",
                                  Alignment.BOTTOM_LEFT,
                                  (185, 35),
                                  30,
                                  (230, 230, 230),
                                  screen_size,
                                  False)

        self.texts["Score"] = Text("SCORE: ",
                                    Alignment.BOTTOM_LEFT,
                                    (25, 80),
                                    30,
                                    (230, 230, 230),
                                    screen_size,
                                    True,
                                    (130, 130, 130))

        self.texts["Score Number"] = Text("XXXXXXX",
                                          Alignment.BOTTOM_LEFT,
                                          (175, 80),
                                          30,
                                          (230, 230, 230),
                                          screen_size,
                                          True,
                                          (130, 130, 130))

        self.buttons["Pause"] = Button(Alignment.BOTTOM_RIGHT,
                                       (125, 25),
                                       (100, 100),
                                       Event.UI_PAUSE,
                                       pygame.K_ESCAPE,
                                       screen_size,
                                       (108, 155, 179),
                                       (138, 200, 230))

        self.texts["Pause"] = Text("II",
                                    Alignment.BOTTOM_RIGHT,
                                    (116, 50),
                                    50,
                                    (230, 230, 230),
                                    screen_size,
                                    False)

    def update(self, score, life):
        '''
        Atualiza a interface de gameplay.
        '''

        self.texts["Score Number"].update(f"{score:07}")
        self.bars["Life"].update(life)
        self.texts["Life"].update(str(life))

class PauseInterface(UserInterface):

    '''
    Interface da tela de pausa.
    '''

    def __init__(self, screen_size, background_color):

        super().__init__((0, 0), screen_size, screen_size, background_color)

        self.background = Background(screen_size)

        self.texts["Title"] = Text("PAUSADO",
                                    Alignment.TOP,
                                    (0, 25),
                                    80,
                                    (77, 111, 128),
                                    screen_size,
                                    True,
                                    (138, 200, 230))

        self.buttons["Resume"] = Button(Alignment.CENTER,
                                        (0, 100),
                                        (400, 100),
                                        Event.UI_RESUME,
                                        pygame.K_ESCAPE,
                                        screen_size,
                                        (108, 155, 179),
                                        (138, 200, 230))

        self.texts["Resume"] = Text("CONTINUAR",
                                  Alignment.CENTER,
                                  (0, 100),
                                  40,
                                  (230, 230, 230),
                                  screen_size,
                                  False)

        self.buttons["Restart"] = Button(Alignment.CENTER,
                                         (0, -50),
                                         (400, 100),
                                         Event.UI_RESTART,
                                         pygame.K_r,
                                         screen_size,
                                         (108, 155, 179),
                                         (138, 200, 230))

        self.texts["Restart"] = Text("REINICIAR",
                                      Alignment.CENTER,
                                      (0, -50),
                                      40,
                                      (230, 230, 230),
                                      screen_size,
                                      False)

        self.buttons["End Gameplay"] = Button(Alignment.CENTER,
                                              (0, -200),
                                              (400, 100),
                                              Event.GP_GAMEOVER,
                                              pygame.K_ESCAPE,
                                              screen_size,
                                              (108, 155, 179),
                                              (138, 200, 230))

        self.texts["End Gameplay"] = Text("ENCERRAR",
                                          Alignment.CENTER,
                                          (0, -200),
                                          40,
                                          (230, 230, 230),
                                          screen_size,
                                          False)

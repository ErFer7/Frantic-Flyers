# -*- coding: utf-8 -*-

'''
Módulo para as entidades.
'''

import os

from random import randint
from enum import Enum

import pygame

from graphics import CustomSprite


class EntityManager():

    '''
    Gerencia as entidades
    '''

    player_score: int
    screen_size: tuple
    player: None
    enemies: list
    bullets: list
    clouds: list
    inactive_enemies: list  # Usado no pooling
    inactive_bullets: list  # Usado no pooling

    def __init__(self, screen_size):

        self.player_score = 0
        self.screen_size = screen_size
        self.player = Player((self.screen_size[0] / 2, self.screen_size[1] / 2),
                             100,
                             100.0,
                             1.0,
                             BulletType.SIMPLE,
                             1.0,
                             '',
                             '',
                             '',
                             (300, 300),
                             os.path.join("Sprites", "Planes", "UK_Spitfire.png"))
        self.enemies = []
        self.bullets = []
        self.clouds = []
        self.inactive_enemies = []
        self.inactive_bullets = []

        self.generate_clouds(10)

    def update_player_modifiers(self, modifiers):
        '''
        Atualiza os modificadores do jogador.
        '''

        self.player.update_modifiers(modifiers)

    def get_player_life(self):
        '''
        Retorna a vida do jogador (método de ligação).
        '''

        return self.player.get_life()

    def get_player_score(self):
        '''
        Retorna a pontuação do jogador.
        '''

        return self.player_score

    def get_entities(self):
        '''
        Retorna uma lista de entidades que serão usadas na física.
        '''

        return self.clouds + self.bullets + self.enemies + [self.player]

    def generate_clouds(self, cloud_count):
        '''
        Gera o cenário do jogo.
        '''

        for _ in range(cloud_count):

            random_position = (randint(0, self.screen_size[0]),
                               randint(-self.screen_size[1], self.screen_size[1]))
            random_cloud_index = randint(0, 4)
            path = os.path.join("Sprites", "Scenery", f"Cloud {random_cloud_index}.png")
            image = pygame.image.load(path)
            size = (image.get_width() * 3, image.get_height() * 3)
            speed = (256.0 / image.get_width()) * 50.0

            self.clouds.append(Cloud(random_position,
                                     size,
                                     path,
                                     speed))

            self.clouds.sort(key=lambda cloud: cloud.size[0], reverse=True)

    def enemy_generator(self):
        '''
        Gera os inimigos.
        '''

        # Podemos aproveitar pra usar um padrão de fábrica aqui

        #Enemies.append(Enemy(posição, posição, vida, velocidade, dano, bala, freq-bala, estado, tiro-som, dano-som))

    def update(self, events):
        '''
        Atualiza as entidades e seus comportamentos.
        '''

        self.player.behaviour(events, self.screen_size)

        for cloud in self.clouds:

            cloud.behaviour(self.screen_size)


class BulletType(Enum):

    '''
    Tipos de bala.
    '''

    SIMPLE = 1
    DOUBLE = 2
    TRIPLE = 3
    TRACKING = 4


class Entity():

    '''
    Entidade física.
    '''

    active: bool
    position: list  # O sistema de coordenadas tem o ponto (0, 0) no topo da tela. eixo y invertido
    velocity: list  # Para cima: (0, -1), para baixo: (0, 1)
    size: tuple
    hitbox: pygame.Rect
    sprite: CustomSprite

    def __init__(self, position, size, sprite_path, collides=True):

        self.active = True
        self.position = list(position)
        self.velocity = [0, 0]
        self.size = size
        self.hitbox = None

        if collides:

            self.hitbox = pygame.Rect(self.position[0] - size[0] / 2,
                                      self.position[1] - size[1] / 2,
                                      size[0],
                                      size[1])

        self.sprite = CustomSprite((self.position[0] - size[0] / 2,
                                    self.position[1] - size[1] / 2),
                                   size,
                                   sprite_path)

    def get_position(self):
        '''
        Retorna a posição.
        '''

        return tuple(self.position)

    def get_velocity(self):
        '''
        Retorna a velocidade.
        '''

        return tuple(self.velocity)

    def set_position(self, position):
        '''
        Define a posição.
        '''

        self.position = list(position)
        self.sprite.update((self.position[0] - self.size[0] / 2,
                            self.position[1] - self.size[1] / 2))

    def set_velocity(self, velocity):
        '''
        Define a velocidade.
        '''

        self.velocity = list(velocity)

    def get_sprite(self):
        '''
        Retorna o sprite da entidade.
        '''

        return self.sprite


class Aircraft(Entity):

    '''
    Super Classe.
    '''

    direction: list  # Armazena a direção, assim conservamos a velocidade
    life: int
    max_life: int
    speed: float  # Pixels por segundo
    damage: float
    bullet_type: BulletType
    firerate: float
    sprites: pygame.sprite.RenderPlain
    attack_sound: pygame.mixer.Sound
    damage_sound: pygame.mixer.Sound
    idle_sound: pygame.mixer.Sound

    def __init__(self,
                 position,
                 max_life,
                 speed,
                 damage,
                 bullet_type,
                 firerate,
                 attack_sound,
                 damage_sound,
                 idle_sound,
                 size,
                 sprite_path):

        super().__init__(position, size, sprite_path)

        self.direction = [0, 0]
        self.life = max_life  # Todas as entidades são instanciadas com a vida cheia
        self.max_life = max_life
        self.speed = speed
        self.damage = damage
        # integer que diz como o tiro sai do avião, vai de 0 até um número
        self.bullet_type = bullet_type
        self.firerate = firerate  # cadencia de tiros
        # self.attack_sound = pygame.mixer.Sound() --som do tiro
        # self.damage_sound = pygame.mixer.Sound() --som quando a nave leva dano


class Player(Aircraft):

    '''
    Jogador.
    '''

    velocity_modifier: int
    damage_modifier: int
    firerate_modifier: int
    armor_modifier: int

    def __init__(self,
                 position,
                 max_life,
                 speed,
                 damage,
                 bullet_type,
                 firerate,
                 attack_sound,
                 damage_sound,
                 idle_sound,
                 size,
                 sprite_path):

        super().__init__(position,
                         max_life,
                         speed,
                         damage,
                         bullet_type,
                         firerate,
                         attack_sound,
                         damage_sound,
                         idle_sound,
                         size,
                         sprite_path)

        self.velocity_modifier = 0
        self.damage_modifier = 0
        self.firerate_modifier = 0
        self.armor_modifier = 0

    def behaviour(self, events, screen_size):
        '''
        Definição do comportamento do jogador.
        '''

        for event in events:

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_a:

                    self.direction[0] = -1
                elif event.key == pygame.K_d and self.position[0] < screen_size[0]:

                    self.direction[0] = 1

                if event.key == pygame.K_s and self.position[1] < screen_size[1]:

                    self.direction[1] = 1
                elif event.key == pygame.K_w and self.position[1] > 0:

                    self.direction[1] = -1
            elif event.type == pygame.KEYUP:  # Caso uma tecla seja solta

                if event.key == pygame.K_a or event.key == pygame.K_d:  # Teclas horizontais

                    self.direction[0] = 0

                if event.key == pygame.K_s or event.key == pygame.K_w:  # Teclas verticais

                    self.direction[1] = 0

            if self.direction[0] != 0:

                self.velocity[0] = self.direction[0] * self.speed * self.velocity_modifier * 0.05

            if self.direction[1] != 0:

                self.velocity[1] = self.direction[1] * self.speed * self.velocity_modifier * 0.05

        if self.position[0] <= 0:

            self.direction[0] = 0
            self.velocity[0] = self.speed
        elif self.position[0] >= screen_size[0]:

            self.direction[0] = 0
            self.velocity[0] = -self.speed

        if self.position[1] <= 0:

            self.direction[1] = 0
            self.velocity[1] = self.speed
        elif self.position[1] >= screen_size[1]:

            self.direction[1] = 0
            self.velocity[1] = -self.speed

    def get_life(self):
        '''
        Retorna a vida do jogador.
        '''

        return self.life

    def update_modifiers(self, modifiers):
        '''
        Atualiza os modificadores.
        '''

        self.velocity_modifier = modifiers["Velocity"]
        self.damage_modifier = modifiers["Damage"]
        self.firerate_modifier = modifiers["Firerate"]
        self.armor_modifier = modifiers["Armor"]

class Enemy(Aircraft):

    '''
    Inimigos.
    '''

    def __init__(self,
                 position,
                 max_life,
                 speed,
                 damage,
                 bullet_type,
                 firerate,
                 attack_sound,
                 damage_sound,
                 idle_sound,
                 size,
                 sprite_path):

        super().__init__(position,
                         max_life,
                         speed,
                         damage,
                         bullet_type,
                         firerate,
                         attack_sound,
                         damage_sound,
                         idle_sound,
                         size,
                         sprite_path)

        # Demais definições aqui

    def behaviour(self):
        '''
        Definição do comportamento do inimigo.
        '''


class Bullet(Entity):

    '''
    Bala.
    '''


class Cloud(Entity):

    '''
    Nuvem.
    '''

    constant_speed: float

    def __init__(self, position, size, sprite_path, constant_speed):

        super().__init__(position, size, sprite_path, False)

        self.constant_speed = constant_speed

    def behaviour(self, screen_size):
        '''
        Comportamento da núvem.
        '''

        self.velocity[1] = self.constant_speed

        if self.position[1] > screen_size[1] * 1.5:

            self.set_position((randint(0, screen_size[0]),
                               randint(-screen_size[1], -screen_size[1] // 2)))

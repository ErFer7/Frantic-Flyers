# -*- coding: utf-8 -*-

'''
Módulo para as entidades.
'''

import os

import pygame

from graphics import CustomSprite

class EntityManager():

    '''
    Gerencia as entidades
    '''

    player_life: int
    player_score: int
    player: None
    enemies: list
    bullets: list
    scenery: list
    inactive_enemies: list # Usado no pooling
    inactive_bullets: list # Usado no pooling

    def __init__(self, screen_size):

        self.player_life = 0 # Depois vamos pegar a vida do jogador de um jeito melhor
        self.player_score = 0
        self.player = Player((screen_size[0] / 2, screen_size[1] / 2),
                             100,
                             100.0,
                             1.0,
                             0,
                             1.0,
                             '',
                             '',
                             '',
                             (300, 300),
                             os.path.join("Sprites", "Planes", "GER_bf109.png"))
        self.enemies = []
        self.bullets = []
        self.scenery = []
        self.inactive_enemies = []
        self.inactive_bullets = []

    def get_player_life(self):
        '''
        Retorna a vida do jogador
        '''

        return self.player_life

    def get_player_score(self):
        '''
        Retorna a pontuação do jogador
        '''

        return self.player_score

    def get_entities(self):
        '''
        Retorna uma lista de entidades que serão usadas na física
        '''

        return [self.player] + self.enemies + self.bullets + self.scenery

    def scenery_generator(self):
        '''
        Gera o cenário do jogo
        '''

    def enemy_generator(self):
        '''
        Gera os inimigos
        '''

        # Podemos aproveitar pra usar um padrão de fábrica aqui

        #Enemies.append(Enemy(posição, posição, vida, velocidade, dano, bala, freq-bala, estado, tiro-som, dano-som))

    def update(self, events):
        '''
        Atualiza as entidades e seus comportamentos
        '''

        self.player.behaviour(events)


class Entity():

    '''
    Entidade física.
    '''

    active: bool
    position: list # O sistema de coordenadas tem o ponto (0, 0) no topo da tela. eixo y invertido
    velocity: list # Para cima: (0, -1), para baixo: (0, 1)
    size: tuple
    hitbox: pygame.Rect
    sprite: CustomSprite

    def __init__(self, position, size, sprite_path, collides = True):

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
        Retorna o sprite da entidade
        '''

        return self.sprite

class Aircraft(Entity):

    '''
    Super Classe
    '''

    direction: list # Armazena a direção, assim conservamos a velocidade
    life: int
    max_life: int
    speed: float # Pixels por segundo
    damage: float
    bullet_type: int # Pode ser um enum também
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
        self.life = max_life # Todas as entidades são instanciadas com a vida cheia
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
    Jogador
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

    def behaviour(self, events):
        '''
        Definição do comportamento do jogador
        '''

        for event in events:

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_a:  # Tecla "A". Movimento para a esquerda

                    self.direction[0] = -1
                elif event.key == pygame.K_d:  # Tecla "D". Movimento para a direita

                    self.direction[0] = 1

                if event.key == pygame.K_s:  # Tecla "S". Movimento para baixo

                    self.direction[1] = 1
                elif event.key == pygame.K_w:  # Tecla "W". Movimento para cima

                    self.direction[1] = -1
            elif event.type == pygame.KEYUP:  # Caso uma tecla seja solta

                if event.key == pygame.K_a or event.key == pygame.K_d:  # Teclas horizontais

                    self.direction[0] = 0

                if event.key == pygame.K_s or event.key == pygame.K_w:  # Teclas verticais

                    self.direction[1] = 0

            if self.direction[0] != 0:

                self.velocity[0] = self.direction[0] * self.speed

            if self.direction[1] != 0:

                self.velocity[1] = self.direction[1] * self.speed

class Enemy(Aircraft):

    '''
    Inimigos
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
        Definição do comportamento do inimigo
        '''

class Bullet(Entity):

    '''
    Bala
    '''

class SceneryEntity(Entity):

    '''
    Entidade do cenário.
    '''

    def __init__(self, position, size, sprite_path):

        super().__init__(position, size, sprite_path, False)

# -*- coding: utf-8 -*-

'''
Módulo para as entidades.
'''

import os

import pygame

class EntityManager():

    '''
    Gerencia as entidades
    '''

    player_life: int
    player_score: int
    player: None
    enemies: list
    bullets: list
    inactive_enemies: list # Usado no pooling
    inactive_bullets: list # Usado no pooling

    def __init__(self):

        self.player_life = 0 # Depois vamos pegar a vida do jogador de um jeito melhor
        self.player_score = 0
        self.player = Player((0, 0), 100, 1.0, 1.0, 0, 1.0, '', '', '')
        self.enemies = []
        self.bullets = []
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

    def enemy_generator(self):
        '''
        Gera os inimigos
        '''

        # Podemos aproveitar pra usar um padrão de fábrica aqui

        #Enemies.append(Enemy(posição, posição, vida, velocidade, dano, bala, freq-bala, estado, tiro-som, dano-som))

    def update(self):
        '''
        Atualiza as entidades e seus comportamentos
        '''


class Entity():

    '''
    Entidade física.
    '''

    # Vamos precisar de uma classe desse jeito por causa das balas e outros objetos físicos

    active: bool
    position: list
    velocity: list
    hitbox: pygame.Rect # A hitbox pode ser o próprio sprite então temos que ver isso
    sprites: pygame.sprite.RenderPlain

    def __init__(self, position):

        self.active = True
        self.position = list(position)
        self.velocity = [0, 0]
        self.hitbox = None # Ainda vou ver melhor
        self.sprites = pygame.sprite.RenderPlain()

class Aircraft(Entity):

    '''
    Super Classe
    '''

    life: int
    max_life: int
    speed: float
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
                 idle_sound):

        super().__init__(position)

        self.life = max_life # Todas as entidades são instanciadas com a vida cheia
        self.max_life = max_life
        self.speed = speed
        self.damage = damage
        # integer que diz como o tiro sai do avião, vai de 0 até um número
        self.bullet_type = bullet_type
        self.firerate = firerate  # cadencia de tiros
        self.sprites = pygame.sprite.RenderPlain()
        # self.attack_sound = pygame.mixer.Sound() --som do tiro
        # self.damage_sound = pygame.mixer.Sound() --som quando a nave leva dano

    def behaviour(self):
        '''
        Comportamento da aeronave.
        '''


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
                 idle_sound):

        super().__init__(position,
                         max_life,
                         speed,
                         damage,
                         bullet_type,
                         firerate,
                         attack_sound,
                         damage_sound,
                         idle_sound)

        # Demais definições aqui

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
                 idle_sound):

        super().__init__(position,
                         max_life,
                         speed,
                         damage,
                         bullet_type,
                         firerate,
                         attack_sound,
                         damage_sound,
                         idle_sound)

        # Demais definições aqui

class Bullet(Entity):

    '''
    Bala
    '''

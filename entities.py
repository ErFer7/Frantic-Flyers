# -*- coding: utf-8 -*-

'''
Módulo para as entidades.
'''

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
        #self.player = Player(posição, vida, velocidade, dano, bala, freq-bala, estado, tiro-som, dano-som)
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

    def __init__(self, position, life, speed, damage, bullet_type, bullet_frequency, state, attack_sound, damage_sound):

        super().__init__(position)

        self.life = life
        self.speed = speed
        self.damage = damage
        self.bullet_type = bullet_type  # integer que diz como o tiro sai do avião, vai de 0 até um número
        self.bullet_frequency = bullet_frequency  # cadencia de tiros
        #self.state = EntityState()
        #self.sprites = pygame.sprite.RenderPlain()
        # self.attack_sound = pygame.mixer.Sound() --som do tiro
        # self.damage_sound = pygame.mixer.Sound() --som quando a nave leva dano


class Player(Aircraft):

    '''
    Jogador
    '''

    def __init__(self, position, life, speed, damage, bullet_type, bullet_frequency, state, attack_sound, damage_sound):
        Aircraft.__init__(self, position, life, speed, damage,
                          bullet_type, bullet_frequency, state, attack_sound, damage_sound)
        self.max_life = 100


class Enemy(Aircraft):

    '''
    Inimigos
    '''

    def __init__(self, position, life, speed, damage, bullet_type, bullet_frequency, state, attack_sound, damage_sound):
        Aircraft.__init__(self, position, life, speed, damage,
                          bullet_type, bullet_frequency, state, attack_sound, damage_sound)

class Bullet(Entity):

    '''
    Bala
    '''

# -*- coding: utf-8 -*-

'''
Módulo para as entidades.
'''


class EntityManager():

    '''
    Gerencia as entidades
    '''

    def __init__(self):
        #self.You = Player(posição, posição, vida, velocidade, dano, bala, freq-bala, estado, tiro-som, dano-som)
        #self.Enemies = []
        # self.Enemies.enemy_generator()
        return

    def enemy_generator(self):
        #Enemies.append(Enemy(posição, posição, vida, velocidade, dano, bala, freq-bala, estado, tiro-som, dano-som))
        return

    def update_entities(self):
        '''
        Atualiza as entidades e seus comportamentos
        '''


class Aircraft():
    '''
    Super Classe
    '''

    def __init__(self, positionX, positionY, life, speed, damage, bullet_type, bullet_frequency, state, attack_sound, damage_sound):
        self.position = [positionX, positionY]
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

    def __init__(self, positionX, positionY, life, speed, damage, bullet_type, bullet_frequency, state, attack_sound, damage_sound):
        Aircraft.__init__(self, positionX, positionY, life, speed, damage,
                          bullet_type, bullet_frequency, state, attack_sound, damage_sound)
        self.max_life = 100


class Enemy(Aircraft):
    '''
    Inimigos
    '''

    def __init__(self, positionX, positionY, life, speed, damage, bullet_type, bullet_frequency, state, attack_sound, damage_sound):
        Aircraft.__init__(self, positionX, positionY, life, speed, damage,
                          bullet_type, bullet_frequency, state, attack_sound, damage_sound)

# -*- coding: utf-8 -*-

'''
Módulo para as entidades.
'''

import os

from random import choice, randint
from enum import Enum
from math import sqrt

import pygame

from graphics import CustomSprite, CustomAnimatedSprite
from physics import Hitbox
from states import Event, State


class EntityManager():

    '''
    Gerencia as entidades
    '''

    score: int  # Pontuação
    screen_size: tuple  # Tamanho da tela
    player: None  # Jogador
    enemies: list  # Inimigos
    bullets: list  # Balas
    clouds: list  # Nuvems
    animations: list  # Animações
    inactive_bullets: list  # Lista de balas inativas
    inactive_bullets_limit: int  # Limite de balas inativas
    enemies_limit: int  # Limite de inimigos
    small_animation_limit: int  # Limite de animações pequenas
    enemy_factory: None  # Fábrica de inimigos
    animation_factory: None  # Fábrica de animações
    elapsed_time: float  # Tempo passado
    event: Event  # Eventos

    def __init__(self, screen_size, inactive_bullets_limit, enemies_limit, small_animation_limit):

        self.score = 0
        self.screen_size = screen_size

        # Hitbox do jogador
        player_hitbox = Hitbox((self.screen_size[0] / 2, self.screen_size[1] / 2),
                               (0, 12, 35, 120),
                               (0, -5, 125, 35))

        self.player = Player((self.screen_size[0] / 2, self.screen_size[1] / 2),
                             1.0,
                             100,
                             100.0,
                             10.0,
                             BulletType.TRIPLE,
                             1.0,
                             1.0,
                             0.25,
                             os.path.join("Audio", "SFX", "Gun 4.wav"),
                             os.path.join("Audio", "SFX", "Damage.wav"),
                             (300, 300),
                             os.path.join("Sprites", "Planes", "UK_Spitfire.png"),
                             0,
                             player_hitbox)

        self.enemies = []
        self.bullets = []
        self.clouds = []
        self.animations = []
        self.inactive_bullets = []
        self.inactive_bullets_limit = inactive_bullets_limit
        self.enemies_limit = enemies_limit
        self.small_animation_limit = small_animation_limit
        self.enemy_factory = EnemyFactory(self.screen_size,
                                          300.0,
                                          1.0,
                                          0.25,
                                          (300, 300),
                                          180,
                                          os.path.join("Audio", "SFX", "Damage.wav"))
        self.animation_factory = AnimationFactory((300, 300))
        self.elapsed_time = 0.0
        self.event = None

        self.generate_clouds(10)  # Gera as nuvens

    def update_player_modifiers(self, modifiers):
        '''
        Atualiza os modificadores do jogador.
        '''

        self.player.update_modifiers(modifiers)

    def get_player_life(self):
        '''
        Retorna a vida do jogador.
        '''

        return self.player.get_life()

    def get_score(self):
        '''
        Retorna a pontuação do jogador.
        '''

        return self.score

    def get_entities(self, physics_entities):
        '''
        Retorna uma lista de entidades.
        '''

        # No caso de entidades para a física retorna um dicionário. Isso deixa a classificação
        # de entidades mais fácil no processamento da física
        if physics_entities:

            return {"Clouds": self.clouds,
                    "Bullets": self.bullets,
                    "Enemies": self.enemies,
                    "Player": self.player}
        else:  # Retorna todas as entidades para o processamento gráfico

            return self.clouds + self.bullets + self.enemies + [self.player] + self.animations

    def generate_clouds(self, cloud_count):
        '''
        Gera as nuvens.
        '''

        for _ in range(cloud_count):  # Loop com base na quantidade de nuvens

            # Posição inicial da nuvem. Esta posição é aleatória e fica acima da tela
            position = (randint(0, self.screen_size[0]),
                        randint(-self.screen_size[1], self.screen_size[1]))

            # Caminho para uma das nuvens. Definido aleatóriamente
            path = os.path.join("Sprites", "Scenery", f"Cloud {randint(0, 4)}.png")

            # Carrega a imagem da nuvem
            image = pygame.image.load(path)

            # Define o tamanho da imagem
            size = (image.get_width() * 3, image.get_height() * 3)

            # Define a velocidade com base no tamanho da imagem
            speed = (256.0 / image.get_width()) * 50.0

            # Adiciona a nuvem na lista
            self.clouds.append(Cloud(position,
                                     size,
                                     path,
                                     0,
                                     speed))

            # Ordena as nuvens com base no tamanho, assim as nuvens maiores ficarão por trás das
            # menores
            self.clouds.sort(key=lambda cloud: cloud.size[0], reverse=True)

    def generate_shot(self, position, bullet_type, friendly, damage):
        '''
        Gera o tiro.
        '''

        # Define o tamanho inicial, tamanho, caminho e velocidade
        instatiation_position = (0, 0)
        size = (3, 9)
        path = os.path.join("Sprites", "Bullets", "Bullet.png")
        velocity = 500.0

        # Caso a bala seja do jogador muda sua velocidade para ir para o norte
        if friendly:

            velocity = -500.0

        if bullet_type == BulletType.SIMPLE:  # Tiro simples

            # Reaproveita balas caso tenha alguma diponível na lista de balas inativas
            if len(self.inactive_bullets) > 0:

                # Define a bala, atira, adiciona a bala na lista de balas e a remove da lista de
                # balas inativas

                bullet = self.inactive_bullets[0]
                bullet.shoot((position[0], position[1]), (0.0, velocity), friendly, damage)
                self.bullets.append(bullet)
                self.inactive_bullets.remove(bullet)
            else:  # Cria uma bala nova caso não haja nenhuma disponível

                # Instancia a bala, atira e adiciona na lista de balas

                bullet = Bullet(instatiation_position,
                                size,
                                path,
                                None,
                                friendly,
                                damage)
                bullet.shoot((position[0], position[1]), (0.0, velocity), friendly, damage)
                self.bullets.append(bullet)
        elif bullet_type == BulletType.DOUBLE:  # Tiro duplo

            # Posições laterais das balas, com um espaçamento de 60 pixels entre elas

            position_x_0 = position[0] - 30
            position_x_1 = position[0] + 30

            if len(self.inactive_bullets) > 1:  # Caso tenham duas balas inativas

                # Define as duas balas, atira cada uma e as adiciona na lista de balas. Depois
                # as remove da lista de balas inativas.

                bullet_left = self.inactive_bullets[0]
                bullet_right = self.inactive_bullets[1]

                bullet_left.shoot((position_x_0, position[1]),
                                  (0.0, velocity),
                                  friendly,
                                  damage)

                bullet_right.shoot((position_x_1, position[1]),
                                   (0.0, velocity),
                                   friendly,
                                   damage)

                self.bullets.append(bullet_left)
                self.inactive_bullets.remove(bullet_left)

                self.bullets.append(bullet_right)
                self.inactive_bullets.remove(bullet_right)
            else:  # Cria novas balas

                # Instancia duas balas, atira cada uma e as adiciona na lista de balas.

                bullet_left = Bullet(instatiation_position,
                                     size,
                                     path,
                                     None,
                                     friendly,
                                     damage)

                bullet_right = Bullet(instatiation_position,
                                      size,
                                      path,
                                      None,
                                      friendly,
                                      damage)

                bullet_left.shoot((position_x_0, position[1]),
                                  (0.0, velocity),
                                  friendly,
                                  damage)

                bullet_right.shoot((position_x_1, position[1]),
                                   (0.0, velocity),
                                   friendly,
                                   damage)

                self.bullets.append(bullet_left)
                self.bullets.append(bullet_right)
        elif bullet_type == BulletType.TRIPLE:  # Tiro triplo

            # Posições laterais das balas, com um espaçamento de 60 pixels entre elas.
            # A bala central fica na posição (0, 0)

            position_x_0 = position[0] - 28
            position_x_1 = position[0] + 28

            if len(self.inactive_bullets) > 2:  # Caso tenham três balas inativas

                # Define as três balas, atira cada uma e as adiciona na lista de balas. Depois
                # as remove da lista de balas inativas.

                bullet_left = self.inactive_bullets[0]
                bullet_center = self.inactive_bullets[1]
                bullet_right = self.inactive_bullets[2]

                bullet_left.shoot((position_x_0, position[1]),
                                  (0.0, velocity),
                                  friendly,
                                  damage)

                bullet_center.shoot((position[0], position[1]),
                                    (0.0, velocity),
                                    friendly,
                                    damage)

                bullet_right.shoot((position_x_1, position[1]),
                                   (0.0, velocity),
                                   friendly,
                                   damage)

                self.bullets.append(bullet_left)
                self.inactive_bullets.remove(bullet_left)

                self.bullets.append(bullet_center)
                self.inactive_bullets.remove(bullet_center)

                self.bullets.append(bullet_right)
                self.inactive_bullets.remove(bullet_right)
            else:  # Cria novas balas

                # Instancia três balas, atira cada uma e as adiciona na lista de balas.

                bullet_left = Bullet(instatiation_position,
                                     size,
                                     path,
                                     None,
                                     friendly,
                                     damage)

                bullet_center = Bullet(instatiation_position,
                                       size,
                                       path,
                                       None,
                                       friendly,
                                       damage)

                bullet_right = Bullet(instatiation_position,
                                      size,
                                      path,
                                      None,
                                      friendly,
                                      damage)

                bullet_left.shoot((position_x_0, position[1]),
                                  (0.0, velocity),
                                  friendly,
                                  damage)

                bullet_center.shoot((position[0], position[1]),
                                    (0.0, velocity),
                                    friendly,
                                    damage)

                bullet_right.shoot((position_x_1, position[1]),
                                   (0.0, velocity),
                                   friendly,
                                   damage)

                self.bullets.append(bullet_left)
                self.bullets.append(bullet_center)
                self.bullets.append(bullet_right)
        else:  # Tiro triplo em ângulo

            # Define as três balas, atira cada uma e as adiciona na lista de balas. Depois
            # as remove da lista de balas inativas.

            position_x_0 = position[0] - 28
            position_x_1 = position[0] + 28

            if len(self.inactive_bullets) > 2:  # Caso tenham três balas inativas

                # Define as três balas, atira cada uma e as adiciona na lista de balas. Depois
                # as remove da lista de balas inativas.

                bullet_left = self.inactive_bullets[0]
                bullet_center = self.inactive_bullets[1]
                bullet_right = self.inactive_bullets[2]

                bullet_left.shoot((position_x_0, position[1]),
                                  (-velocity, velocity),
                                  friendly,
                                  damage)

                bullet_center.shoot((position[0], position[1]),
                                    (0.0, velocity),
                                    friendly,
                                    damage)

                bullet_right.shoot((position_x_1, position[1]),
                                   (velocity, velocity),
                                   friendly,
                                   damage)

                self.bullets.append(bullet_left)
                self.inactive_bullets.remove(bullet_left)

                self.bullets.append(bullet_center)
                self.inactive_bullets.remove(bullet_center)

                self.bullets.append(bullet_right)
                self.inactive_bullets.remove(bullet_right)
            else:  # Cria novas balas

                # Instancia três balas, atira cada uma e as adiciona na lista de balas.

                bullet_left = Bullet(instatiation_position,
                                     size,
                                     path,
                                     None,
                                     friendly,
                                     damage)

                bullet_center = Bullet(instatiation_position,
                                       size,
                                       path,
                                       None,
                                       friendly,
                                       damage)

                bullet_right = Bullet(instatiation_position,
                                      size,
                                      path,
                                      None,
                                      friendly,
                                      damage)

                bullet_left.shoot((position_x_0, position[1]),
                                  (-velocity, velocity),
                                  friendly,
                                  damage)

                bullet_center.shoot((position[0], position[1]),
                                    (0.0, velocity),
                                    friendly,
                                    damage)

                bullet_right.shoot((position_x_1, position[1]),
                                   (velocity, velocity),
                                   friendly,
                                   damage)

                self.bullets.append(bullet_left)
                self.bullets.append(bullet_center)
                self.bullets.append(bullet_right)

    def enemy_generator(self):
        '''
        Gera os inimigos.
        '''

        # A cada 30 segundos adiciona um novo inimigo. Esta variável define quantos inimigos devem
        # estar ativos.
        enemy_count = 1 + int(self.elapsed_time / 30)

        # Limita os inimigos
        if enemy_count > self.enemies_limit:

            enemy_count = self.enemies_limit

        # Gera inimigos quando necessário
        while enemy_count - len(self.enemies) > 0:

            enemy = self.enemy_factory.generate_enemy(self.elapsed_time)

            if enemy is not None:

                self.enemies.append(enemy)

    def reset(self):
        '''
        Redefine as entidades e outros atributos.
        '''

        self.score = 0
        self.player.reset((self.screen_size[0] / 2, self.screen_size[1] / 2))
        self.enemies.clear()
        self.bullets.clear()
        self.animations.clear()
        self.elapsed_time = 0.0

    def update(self, state, events, tick):
        '''
        Atualiza as entidades e seus comportamentos.
        '''

        self.event = None  # Reseta o evento

        if state == State.GAMEPLAY:  # atualiza apenas durante o gameplay

            # Comportamento do jogador
            self.player.behaviour(events, self.screen_size, tick)

            # Caso o jogador esteja preparado para dar um tiro
            if self.player.is_attacking() and self.player.is_ready():

                # Gera o tiro
                self.generate_shot(self.player.get_position(),
                                   self.player.get_bullet_type(),
                                   True,
                                   self.player.get_damage(self.player.get_damage_modifier()))

                # Define o jogador como não preparado para dar um tiro (Cooldown)
                self.player.set_fire_state(False)

                # Toca o som de tiro
                self.player.play_shot_sound()

            # Caso o jogador tenha sofrido dano adiciona uma animação de explosão e toca um som de
            # dano
            if self.player.is_damaged():

                if len(self.animations) <= self.small_animation_limit:

                    self.animations.append(self.animation_factory.generate_explosion(
                        self.player.get_position(), True))

                self.player.play_damage_sound()

            # Caso o jogador tenha sido destruido encerra o gameplay
            if not self.player.is_active():

                self.event = Event.GP_GAMEOVER

            # Processa o comportamento das nuvens
            for cloud in self.clouds:

                cloud.behaviour(self.screen_size)

            # Processa o comportamento das balas e as remove da lista quando elas saem da tela
            # ou atingem um inimigo
            for bullet in self.bullets:

                bullet.behaviour(self.screen_size)

                if not bullet.is_active():

                    self.inactive_bullets.append(bullet)
                    self.bullets.remove(bullet)

            # Processa o comportamento dos inimigos
            for enemy in self.enemies:

                enemy.behaviour(tick, self.screen_size, self.player.get_position(), self.enemies)

                # Gera os tiros dos inimigos. A lógica é similar a do jogador
                if enemy.is_attacking() and enemy.is_ready():

                    self.generate_shot(enemy.get_position(),
                                       enemy.get_bullet_type(),
                                       False,
                                       enemy.get_damage())

                    enemy.set_fire_state(False)
                    enemy.play_shot_sound()

                # Gera uma pequena explosão quando sofre dano. Lógica similar a do jogador
                if enemy.is_damaged():

                    if len(self.animations) <= self.small_animation_limit:

                        self.animations.append(
                            self.animation_factory.generate_explosion(enemy.get_position(), True))

                    enemy.play_damage_sound()

                # Quando o inimigo fica inativo
                if not enemy.is_active():

                    # Caso o inimigo tenha sido destruído
                    if enemy.is_destroyed():

                        # Adiciona a pontuação e dá 10 de vida ao jogador
                        self.score += enemy.get_score_value()
                        self.player.change_life(10)

                        # Sempre explode, idependente do limite
                        self.animations.append(
                            self.animation_factory.generate_explosion(enemy.get_position(), False))

                    self.enemies.remove(enemy)  # Remove o inimigo

            # Processa o comportamento das animações e as remove da lista quando elas acabam
            for animation in self.animations:

                animation.behaviour()

                if not animation.is_active():

                    self.animations.remove(animation)

            self.enemy_generator()  # Processa a geração de inimigos
            self.elapsed_time += (1 / tick)  # Conta o tempo

            # Remove o excesso de balas inativas
            while len(self.inactive_bullets) > self.inactive_bullets_limit:

                self.inactive_bullets.remove(self.inactive_bullets[0])

    def get_event(self):
        '''
        Retorna os eventos.
        '''

        return self.event


class EnemyFactory():

    '''
    Fábrica de inimigos. Auxilia na criação dos inimigos. A dificuldade total é o tempo que demora
    para ser permitida a geração dos inimigos mais difíceis.
    '''

    screen_size: tuple  # Tamanho da tela
    max_difficulty: float  # Dificuldade máxima
    drag: float  # Arrasto padrão
    stun_time: float  # Tempo de atordoamento padrão
    size: tuple  # Tamanho padrão
    angle: int  # Ângulo padrão
    damage_sound: str  # Som de dano padrão

    def __init__(self, scree_size, max_difficulty, drag, stun_time, size, angle, damage_sound):

        self.screen_size = scree_size
        self.max_difficulty = max_difficulty
        self.drag = drag
        self.stun_time = stun_time
        self.size = size
        self.angle = angle
        self.damage_sound = damage_sound

    def generate_enemy(self, difficulty):
        '''
        Gera um inimigo e o retorna.
        '''

        enemy = None

        # A posição no spawn é determinada em uma matriz, assim  evita que aviões sejam
        # instanciados em posições desajustadas

        spawn_positions = []

        for i in range(150, self.screen_size[0] - 150, 300):

            for j in range(-self.screen_size[1], -150, 300):

                spawn_positions.append((i, j))

        position = choice(spawn_positions)

        if difficulty > self.max_difficulty:

            difficulty = self.max_difficulty

        # Número aleatório gerado com base em um intervalo que aumenta conforme o tempo passa
        difficulty_range = randint(0, int(100.0 * difficulty / self.max_difficulty))

        if difficulty_range <= 25:  # Dificuldade inicial

            # Gera algum dos quatro aviões. O avião gerado tem sua hibox definida e é instanciado
            # com seus parÂmetros

            random_number = randint(0, 100)

            if random_number < 33:

                hitbox = Hitbox(position,
                                (0, -12, 35, 120),
                                (0, 5, 125, 35))

                enemy = Enemy(position,
                              self.drag,
                              80,
                              100.0,
                              10.0,
                              BulletType.SIMPLE,
                              1.0,
                              1.0,
                              self.stun_time,
                              os.path.join("Audio", "SFX", "Gun 3.wav"),
                              self.damage_sound,
                              self.size,
                              os.path.join("Sprites", "Planes", "GER_bf109.png"),
                              self.angle,
                              hitbox,
                              100)
            elif random_number < 66:

                hitbox = Hitbox(position,
                                (0, -12, 35, 120),
                                (0, 5, 125, 35))

                enemy = Enemy(position,
                              self.drag,
                              80,
                              100.0,
                              10.0,
                              BulletType.SIMPLE,
                              1.25,
                              1.0,
                              self.stun_time,
                              os.path.join("Audio", "SFX", "Gun 3.wav"),
                              self.damage_sound,
                              self.size,
                              os.path.join("Sprites", "Planes", "JAP_a6m.png"),
                              self.angle,
                              hitbox,
                              100)
            elif random_number < 98:

                hitbox = Hitbox(position,
                                (0, -12, 35, 120),
                                (0, 5, 125, 35))

                enemy = Enemy(position,
                              self.drag,
                              80,
                              100.0,
                              10.0,
                              BulletType.SIMPLE,
                              1.5,
                              1.0,
                              self.stun_time,
                              os.path.join("Audio", "SFX", "Gun 3.wav"),
                              self.damage_sound,
                              self.size,
                              os.path.join("Sprites", "Planes", "US_p40.png"),
                              self.angle,
                              hitbox,
                              100)
            else:  # Avião para pontos extras

                hitbox = Hitbox(position,
                                (0, -12, 35, 120),
                                (0, 5, 125, 35))

                enemy = Enemy(position,
                              self.drag,
                              10,
                              200.0,
                              1.0,
                              BulletType.SIMPLE,
                              0.1,
                              0.1,
                              self.stun_time,
                              os.path.join("Audio", "SFX", "Gun 3.wav"),
                              self.damage_sound,
                              self.size,
                              os.path.join("Sprites", "Planes", "USSR_Lagg3.png"),
                              self.angle,
                              hitbox,
                              1000)
        elif difficulty_range <= 50:  # Dificuldade média

            # Gera algum dos dois aviões. O avião gerado tem sua hibox definida e é instanciado
            # com seus parÂmetros

            random_number = randint(0, 1)

            if random_number == 0:

                hitbox = Hitbox(position,
                                (0, -5, 35, 130),
                                (0, 15, 165, 35))

                enemy = Enemy(position,
                              self.drag,
                              120,
                              100.0,
                              12.0,
                              BulletType.SIMPLE,
                              2.0,
                              5.0,
                              self.stun_time,
                              os.path.join("Audio", "SFX", "Gun 1.wav"),
                              self.damage_sound,
                              self.size,
                              os.path.join("Sprites", "Planes", "GER_bf110.png"),
                              self.angle,
                              hitbox,
                              250)
            else:

                hitbox = Hitbox(position,
                                (0, -8, 35, 145),
                                (0, 20, 200, 40))

                enemy = Enemy(position,
                              self.drag,
                              150,
                              90.0,
                              12.0,
                              BulletType.SIMPLE,
                              0.9,
                              5.0,
                              self.stun_time,
                              os.path.join("Audio", "SFX", "Gun 2.wav"),
                              self.damage_sound,
                              self.size,
                              os.path.join("Sprites", "Planes", "GER_He111.png"),
                              self.angle,
                              hitbox,
                              250)
        elif difficulty_range <= 75:  # Dificuldade alta

            # Gera algum dos dois aviões. O avião gerado tem sua hibox definida e é instanciado
            # com seus parÂmetros

            random_number = randint(0, 1)

            if random_number == 0:

                hitbox = Hitbox(position,
                                (0, -15, 35, 155),
                                (0, 5, 210, 40))

                enemy = Enemy(position,
                              self.drag,
                              200,
                              80.0,
                              18.0,
                              BulletType.DOUBLE,
                              0.75,
                              1.5,
                              self.stun_time,
                              os.path.join("Audio", "SFX", "Gun 2.wav"),
                              self.damage_sound,
                              self.size,
                              os.path.join("Sprites", "Planes", "JAP_Ki21.png"),
                              self.angle,
                              hitbox,
                              500)
            else:

                hitbox = Hitbox(position,
                                (0, 0, 35, 155),
                                (0, 12, 215, 35))

                enemy = Enemy(position,
                              self.drag,
                              150,
                              100.0,
                              13.0,
                              BulletType.DOUBLE,
                              1.1,
                              1.2,
                              self.stun_time,
                              os.path.join("Audio", "SFX", "Gun 1.wav"),
                              self.damage_sound,
                              self.size,
                              os.path.join("Sprites", "Planes", "US_a26.png"),
                              self.angle,
                              hitbox,
                              500)
        else:  # Dificuldade máxima

            # Gera algum dos dois aviões. O avião gerado tem sua hibox definida e é instanciado
            # com seus parÂmetros

            random_number = randint(0, 1)

            if random_number == 0:

                hitbox = Hitbox(position,
                                (0, -12, 35, 220),
                                (0, 18, 295, 50))

                enemy = Enemy(position,
                              self.drag,
                              500,
                              50.0,
                              24.0,
                              BulletType.TRIPLE,
                              0.75,
                              1.3,
                              self.stun_time,
                              os.path.join("Audio", "SFX", "Gun 5.wav"),
                              self.damage_sound,
                              self.size,
                              os.path.join("Sprites", "Planes", "US_b17.png"),
                              self.angle,
                              hitbox,
                              750)
            else:

                hitbox = Hitbox(position,
                                (0, -12, 40, 215),
                                (0, 18, 295, 50))

                enemy = Enemy(position,
                              self.drag,
                              777,
                              40.0,
                              30.0,
                              BulletType.TRIPLE,
                              1.0,
                              1.5,
                              self.stun_time,
                              os.path.join("Audio", "SFX", "Gun 5.wav"),
                              self.damage_sound,
                              self.size,
                              os.path.join("Sprites", "Planes", "UK_Lancaster.png"),
                              self.angle,
                              hitbox,
                              750)

        return enemy


class AnimationFactory():

    '''
    Auxilia na criação de uma animação.
    '''

    path_lists: list  # Lista de caminhos para os arquivos
    size: tuple  # Tamanho padrão

    def __init__(self, size):

        # Obtém o caminho para todos arquivos

        self.size = size
        self.path_lists = []

        for i in range(5):

            path_list = []

            file_number = len(os.listdir(os.path.join("Sprites",
                                                      "Animations",
                                                      f"Explosion {i + 1}")))

            for j in range(file_number):

                path_list.append(os.path.join("Sprites",
                                              "Animations",
                                              f"Explosion {i + 1}",
                                              f"{j}.png"))

            self.path_lists.append(path_list)

    def generate_explosion(self, position, small):
        '''
        Gera uma entidade animada de explosão e a retorna.
        '''

        path = None
        index = 0

        if small:  # Caso a explosão seja pequena

            index = randint(0, 2)  # Indice das explosões pequenas
        else:  # Caso a explosão seja grande

            index = randint(3, 4)  # Indice das explosões grandes

            # Caminho do som da explosão
            path = os.path.join("Audio", "SFX", "Explosion.wav")

        return Explosion(position, self.size, self.path_lists[index], path)


class BulletType(Enum):

    '''
    Tipos de bala.
    '''

    SIMPLE = 1
    DOUBLE = 2
    TRIPLE = 3
    TRIPLE_IN_ANGLE = 4


class Entity():

    '''
    Entidade física.
    '''

    active: bool  # Estado de atividade da entidade
    position: list  # O sistema de coordenadas tem o ponto (0, 0) no topo da tela. eixo y invertido
    velocity: list  # Para cima: (0, -1), para baixo: (0, 1)
    drag: float  # Arrasto
    size: tuple  # Tamanho
    hitbox: Hitbox  # Hitbox
    sprite: CustomSprite  # Sprite

    def __init__(self, position, drag, size, animate, sprite_path, angle, hitbox):

        self.active = True
        self.position = list(position)
        self.velocity = [0, 0]
        self.drag = drag
        self.size = size
        self.hitbox = None

        # Define uma hitbox caso necessário
        if hitbox is not None:

            self.hitbox = hitbox

        self.sprite = None

        # Define um sprite animado ou normal
        if animate:

            self.sprite = CustomAnimatedSprite((self.position[0] - size[0] / 2,
                                                self.position[1] - size[1] / 2),
                                               size,
                                               sprite_path)
        else:

            self.sprite = CustomSprite((self.position[0] - size[0] / 2,
                                        self.position[1] - size[1] / 2),
                                       size,
                                       sprite_path,
                                       angle=angle)

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

    def get_drag(self):
        '''
        Retorna o arrasto.
        '''

        return self.drag

    def set_position(self, position):
        '''
        Define a posição.
        '''

        self.position = list(position)

        # Atualiza a posição do sprite
        self.sprite.update((self.position[0] - self.size[0] / 2,
                            self.position[1] - self.size[1] / 2))

        # Atualiza a hitbox caso tenha
        if self.hitbox is not None:

            self.hitbox.update(position)

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

    def get_hitbox(self):
        '''
        Retorna uma lista de hitbox's. Pode ser None.
        '''

        if self.hitbox is not None:

            return self.hitbox.get_hitbox()
        else:

            return None

    def deactivate(self):
        '''
        Desativa a entidade.
        '''

        self.active = False

    def is_active(self):
        '''
        Retorna verdadeiro caso a entidade esteja ativa.
        '''

        return self.active


class Aircraft(Entity):

    '''
    Super Classe para as aeronaves.
    '''

    direction: list  # Armazena a direção, assim conservamos a velocidade
    life: int  # Vida
    max_life: int  # Vida máxima
    speed: float  # Velocidade em pixels por segundo
    damage: float  # Dano
    bullet_type: BulletType  # Tipo de bala
    firerate: float  # Cadência de tiros
    firerate_cooldown: float  # Cooldown da cadência
    fire_ready: bool  # Define se está pronto para dar um tiro
    armor: float  # Armadura
    stun_time: float  # Tempo de atordoamento
    stun_cooldown: float  # Cooldown de atordoamento
    stunned: bool  # Define se está atordoado
    attacking: bool  # Define se está atacando
    destroyed: bool  # Define se está destruido
    damaged: bool  # Define se levou dano
    attack_sound: pygame.mixer.Sound  # Som de ataque
    damage_sound: pygame.mixer.Sound  # Som de dano

    def __init__(self,
                 position,
                 drag,
                 max_life,
                 speed,
                 damage,
                 bullet_type,
                 firerate,
                 armor,
                 stun_time,
                 attack_sound,
                 damage_sound,
                 size,
                 sprite_path,
                 angle,
                 hitbox):

        super().__init__(position, drag, size, False, sprite_path, angle, hitbox)

        self.direction = [0, 0]
        self.life = max_life  # Todas as entidades são instanciadas com a vida cheia
        self.max_life = max_life
        self.speed = speed
        self.damage = damage
        self.bullet_type = bullet_type
        self.firerate = firerate
        self.firerate_cooldown = 0.0
        self.fire_ready = True
        self.armor = armor
        self.stun_time = stun_time
        self.stun_cooldown = 0.0
        self.stunned = False
        self.attacking = False
        self.destroyed = False
        self.damaged = False
        self.attack_sound = pygame.mixer.Sound(attack_sound)
        self.damage_sound = pygame.mixer.Sound(damage_sound)

    def change_life(self, value, stun=False, armor_modifier=0.0):
        '''
        Muda o valor de vida da aeronave
        '''

        if value < 0:  # Se for dano

            if not self.stunned:  # Se não estiver atordoado

                # Muda a vida com base na armadura
                self.life += int(value * (1.0 / (self.armor + armor_modifier / 100.0)))

                if stun:  # Atordoa caso necessário

                    self.stunned = True
                self.damaged = True  # Define que a aeronave foi danificada
        else:  # Se for cura

            # Aumenta vida, mas limita até a vida máxima

            self.life += int(value)

            if self.life > self.max_life:

                self.life = self.max_life

        if self.life <= 0:  # Caso a vida seja menor que zero marca que a aeronave está inativa

            self.life = 0
            self.active = False
            self.destroyed = True

    def stun_behaviour(self, tick):
        '''
        Processa o comportamento do atordoamento. Funciona como um contador que reseta quando chega
        a um limite
        '''

        if self.stunned:

            self.stun_cooldown += (1 / tick)

            if self.stun_cooldown > self.stun_time:

                self.stun_cooldown = 0.0
                self.stunned = False

    def firerate_behaviour(self, tick, firerate_modifier=0.0):
        '''
        Processa o cooldown do tiro. Funciona como um contador que reseta quando chega
        a um limite. Neste método é considerado o modificador de cadência.
        '''
        if not self.fire_ready:

            self.firerate_cooldown += (1 / tick)

            if self.firerate_cooldown > 1 / (self.firerate + firerate_modifier / 10.0):

                self.firerate_cooldown = 0.0
                self.fire_ready = True

    def get_damage(self, damage_modifier=0.0):
        '''
        Obtém o dano da aeronave. Considera o modificador de dano.
        '''

        return -(self.damage + damage_modifier / 4)

    def is_attacking(self):
        '''
        Retorna verdadeiro caso a aeronave esteja atacando.
        '''

        return self.attacking

    def is_ready(self):
        '''
        Retorna verdadeiro caso a aeronave esteja pronta para atirar.
        '''

        return self.fire_ready

    def set_fire_state(self, ready):
        '''
        Estado do tiro.
        '''

        self.fire_ready = ready

    def get_bullet_type(self):
        '''
        Retorna o tipo de bala.
        '''

        return self.bullet_type

    def is_destroyed(self):
        '''
        Retorna verdadeiro se a aeronave foi destruída.
        '''

        return self.destroyed

    def is_damaged(self):
        '''
        Retorna verdadeiro caso a aeronave tenha sofrido dano. Reseta o estado do dano.
        '''

        damaged = self.damaged
        self.damaged = False

        return damaged

    def play_shot_sound(self):
        '''
        Toca o som de tiro.
        '''

        self.attack_sound.play(maxtime=600)

    def play_damage_sound(self):
        '''
        Toca o som de dano.
        '''

        self.damage_sound.play(maxtime=600)


class Player(Aircraft):

    '''
    Jogador.
    '''

    # Modificadores
    velocity_modifier: int
    damage_modifier: int
    firerate_modifier: int
    armor_modifier: int

    def __init__(self,
                 position,
                 drag,
                 max_life,
                 speed,
                 damage,
                 bullet_type,
                 firerate,
                 armor,
                 stun_time,
                 attack_sound,
                 damage_sound,
                 size,
                 sprite_path,
                 angle,
                 hitbox):

        super().__init__(position,
                         drag,
                         max_life,
                         speed,
                         damage,
                         bullet_type,
                         firerate,
                         armor,
                         stun_time,
                         attack_sound,
                         damage_sound,
                         size,
                         sprite_path,
                         angle,
                         hitbox)

        self.velocity_modifier = 0
        self.damage_modifier = 0
        self.firerate_modifier = 0
        self.armor_modifier = 0

    def behaviour(self, events, screen_size, tick):
        '''
        Definição do comportamento do jogador.
        '''

        self.stun_behaviour(tick)  # Processa o contador do atordoamento
        self.firerate_behaviour(tick, self.firerate_modifier)  # Processa o contador da cadência

        for event in events:  # Para cada tecla pressionada ou clique

            if event.type == pygame.KEYDOWN:  # Caso uma tecla tenha sido pressionada

                if event.key == pygame.K_a:  # Tecla 'A'

                    self.direction[0] = -1  # Esquerda
                elif event.key == pygame.K_d:  # Tecla 'D'

                    self.direction[0] = 1  # Direita

                if event.key == pygame.K_s:  # Tecla 'S'

                    self.direction[1] = 1  # Para baixo
                elif event.key == pygame.K_w:  # Tecla 'W'

                    self.direction[1] = -1  # Para cima

                if event.key == pygame.K_k:  # Tecla 'K'

                    self.attacking = True  # Ataca
            elif event.type == pygame.KEYUP:  # Caso uma tecla seja solta

                if event.key == pygame.K_a or event.key == pygame.K_d:  # Teclas horizontais

                    self.direction[0] = 0  # Parado horizontalmente

                if event.key == pygame.K_s or event.key == pygame.K_w:  # Teclas verticais

                    self.direction[1] = 0  # Parado verticalmente

                if event.key == pygame.K_k:  # Para de atacar

                    self.attacking = False

            if self.direction[0] != 0:  # Adiciona a velociade lateral

                self.velocity[0] = self.direction[0] * (self.speed + self.velocity_modifier * 4)

            if self.direction[1] != 0:  # Adiciona a velocidade vertical

                self.velocity[1] = self.direction[1] * (self.speed + self.velocity_modifier * 4)

        # Adiciona uma velociade contrária para impedir que o jogador saia da tela

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

        if modifiers["Bullet Type"] <= 25:

            self.bullet_type = BulletType.SIMPLE
        elif modifiers["Bullet Type"] <= 50:

            self.bullet_type = BulletType.DOUBLE
        elif modifiers["Bullet Type"] <= 75:

            self.bullet_type = BulletType.TRIPLE
        else:

            self.bullet_type = BulletType.TRIPLE_IN_ANGLE

    def get_damage_modifier(self):
        '''
        Retorna o modificador de dano.
        '''

        return self.damage_modifier

    def get_armor_modifier(self):
        '''
        Retorna o modificador de armadura.
        '''

        return self.armor_modifier

    def reset(self, position):
        '''
        Redefine o jogador.
        '''

        self.active = True
        self.attacking = False
        self.stunned = False
        self.life = self.max_life
        self.velocity = [0, 0]
        self.position = list(position)
        self.direction = [0, 0]


class Enemy(Aircraft):

    '''
    Inimigos.
    '''

    score_value: int  # Valor em pontos

    def __init__(self,
                 position,
                 drag,
                 max_life,
                 speed,
                 damage,
                 bullet_type,
                 firerate,
                 armor,
                 stun_time,
                 attack_sound,
                 damage_sound,
                 size,
                 sprite_path,
                 angle,
                 hitbox,
                 score_value):

        super().__init__(position,
                         drag,
                         max_life,
                         speed,
                         damage,
                         bullet_type,
                         firerate,
                         armor,
                         stun_time,
                         attack_sound,
                         damage_sound,
                         size,
                         sprite_path,
                         angle,
                         hitbox)

        self.score_value = score_value

    def behaviour(self, tick, screen_size, player_position, enemies):
        '''
        Definição do comportamento do inimigo.
        '''

        self.stun_behaviour(tick)  # Processa o contador do atordoamento
        self.firerate_behaviour(tick)  # Processa o contador da cadência

        self.velocity[1] = self.speed  # Mantém sempre a mesma velocidade vertical

        chase_player = True  # Definição se o inimigo deve ou não perseguir o jogador

        # Distâncias mínimas
        minimum_x_distance = self.size[0] - 100
        minimum_y_distance = self.size[1] - 100

        # Impede a colisão entre inimigos
        for enemy in enemies:

            if enemy != self:  # Caso o inimigo não seja ele mesmo

                # Calcula a distância
                distance = sqrt((enemy.get_position()[0] - self.position[0])**2 +
                                (enemy.get_position()[1] - self.position[1])**2)

                # Se afasta dos outros inimigos
                if distance < minimum_x_distance:

                    if enemy.get_position()[0] < self.position[0]:  # O outro inimgo está a esquerda

                        self.velocity[0] = self.speed
                    else:

                        self.velocity[0] = -self.speed

                    chase_player = False
                # Evita que o inimigo procure o jogador logo depois de se afastar de outro inimigo
                elif distance < minimum_x_distance + 100:

                    chase_player = False

        if chase_player:  # Caso seja possível perseguir o jogador

            # Caso o jogador esteja a mais de 100 pixels de distância lateral
            if abs(player_position[0] - self.position[0]) > 100:

                # Caso esteja muito perto do jogador inverte a direção
                if (player_position[1] - self.position[1]) > minimum_y_distance:

                    direction = -1
                else:

                    direction = 1

                # Determina a direção para chegar perto do jogador
                if player_position[0] < self.position[0]:

                    self.velocity[0] = self.speed * direction
                else:

                    self.velocity[0] = self.speed * -direction

        # Ataca o jogador caso estejam próximos nas coordenadas verticais
        if (player_position[0] - self.position[0]) < - 100:

            self.attacking = False
        elif (player_position[0] - self.position[0]) > 100:

            self.attacking = False
        elif self.position[1] > 0:

            self.attacking = True

        # Desativa o inimigo caso ele saia da tela na lateral ou em baixo
        if self.position[0] <= 0 - self.size[0] or              \
           self.position[0] >= screen_size[0] + self.size[0] or \
           self.position[1] >= screen_size[1] + self.size[1]:

            self.active = False

    def get_score_value(self):
        '''
        Retorna a pontuação obtida ao destruir o inimigo.
        '''

        return self.score_value


class Bullet(Entity):

    '''
    Bala.
    '''

    friendly: bool  # Define se a bala vem do jogador ou não
    damage: int  # Dano da bala

    def __init__(self, position, size, sprite_path, hitbox, friendly, damage):

        super().__init__(position, 0.0, size, False, sprite_path, 0, hitbox)

        self.friendly = friendly
        self.damage = damage

    def behaviour(self, screen_size):
        '''
        Comportamento da bala. Desativa caso saia da tela.
        '''

        if self.position[0] <= 0 or              \
           self.position[0] >= screen_size[0] or \
           self.position[1] <= 0 or              \
           self.position[1] >= screen_size[1]:

            self.active = False

    def shoot(self, position, velocity, friendly, damage):
        '''
        Atira a bala. Define a sua posição e velocidade.
        '''

        self.active = True
        self.position = list(position)
        self.velocity = list(velocity)
        self.friendly = friendly
        self.damage = damage

    def is_friendly(self):
        '''
        Retorna verdadeiro caso a bala seja do jogador.
        '''

        return self.friendly

    def get_damage(self):
        '''
        Retorna o dano da bala
        '''

        return self.damage


class Cloud(Entity):

    '''
    Nuvem.
    '''

    def __init__(self, position, size, sprite_path, angle, constant_speed):

        super().__init__(position, 0.0, size, False, sprite_path, angle, None)

        self.velocity[1] = constant_speed  # Define uma velocidade constante

    def behaviour(self, screen_size):
        '''
        Comportamento da núvem. Redefine a posição assim que a nuvem sai da tela
        '''

        if self.position[1] > screen_size[1] + self.size[1] / 2:

            self.set_position((randint(0, screen_size[0]),
                               randint(-screen_size[1], -screen_size[1] // 2)))


class Explosion(Entity):

    '''
    Entidade que representa uma explosão, ela é usada apenas para fins visuais.
    '''

    def __init__(self, position, size, sprite_path, sound=None):

        super().__init__(position, 0.0, size, True, sprite_path, 0, None)

        self.sprite.start_animation()

        # Define o som caso tenha um
        if sound is not None:

            pygame.mixer.Sound(sound).play(maxtime=2000)

    def behaviour(self):
        '''
        Comportamento da explosão. Anima ela e a desativa quando a animação acaba.
        '''

        self.sprite.animate_frame()

        if not self.sprite.is_animating():

            self.active = False

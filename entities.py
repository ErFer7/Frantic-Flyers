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

    score: int
    screen_size: tuple
    player: None
    enemies: list
    bullets: list
    clouds: list
    animations: list
    inactive_bullets: list  # Usado no pooling
    inactive_bullets_limit: int
    enemies_limit: int
    small_animation_limit: int
    enemy_factory: None
    animation_factory: None
    elapsed_time: float
    event: Event

    def __init__(self, screen_size, inactive_bullets_limit, enemies_limit, small_animation_limit):

        self.score = 0
        self.screen_size = screen_size

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
                             '',  # Som
                             '',  # Som
                             '',  # Som
                             (300, 300),
                             os.path.join("Sprites", "Planes", "UK_Spitfire.png"),
                             0,
                             player_hitbox,
                             ((-28, 0), (0, 0), (28, 0)))

        self.enemies = []
        self.bullets = []
        self.clouds = []
        self.animations = []
        self.inactive_bullets = []
        self.inactive_bullets_limit = inactive_bullets_limit
        self.enemies_limit = enemies_limit
        self.small_animation_limit = small_animation_limit
        self.enemy_factory = EnemyFactory(self.screen_size, 300.0)
        self.animation_factory = AnimationFactory()
        self.elapsed_time = 0.0
        self.event = None

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

    def get_score(self):
        '''
        Retorna a pontuação do jogador.
        '''

        return self.score

    def get_entities(self, physics_entities):
        '''
        Retorna uma lista de entidades.
        '''

        if physics_entities:

            return {"Clouds": self.clouds,
                    "Bullets": self.bullets,
                    "Enemies": self.enemies,
                    "Player": self.player}
        else:

            return self.clouds + self.bullets + self.enemies + [self.player] + self.animations

    def generate_clouds(self, cloud_count):
        '''
        Gera o cenário do jogo.
        '''

        for _ in range(cloud_count):

            position = (randint(0, self.screen_size[0]),
                        randint(-self.screen_size[1], self.screen_size[1]))
            cloud_index = randint(0, 4)
            path = os.path.join("Sprites", "Scenery", f"Cloud {cloud_index}.png")
            image = pygame.image.load(path)
            size = (image.get_width() * 3, image.get_height() * 3)
            speed = (256.0 / image.get_width()) * 50.0

            self.clouds.append(Cloud(position,
                                     size,
                                     path,
                                     0,
                                     speed))

            self.clouds.sort(key=lambda cloud: cloud.size[0], reverse=True)

    def generate_shot(self, position, gun_points, bullet_type, friendly, damage):
        '''
        Gera o tiro.
        '''

        instatiation_position = (0, 0)
        size = (3, 9)
        path = os.path.join("Sprites", "Bullets", "Bullet.png")
        velocity = 500.0

        if friendly:

            velocity = -500.0

        if bullet_type == BulletType.SIMPLE:

            position_x = gun_points[1][0] + position[0]
            position_y = gun_points[1][1] + position[1]

            if len(self.inactive_bullets) > 0:

                bullet = self.inactive_bullets[0]
                bullet.shoot((position_x, position_y), (0.0, velocity), friendly, damage)
                self.bullets.append(bullet)
                self.inactive_bullets.remove(bullet)
            else:

                bullet = Bullet(instatiation_position,
                                size,
                                path,
                                None,
                                friendly,
                                damage)
                bullet.shoot((position_x, position_y), (0.0, velocity), friendly, damage)
                self.bullets.append(bullet)
        elif bullet_type == BulletType.DOUBLE:

            position_x_left = gun_points[0][0] + position[0]
            position_y_left = gun_points[0][1] + position[1]

            position_x_right = gun_points[2][0] + position[0]
            position_y_right = gun_points[2][1] + position[1]

            if len(self.inactive_bullets) > 1:

                bullet_left = self.inactive_bullets[0]
                bullet_right = self.inactive_bullets[1]

                bullet_left.shoot((position_x_left, position_y_left),
                                  (0.0, velocity),
                                  friendly,
                                  damage)

                bullet_right.shoot((position_x_right, position_y_right),
                                   (0.0, velocity),
                                   friendly,
                                   damage)

                self.bullets.append(bullet_left)
                self.inactive_bullets.remove(bullet_left)

                self.bullets.append(bullet_right)
                self.inactive_bullets.remove(bullet_right)
            else:

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

                bullet_left.shoot((position_x_left, position_y_left),
                                  (0.0, velocity),
                                  friendly,
                                  damage)

                bullet_right.shoot((position_x_right, position_y_right),
                                   (0.0, velocity),
                                   friendly,
                                   damage)

                self.bullets.append(bullet_left)
                self.bullets.append(bullet_right)
        elif bullet_type == BulletType.TRIPLE:

            position_x_left = gun_points[0][0] + position[0]
            position_y_left = gun_points[0][1] + position[1]

            position_x_center = gun_points[1][0] + position[0]
            position_y_center = gun_points[1][1] + position[1]

            position_x_right = gun_points[2][0] + position[0]
            position_y_right = gun_points[2][1] + position[1]

            if len(self.inactive_bullets) > 2:

                bullet_left = self.inactive_bullets[0]
                bullet_center = self.inactive_bullets[1]
                bullet_right = self.inactive_bullets[2]

                bullet_left.shoot((position_x_left, position_y_left),
                                  (0.0, velocity),
                                  friendly,
                                  damage)

                bullet_center.shoot((position_x_center, position_y_center),
                                    (0.0, velocity),
                                    friendly,
                                    damage)

                bullet_right.shoot((position_x_right, position_y_right),
                                   (0.0, velocity),
                                   friendly,
                                   damage)

                self.bullets.append(bullet_left)
                self.inactive_bullets.remove(bullet_left)

                self.bullets.append(bullet_center)
                self.inactive_bullets.remove(bullet_center)

                self.bullets.append(bullet_right)
                self.inactive_bullets.remove(bullet_right)
            else:

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

                bullet_left.shoot((position_x_left, position_y_left),
                                  (0.0, velocity),
                                  friendly,
                                  damage)

                bullet_center.shoot((position_x_center, position_y_center),
                                    (0.0, velocity),
                                    friendly,
                                    damage)

                bullet_right.shoot((position_x_right, position_y_right),
                                   (0.0, velocity),
                                   friendly,
                                   damage)

                self.bullets.append(bullet_left)
                self.bullets.append(bullet_center)
                self.bullets.append(bullet_right)
        else:

            position_x_left = gun_points[0][0] + position[0]
            position_y_left = gun_points[0][1] + position[1]

            position_x_center = gun_points[1][0] + position[0]
            position_y_center = gun_points[1][1] + position[1]

            position_x_right = gun_points[2][0] + position[0]
            position_y_right = gun_points[2][1] + position[1]

            if len(self.inactive_bullets) > 2:

                bullet_left = self.inactive_bullets[0]
                bullet_center = self.inactive_bullets[1]
                bullet_right = self.inactive_bullets[2]

                bullet_left.shoot((position_x_left, position_y_left),
                                  (-velocity, velocity),
                                  friendly,
                                  damage)

                bullet_center.shoot((position_x_center, position_y_center),
                                    (0.0, velocity),
                                    friendly,
                                    damage)

                bullet_right.shoot((position_x_right, position_y_right),
                                   (velocity, velocity),
                                   friendly,
                                   damage)

                self.bullets.append(bullet_left)
                self.inactive_bullets.remove(bullet_left)

                self.bullets.append(bullet_center)
                self.inactive_bullets.remove(bullet_center)

                self.bullets.append(bullet_right)
                self.inactive_bullets.remove(bullet_right)
            else:

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

                bullet_left.shoot((position_x_left, position_y_left),
                                  (-velocity, velocity),
                                  friendly,
                                  damage)

                bullet_center.shoot((position_x_center, position_y_center),
                                    (0.0, velocity),
                                    friendly,
                                    damage)

                bullet_right.shoot((position_x_right, position_y_right),
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

        enemy_count = 1 + int(self.elapsed_time / 30)

        if enemy_count > self.enemies_limit:

            enemy_count = self.enemies_limit

        while enemy_count - len(self.enemies) > 0:

            enemy = self.enemy_factory.generate_enemy(self.elapsed_time)

            if enemy is not None:

                self.enemies.append(enemy)

    def reset(self):
        '''
        Redefine todas as entidades.
        '''

        self.score = 0
        self.player.reset((self.screen_size[0] / 2, self.screen_size[1] / 2))
        self.enemies.clear()
        self.bullets.clear()
        self.elapsed_time = 0.0

    def update(self, state, events, tick):
        '''
        Atualiza as entidades e seus comportamentos.
        '''

        self.event = None

        if state == State.GAMEPLAY:

            self.player.behaviour(events, self.screen_size, tick)

            if self.player.is_attacking() and self.player.is_ready():

                self.generate_shot(self.player.get_position(),
                                   self.player.get_gun_points(),
                                   self.player.get_bullet_type(),
                                   True,
                                   self.player.get_damage(self.player.get_damage_modifier()))

                self.player.set_fire_state(False)

            if self.player.is_damaged():

                if len(self.animations) <= self.small_animation_limit:

                    self.animations.append(self.animation_factory.generate_explosion(
                        self.player.get_position(), True))

            if not self.player.is_active():

                self.event = Event.GP_GAMEOVER

            for cloud in self.clouds:

                cloud.behaviour(self.screen_size)

            for bullet in self.bullets:

                bullet.behaviour(self.screen_size)

                if not bullet.is_active():

                    self.inactive_bullets.append(bullet)
                    self.bullets.remove(bullet)

            for enemy in self.enemies:

                enemy.behaviour(tick, self.screen_size, self.player.get_position(), self.enemies)

                if enemy.is_attacking() and enemy.is_ready():

                    self.generate_shot(enemy.get_position(),
                                       enemy.get_gun_points(),
                                       enemy.get_bullet_type(),
                                       False,
                                       enemy.get_damage())
                    enemy.set_fire_state(False)

                if enemy.is_damaged():

                    if len(self.animations) <= self.small_animation_limit:

                        self.animations.append(
                            self.animation_factory.generate_explosion(enemy.get_position(), True))

                if not enemy.is_active():

                    if enemy.is_destroyed():

                        self.score += enemy.get_score_value()
                        self.player.change_life(10)

                        # Sempre explode, idependente do limite
                        self.animations.append(
                            self.animation_factory.generate_explosion(enemy.get_position(), False))

                    self.enemies.remove(enemy)

            for animation in self.animations:

                animation.behaviour()

                if not animation.is_active():

                    self.animations.remove(animation)

            self.enemy_generator()
            self.elapsed_time += (1 / tick)

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

    screen_size: tuple
    max_difficulty: float

    def __init__(self, scree_size, max_difficulty):

        self.screen_size = scree_size
        self.max_difficulty = max_difficulty

    def generate_enemy(self, difficulty):
        '''
        Gera um inimigo e o retorna.
        '''

        enemy = None

        spawn_positions = []

        for i in range(150, self.screen_size[0] - 150, 300):

            for j in range(-self.screen_size[1], -150, 300):

                spawn_positions.append((i, j))

        position = choice(spawn_positions)

        drag = 1.0
        stun_time = 0.25
        size = (300, 300)
        angle = 180

        if difficulty > self.max_difficulty:

            difficulty = self.max_difficulty

        difficulty_range = randint(0, int(100.0 * difficulty / self.max_difficulty))

        if difficulty_range <= 25:

            random_number = randint(0, 100)

            if random_number < 33:

                hitbox = Hitbox(position,
                                (0, -12, 35, 120),
                                (0, 5, 125, 35))

                enemy = Enemy(position,
                              drag,
                              80,
                              100.0,
                              10.0,
                              BulletType.SIMPLE,
                              1.0,
                              1.0,
                              stun_time,
                              '',  # Som
                              '',  # Som
                              size,
                              os.path.join("Sprites", "Planes", "GER_bf109.png"),
                              angle,
                              hitbox,
                              ((10, 0), (0, 0), (-10, 0)),
                              100)
            elif random_number < 66:

                hitbox = Hitbox(position,
                                (0, -12, 35, 120),
                                (0, 5, 125, 35))

                enemy = Enemy(position,
                              drag,
                              80,
                              100.0,
                              10.0,
                              BulletType.SIMPLE,
                              1.0,
                              1.0,
                              stun_time,
                              '',  # Som
                              '',  # Som
                              size,
                              os.path.join("Sprites", "Planes", "JAP_a6m.png"),
                              angle,
                              hitbox,
                              ((10, 0), (0, 0), (-10, 0)),
                              100)
            elif random_number < 98:

                hitbox = Hitbox(position,
                                (0, -12, 35, 120),
                                (0, 5, 125, 35))

                enemy = Enemy(position,
                              drag,
                              80,
                              100.0,
                              10.0,
                              BulletType.SIMPLE,
                              1.0,
                              1.0,
                              stun_time,
                              '',  # Som
                              '',  # Som
                              size,
                              os.path.join("Sprites", "Planes", "US_p40.png"),
                              angle,
                              hitbox,
                              ((10, 0), (0, 0), (-10, 0)),
                              100)
            else:  # Avião para pontos extras

                hitbox = Hitbox(position,
                                (0, -12, 35, 120),
                                (0, 5, 125, 35))

                enemy = Enemy(position,
                              drag,
                              10,
                              200.0,
                              1.0,
                              BulletType.SIMPLE,
                              0.1,
                              0.1,
                              stun_time,
                              '',  # Som
                              '',  # Som
                              size,
                              os.path.join("Sprites", "Planes", "USSR_Lagg3.png"),
                              angle,
                              hitbox,
                              ((10, 0), (0, 0), (-10, 0)),
                              1000)
        elif difficulty_range <= 50:

            random_number = randint(0, 2)

            if random_number == 0:

                hitbox = Hitbox(position,
                                (0, -12, 35, 120),
                                (0, 5, 125, 35))

                enemy = Enemy(position,
                              drag,
                              120,
                              100.0,
                              12.0,
                              BulletType.SIMPLE,
                              1.0,
                              1.2,
                              stun_time,
                              '',  # Som
                              '',  # Som
                              size,
                              os.path.join("Sprites", "Planes", "GER_bf110.png"),
                              angle,
                              hitbox,
                              ((10, 0), (0, 0), (-10, 0)),
                              250)

            else:

                hitbox = Hitbox(position,
                                (0, -12, 35, 120),
                                (0, 5, 125, 35))

                enemy = Enemy(position,
                              drag,
                              150,
                              90.0,
                              12.0,
                              BulletType.SIMPLE,
                              0.9,
                              1.0,
                              stun_time,
                              '',  # Som
                              '',  # Som
                              size,
                              os.path.join("Sprites", "Planes", "GER_He111.png"),
                              angle,
                              hitbox,
                              ((10, 0), (0, 0), (-10, 0)),
                              250)
        elif difficulty_range <= 75:

            random_number = randint(0, 2)

            if random_number == 0:

                hitbox = Hitbox(position,
                                (0, -12, 35, 120),
                                (0, 5, 125, 35))

                enemy = Enemy(position,
                              drag,
                              200,
                              80.0,
                              18.0,
                              BulletType.SIMPLE,
                              0.75,
                              1.5,
                              stun_time,
                              '',  # Som
                              '',  # Som
                              size,
                              os.path.join("Sprites", "Planes", "JAP_Ki21.png"),
                              angle,
                              hitbox,
                              ((10, 0), (0, 0), (-10, 0)),
                              500)

            else:

                hitbox = Hitbox(position,
                                (0, -12, 35, 120),
                                (0, 5, 125, 35))

                enemy = Enemy(position,
                              drag,
                              150,
                              100.0,
                              13.0,
                              BulletType.SIMPLE,
                              1.1,
                              1.2,
                              stun_time,
                              '',  # Som
                              '',  # Som
                              size,
                              os.path.join("Sprites", "Planes", "US_a26.png"),
                              angle,
                              hitbox,
                              ((10, 0), (0, 0), (-10, 0)),
                              500)
        else:

            random_number = randint(0, 2)

            if random_number == 0:

                hitbox = Hitbox(position,
                                (0, -12, 35, 120),
                                (0, 5, 125, 35))

                enemy = Enemy(position,
                              drag,
                              500,
                              50.0,
                              24.0,
                              BulletType.SIMPLE,
                              0.75,
                              1.3,
                              stun_time,
                              '',  # Som
                              '',  # Som
                              size,
                              os.path.join("Sprites", "Planes", "US_b17.png"),
                              angle,
                              hitbox,
                              ((10, 0), (0, 0), (-10, 0)),
                              750)

            else:

                hitbox = Hitbox(position,
                                (0, -12, 35, 120),
                                (0, 5, 125, 35))

                enemy = Enemy(position,
                              drag,
                              777,
                              40.0,
                              30.0,
                              BulletType.SIMPLE,
                              1.0,
                              1.5,
                              stun_time,
                              '',  # Som
                              '',  # Som
                              size,
                              os.path.join("Sprites", "Planes", "UK_Lancaster.png"),
                              angle,
                              hitbox,
                              ((10, 0), (0, 0), (-10, 0)),
                              750)

        return enemy


class AnimationFactory():

    '''
    Auxilia na criação de uma animação.
    '''

    path_lists: list

    def __init__(self):

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
        Gera uma entidade animada de explosão.
        '''

        size = (300, 300)

        index = 0

        if small:

            index = randint(0, 2)
        else:

            index = randint(3, 4)

        return Explosion(position, size, self.path_lists[index])


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

    active: bool
    position: list  # O sistema de coordenadas tem o ponto (0, 0) no topo da tela. eixo y invertido
    velocity: list  # Para cima: (0, -1), para baixo: (0, 1)
    drag: float
    size: tuple
    hitbox: Hitbox
    sprite: CustomSprite

    def __init__(self, position, drag, size, animate, sprite_path, angle, hitbox):

        self.active = True
        self.position = list(position)
        self.velocity = [0, 0]
        self.drag = drag
        self.size = size
        self.hitbox = None

        if hitbox is not None:

            self.hitbox = hitbox

        self.sprite = None

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

        self.sprite.update((self.position[0] - self.size[0] / 2,
                            self.position[1] - self.size[1] / 2))

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
        Retorna uma lista de hitbox. Pode ser None.
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
    Super Classe.
    '''

    direction: list  # Armazena a direção, assim conservamos a velocidade
    life: int
    max_life: int
    speed: float  # Pixels por segundo
    damage: float
    bullet_type: BulletType
    firerate: float
    firerate_cooldown: float
    fire_ready: bool
    armor: float
    stun_time: float  # Tempo depois de levar dano
    stun_cooldown: float
    stunned: bool
    attacking: bool
    destroyed: bool
    damaged: bool
    gun_points: list
    attack_sound: pygame.mixer.Sound
    damage_sound: pygame.mixer.Sound

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
                 gun_points):

        super().__init__(position, drag, size, False, sprite_path, angle, hitbox)

        self.direction = [0, 0]
        self.life = max_life  # Todas as entidades são instanciadas com a vida cheia
        self.max_life = max_life
        self.speed = speed
        self.damage = damage
        # integer que diz como o tiro sai do avião, vai de 0 até um número
        self.bullet_type = bullet_type
        self.firerate = firerate  # cadencia de tiros
        self.firerate_cooldown = 0.0
        self.fire_ready = True
        self.armor = armor
        self.stun_time = stun_time
        self.stun_cooldown = 0.0
        self.stunned = False
        self.attacking = False
        self.destroyed = False
        self.damaged = False
        self.gun_points = list(gun_points)
        # self.attack_sound = pygame.mixer.Sound() --som do tiro
        # self.damage_sound = pygame.mixer.Sound() --som quando a nave leva dano

    def change_life(self, value, armor_modifier=0.0):
        '''
        Aplica o dano
        '''

        if value < 0:

            if not self.stunned:

                self.life += int(value * (1.0 / (self.armor + armor_modifier / 100.0)))
                self.stunned = True
                self.damaged = True
        else:

            self.life += int(value)

            if self.life > self.max_life:

                self.life = self.max_life

        if self.life <= 0:

            self.life = 0
            self.active = False
            self.destroyed = True

    def stun_behaviour(self, tick):
        '''
        Processa o comportamento do atordoamento.
        '''

        if self.stunned:

            self.stun_cooldown += (1 / tick)

            if self.stun_cooldown > self.stun_time:

                self.stun_cooldown = 0.0
                self.stunned = False

    def firerate_behaviour(self, tick, firerate_modifier=0.0):
        '''
        Processa o cooldown do tiro.
        '''
        if not self.fire_ready:

            self.firerate_cooldown += (1 / tick)

            if self.firerate_cooldown > 1 / (self.firerate + firerate_modifier / 10.0):

                self.firerate_cooldown = 0.0
                self.fire_ready = True

    def get_damage(self, damage_modifier=0.0):
        '''
        Obtém o dano da aeronave.
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

    def get_gun_points(self):
        '''
        Retorna o offset das posições das armas.
        '''

        return self.gun_points

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
        Retorna verdadeiro caso a aeronave tenha sofrido dano.
        '''

        damaged = self.damaged
        self.damaged = False

        return damaged


class Player(Aircraft):

    '''
    Jogador.
    '''

    velocity_modifier: int
    damage_modifier: int
    firerate_modifier: int
    armor_modifier: int
    idle_sound: pygame.mixer.Sound

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
                 idle_sound,
                 size,
                 sprite_path,
                 angle,
                 hitbox,
                 gun_points):

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
                         hitbox,
                         gun_points)

        self.velocity_modifier = 0
        self.damage_modifier = 0
        self.firerate_modifier = 0
        self.armor_modifier = 0
        #self.idle_sound = pygame.mixer.Sound(idle_sound)

    def behaviour(self, events, screen_size, tick):
        '''
        Definição do comportamento do jogador.
        '''

        self.stun_behaviour(tick)
        self.firerate_behaviour(tick, self.firerate_modifier)

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

                if event.key == pygame.K_k:

                    self.attacking = True
            elif event.type == pygame.KEYUP:  # Caso uma tecla seja solta

                if event.key == pygame.K_a or event.key == pygame.K_d:  # Teclas horizontais

                    self.direction[0] = 0

                if event.key == pygame.K_s or event.key == pygame.K_w:  # Teclas verticais

                    self.direction[1] = 0

                if event.key == pygame.K_k:

                    self.attacking = False

            if self.direction[0] != 0:

                self.velocity[0] = self.direction[0] * (self.speed + self.velocity_modifier * 4)

            if self.direction[1] != 0:

                self.velocity[1] = self.direction[1] * (self.speed + self.velocity_modifier * 4)

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

    score_value: int

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
                 gun_points,
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
                         hitbox,
                         gun_points)

        self.score_value = score_value

    def behaviour(self, tick, screen_size, player_position, enemies):
        '''
        Definição do comportamento do inimigo.
        '''

        self.stun_behaviour(tick)
        self.firerate_behaviour(tick)

        self.velocity[1] = self.speed

        chase_player = True

        minimum_x_distance = self.size[0] - 100
        minimum_y_distance = self.size[1] - 100

        for enemy in enemies:

            if enemy != self:

                distance = sqrt((enemy.get_position()[0] - self.position[0])**2 +
                                (enemy.get_position()[1] - self.position[1])**2)

                if distance < minimum_x_distance:

                    if enemy.get_position()[0] < self.position[0]:  # O outro inimgo está a esquerda

                        self.velocity[0] = self.speed
                    else:

                        self.velocity[0] = -self.speed

                    chase_player = False
                # Evita que o inimigo procure o jogador logo depois de se afastar de outro inimigo
                elif distance < minimum_x_distance + 100:

                    chase_player = False

        if chase_player:

            if abs(player_position[0] - self.position[0]) > 100:

                if (player_position[1] - self.position[1]) > minimum_y_distance:

                    direction = -1
                else:

                    direction = 1

                if player_position[0] < self.position[0]:

                    self.velocity[0] = self.speed * direction
                else:

                    self.velocity[0] = self.speed * -direction

        if (player_position[0] - self.position[0]) < - 100:

            self.attacking = False
        elif (player_position[0] - self.position[0]) > 100:

            self.attacking = False
        else:

            self.attacking = True

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

    friendly: bool
    damage: int

    def __init__(self, position, size, sprite_path, hitbox, friendly, damage):

        super().__init__(position, 0.0, size, False, sprite_path, 0, hitbox)

        self.friendly = friendly
        self.damage = damage

    def behaviour(self, screen_size):
        '''
        Comportamento da bala.
        '''

        if self.position[0] <= 0 or              \
           self.position[0] >= screen_size[0] or \
           self.position[1] <= 0 or              \
           self.position[1] >= screen_size[1]:

            self.active = False

    def shoot(self, position, velocity, friendly, damage):
        '''
        Atira a bala.
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

        self.velocity[1] = constant_speed

    def behaviour(self, screen_size):
        '''
        Comportamento da núvem.
        '''

        if self.position[1] > screen_size[1] * 1.5:

            self.set_position((randint(0, screen_size[0]),
                               randint(-screen_size[1], -screen_size[1] // 2)))


class Explosion(Entity):

    '''
    Entidade que representa uma explosão, ela é usada apenas para fins visuais.
    '''

    def __init__(self, position, size, sprite_path):

        super().__init__(position, 0.0, size, True, sprite_path, 0, None)

        self.sprite.start_animation()

    def behaviour(self):
        '''
        Comportamento da explosão
        '''

        self.sprite.animate_frame()

        if not self.sprite.is_animating():

            self.active = False

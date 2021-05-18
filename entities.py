# -*- coding: utf-8 -*-

'''
Módulo para as entidades.
'''

import os

from random import randint
from enum import Enum
from math import sqrt

import pygame
from pygame.sprite import RenderUpdates

from graphics import CustomSprite
from physics import Hitbox
from states import Event

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
    inactive_bullets: list  # Usado no pooling
    inactive_bullets_limit: int
    enemies_limit: int
    enemy_factory: None
    elapsed_time: float
    event: Event

    def __init__(self, screen_size, inactive_bullets_limit, enemies_limit):

        self.score = 0
        self.screen_size = screen_size

        player_hitbox = Hitbox((self.screen_size[0] / 2, self.screen_size[1] / 2),
                               (0, 12, 35, 120),
                               (0, -5, 125, 35))

        self.player = Player((self.screen_size[0] / 2, self.screen_size[1] / 2),
                             -1.0,
                             100,
                             100.0,
                             10.0,
                             BulletType.SIMPLE,
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
                             ((-10, 0), (0, 0), (10, 0)))

        self.enemies = []
        self.bullets = []
        self.clouds = []
        self.inactive_bullets = []
        self.inactive_bullets_limit = inactive_bullets_limit
        self.enemies_limit = enemies_limit
        self.enemy_factory = EnemyFactory(self.screen_size, 300.0)
        self.elapsed_time = 1.0
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

    def get_entities(self, filter_dict):
        '''
        Retorna uma lista de entidades.
        '''

        if filter_dict:

            return {"Clouds": self.clouds,
                    "Bullets": self.bullets,
                    "Enemies": self.enemies,
                    "Player": self.player}
        else:

            return self.clouds + self.bullets + self.enemies + [self.player]

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

        if bullet_type == BulletType.SIMPLE:

            position_x = gun_points[1][0] + position[0]
            position_y = gun_points[1][1] + position[1]
            velocity_y = 500.0

            if friendly:

                velocity_y = -500.0

            if len(self.inactive_bullets) > 0:

                bullet = self.inactive_bullets[0]
                bullet.shoot((position_x, position_y), (0.0, velocity_y), friendly, damage)
                self.bullets.append(bullet)
                self.inactive_bullets.remove(bullet)
            else:

                bullet = Bullet((0, 0),
                                (3, 9),
                                os.path.join("Sprites", "Bullets", "Bullet.png"),
                                0,
                                None,
                                friendly,
                                damage)
                bullet.shoot((position_x, position_y), (0.0, velocity_y), friendly, damage)
                self.bullets.append(bullet)

    def enemy_generator(self):
        '''
        Gera os inimigos.
        '''

        enemy_count = 1 + int(self.elapsed_time / 20)

        if enemy_count > self.enemies_limit:

            enemy_count = self.enemies_limit

        while enemy_count - len(self.enemies) > 0:

            enemy = self.enemy_factory.generate_enemy(self.elapsed_time)

            if enemy is not None:

                self.enemies.append(enemy)

    def update(self, events, tick):
        '''
        Atualiza as entidades e seus comportamentos.
        '''

        self.player.behaviour(events, self.screen_size, tick)

        if self.player.is_attacking() and self.player.is_ready():

            self.generate_shot(self.player.get_position(),
                               self.player.get_gun_points(),
                               self.player.get_bullet_type(),
                               True,
                               self.player.get_damage(self.player.get_damage_modifier()))
            self.player.set_fire_state(False)

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

            if not enemy.is_active():

                if enemy.is_destroyed():

                    self.score += enemy.get_score_value()
                    self.player.change_life(10)

                self.enemies.remove(enemy)

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

        position = (randint(150, self.screen_size[0] - 150),
                    randint(-self.screen_size[1], -150))

        drag = -1.0
        stun_time = 0.25
        size = (300, 300)
        angle = 180

        if difficulty > self.max_difficulty:

            difficulty = self.max_difficulty

        difficulty_range = randint(0, int(100.0 * difficulty / self.max_difficulty))

        if difficulty_range <= 10:

            random_number = randint(0, 3)

            if random_number == 0:

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
                              '',  # Som
                              size,
                              os.path.join("Sprites", "Planes", "GER_bf109.png"),
                              angle,
                              hitbox,
                              ((10, 0), (0, 0), (-10, 0)),
                              100)
            elif random_number == 1:

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
                              '',  # Som
                              size,
                              os.path.join("Sprites", "Planes", "JAP_a6m.png"),
                              angle,
                              hitbox,
                              ((10, 0), (0, 0), (-10, 0)),
                              100)
            else:

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
                              '',  # Som
                              size,
                              os.path.join("Sprites", "Planes", "US_p40.png"),
                              angle,
                              hitbox,
                              ((10, 0), (0, 0), (-10, 0)),
                              100)

        return enemy


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

    def __init__(self, position, drag, size, sprite_path, angle, hitbox):

        self.active = True
        self.position = list(position)
        self.velocity = [0, 0]
        self.drag = drag
        self.size = size
        self.hitbox = None

        if hitbox is not None:

            self.hitbox = hitbox

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
    gun_points: list
    attack_sound: pygame.mixer.Sound
    damage_sound: pygame.mixer.Sound
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

        super().__init__(position, drag, size, sprite_path, angle, hitbox)

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
                         idle_sound,
                         size,
                         sprite_path,
                         angle,
                         hitbox,
                         gun_points)

        self.velocity_modifier = 0
        self.damage_modifier = 0
        self.firerate_modifier = 0
        self.armor_modifier = 0

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
                 idle_sound,
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
                         idle_sound,
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

                distance = sqrt((enemy.get_position()[0] - self.position[0])**2 + \
                                (enemy.get_position()[1] - self.position[1])**2)

                if distance < minimum_x_distance:

                    if enemy.get_position()[0] < self.position[0]: # O outro inimgo está a esquerda

                        self.velocity[0] = self.speed
                    else:

                        self.velocity[0] = -self.speed

                    chase_player = False
                # Evita que o inimigo procure o jogador logo depois de se afastar de outro inimigo
                elif distance < minimum_x_distance + 100:

                    chase_player = False

        if chase_player:

            if (player_position[0] - self.position[0]) < - 100:

                self.velocity[0] = -self.speed
                self.attacking = False
            elif (player_position[0] - self.position[0]) > 100:

                self.velocity[0] = self.speed
                self.attacking = False
            else:

                self.attacking = True

            if (player_position[1] - self.position[1]) < minimum_y_distance and \
               (player_position[1] - self.position[1]) > -minimum_y_distance:

                if (player_position[0] - self.position[0]) < 0:

                    self.velocity[0] = self.speed
                else:

                    self.velocity[0] = -self.speed

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

    def __init__(self, position, size, sprite_path, angle, hitbox, friendly, damage):

        super().__init__(position, 0.0, size, sprite_path, angle, hitbox)

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

        super().__init__(position, 0.0, size, sprite_path, angle, None)

        self.velocity[1] = constant_speed

    def behaviour(self, screen_size):
        '''
        Comportamento da núvem.
        '''

        if self.position[1] > screen_size[1] * 1.5:

            self.set_position((randint(0, screen_size[0]),
                               randint(-screen_size[1], -screen_size[1] // 2)))

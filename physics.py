# -*- coding: utf-8 -*-

'''
Módulo para a física.
'''

import pygame

from states import State


class PhysicsManager():

    '''
    Gerencia a física
    '''

    def update(self, state, tick, entities):
        '''
        Atualiza a física.
        '''

        if state == State.GAMEPLAY:

            clouds = entities["Clouds"]
            bullets = entities["Bullets"]
            enemies = entities["Enemies"]
            player = entities["Player"]

            all_entities = clouds + bullets + enemies + [player]

            # Calcula a nova posição e velocidade
            for entity in all_entities:

                position = entity.get_position()
                velocity = entity.get_velocity()
                drag = entity.get_drag()

                new_position_x = position[0] + velocity[0] / tick
                new_position_y = position[1] + velocity[1] / tick

                new_velocity_x = velocity[0] * (1.0 - drag / tick)
                new_velocity_y = velocity[1] * (1.0 - drag / tick)

                entity.set_position((new_position_x, new_position_y))
                entity.set_velocity((new_velocity_x, new_velocity_y))

            # Resolve as colisões

            # Jogador x Inimigos
            player_rects = player.get_hitbox()

            for enemy in enemies:

                collided = False

                for rect in player_rects:

                    if rect.collidelist(enemy.get_hitbox()) != -1:

                        collided = True
                        break

                if collided:

                    enemy.change_life(-15)
                    player.change_life(-15, player.get_armor_modifier())

            for bullet in bullets:

                if bullet.is_friendly():  # Bala x inimigo

                    for enemy in enemies:

                        for rect in enemy.get_hitbox():

                            if rect.collidepoint(bullet.get_position()):

                                enemy.change_life(bullet.get_damage())
                                bullet.deactivate()
                else:  # Bala x jogador

                    for rect in player.get_hitbox():

                        if rect.collidepoint(bullet.get_position()):

                            player.change_life(bullet.get_damage(), player.get_armor_modifier())
                            bullet.deactivate()


class Hitbox():

    '''
    Hitbox. Aceita rects como argumento, definidos como (x, y, largura, altura). A posição (x, y)
    tem a origem no argumento "posição".
    '''

    position: list
    hitbox_list: list
    hitbox_count: int

    def __init__(self, position, *rects):

        self.position = list(position)
        self.hitbox_list = []
        self.hitbox_count = len(rects)

        for rect in rects:

            self.hitbox_list.append(pygame.Rect(self.position[0] + rect[0] - rect[2] / 2,
                                                self.position[1] + rect[1] - rect[3] / 2,
                                                rect[2],
                                                rect[3]))

    def update(self, position):
        '''
        Atualiza a posição da hitbox.
        '''

        position = list(map(int, position))

        offset_x = position[0] - self.position[0]
        offset_y = position[1] - self.position[1]

        self.position = list(position)

        for i in range(self.hitbox_count):

            self.hitbox_list[i] = self.hitbox_list[i].move(offset_x, offset_y)

    def get_hitbox(self):
        '''
        Retorna os rects.
        '''

        return self.hitbox_list

# -*- coding: utf-8 -*-

'''
Módulo para a física.
'''

from states import State


class PhysicsManager():

    '''
    Gerencia a física
    '''

    drag: float  # Arrasto (No jogo o arrasto é igual para todos)

    def __init__(self, drag_acceleration):

        self.drag = drag_acceleration

    def update(self, state, tick, entities):
        '''
        Atualiza a física.
        '''

        if state == State.GAMEPLAY:

            # Calcula a nova posição e velocidade
            for entity in entities:

                position = entity.get_position()
                velocity = entity.get_velocity()

                new_position_x = position[0] + velocity[0] * (1 / tick)
                new_position_y = position[1] + velocity[1] * (1 / tick)

                new_velocity_x = velocity[0] * (1.0 + self.drag * (1 / tick))
                new_velocity_y = velocity[1] * (1.0 + self.drag * (1 / tick))

                entity.set_position((new_position_x, new_position_y))
                entity.set_velocity((new_velocity_x, new_velocity_y))

            # Resolve as colisões

            # Aplica os resultados das colisões

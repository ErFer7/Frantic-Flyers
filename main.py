# -*- coding: utf-8 -*-

'''
Jogo para a conclusão da disciplina de programação orientada a objetos II.

Autores: Arthur Medeiros Machado e Eric Fernandes Evaristo.
Projeto: Frantic Flyers.

Manutenção atual feita por: Eric Fernandes Evaristo
'''

from source.game_system import GameManager

VERSION = "v1.1"

game_manager = GameManager(VERSION)  # Instancia o jogo
game_manager.run_game(75)  # Roda o jogo

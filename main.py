# -*- coding: utf-8 -*-

'''
Jogo para a conclusão da disciplina de programação orientada a objetos II.

Autores: Arthur Medeiros Machado e Eric Fernandes Evaristo.
Projeto: Frantic Flyers.
'''

from game_system import GameManager

VERSION = "v0.16"

game_manager = GameManager(VERSION)  # Instancia o jogo
game_manager.run_game(60)  # Roda o jogo

# -*- coding: utf-8 -*-

'''
Jogo para a conclusão da disciplina de programação orientada a objetos II.

Autores: Arthur Medeiros Machado e Eric Fernandes Evaristo.
Projeto: Frantic Flyers.

Para fazer:

* Som e música
'''

from game_system import GameManager

VERSION = "v0.15"

game_manager = GameManager(VERSION)
game_manager.run_game(60)

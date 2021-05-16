# -*- coding: utf-8 -*-

'''
Jogo para a conclusão da disciplina de programação orientada a objetos II.

Autores: Arthur Medeiros Machado e Eric Fernandes Evaristo.
Projeto: Frantic Flyers.

Para fazer:

* Sistema de interfaces completo
    * Gameover
* Sistema de entidades
    * Gerenciador
    * Entidades
    * Jogador
    * Inimigos
* Sistema de física
* Sistema de gráficos
* Polir o jogo e consertar tudo
    * Testar performance
    * Testar memória
'''

from game_system import GameManager

VERSION = "v0.6"

game_manager = GameManager(VERSION)
game_manager.run_game(60)

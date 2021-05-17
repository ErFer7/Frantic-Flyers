# -*- coding: utf-8 -*-

'''
Jogo para a conclusão da disciplina de programação orientada a objetos II.

Autores: Arthur Medeiros Machado e Eric Fernandes Evaristo.
Projeto: Frantic Flyers.

Para fazer:

* Sistema de entidades
    * Gerenciador
    * Inimigos
* Sistema gráfico
    * Animações
* Som e música
* Polir o jogo e consertar tudo
    * Testar performance
    * Testar memória
'''

from game_system import GameManager

VERSION = "v0.9"

game_manager = GameManager(VERSION)
game_manager.run_game(60)

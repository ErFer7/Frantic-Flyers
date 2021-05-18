# -*- coding: utf-8 -*-

'''
Jogo para a conclusão da disciplina de programação orientada a objetos II.

Autores: Arthur Medeiros Machado e Eric Fernandes Evaristo.
Projeto: Frantic Flyers.

Para fazer:

* Sistema de entidades
    * Todos os tipos de bala
    * Fábrica de inimigos
    * Pontos de modificação calculados
* Sistema gráfico
    * Animações
* Som e música
* Polir o jogo e consertar tudo
'''

from game_system import GameManager

VERSION = "v0.10.1"

game_manager = GameManager(VERSION)
game_manager.run_game(60)

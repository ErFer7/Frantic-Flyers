# -*- coding: utf-8 -*-

'''
Módulo para o sistema de arquivos.
'''

import json
from re import sub

import pygame

from os import listdir, makedirs
from os.path import isfile, join, exists, dirname

class FileSystem():

    '''
    Classe para gerenciar um arquivo em forma de lista.
    '''

    path: str  # Local do arquivo de dados
    data: dict  # Dicionário para armazenar dados

    def __init__(self, path):

        self.path = path
        self.data = {}

        # Caso o arquivo exista ele é lido
        if exists(path):

            with open(path, 'r', encoding="utf-8") as file:

                data_json = file.read()

            self.data = json.loads(data_json)
        else:  # Cria a pasta caso ela não exista

            directory = dirname(path)

            if not exists(directory):

                makedirs(directory)

    def write_file(self):
        '''
        Salva os dados no arquivo.
        '''

        with open(self.path, 'w', encoding="utf-8") as file:

            data_json = json.dumps(self.data, indent=4)  # indent é usado para formatar o json
            file.write(data_json)

    def set_data(self, data: dict):
        '''
        Define um dicionário que é usado para os dados.
        '''

        self.data = data
        self.write_file()

    def get_data(self):
        '''
        Retorna os dados.
        '''

        return self.data


class AssetContainer():

    '''
    Classe para representar um objeto que contém os assets.
    '''

    audio: dict
    sprites: dict

    def __init__(self):

        self.audio = self.build_dir_dict(join("assets", "audio"), "audio")
        self.sprites = self.build_dir_dict(join("assets", "sprites"), "sprite")

    def build_dir_dict(self, path: str, mode: str):
        '''
        Constrói um dicionário com os diretórios
        '''

        dir_dict = {}

        for file in listdir(path):

            if not isfile(join(path, file)):
                dir_dict[file] = self.build_dir_dict(join(path, file), mode)
            else:

                if mode == "audio":
                    dir_dict[file] = pygame.mixer.Sound(join(path, file))
                else:
                    dir_dict[file] = pygame.image.load(join(path, file)).convert_alpha()

        return dir_dict

    def get_asset(self, mode: str, *path):
        '''
        Obtém um asset.
        '''

        asset = None

        if mode == "audio":

            asset = self.audio
            for subpath in path:
                asset = asset[subpath]
        else:

            asset = self.sprites
            for subpath in path:
                asset = asset[subpath]

        return asset

    def get_audio(self, *path):
        '''
        Obtém um áudio.
        '''

        return self.get_asset("audio", *path)

    def get_sprite(self, *path):
        '''
        Obtém um sprite.
        '''

        return self.get_asset("sprite", *path)

# -*- coding: utf-8 -*-

'''
Módulo para o sistema de arquivos.
'''

import os
import json


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
        if os.path.exists(path):

            with open(path, 'r') as file:

                data_json = file.read()

            self.data = json.loads(data_json)

    def write_file(self):
        '''
        Salva os dados no arquivo.
        '''

        with open(self.path, 'w') as file:

            data_json = json.dumps(self.data, indent=4)  # indent é usada para formatar o json
            file.write(data_json)

    def set_element(self, element_id: str, element_data: list):
        '''
        Insere ou edita dados.
        Essencialmente define um elemento.
        '''

        self.data[element_id] = element_data
        self.write_file()

    def remove_element(self, element_id: str):
        '''
        Remove dados.
        '''

        del self.data[element_id]
        self.write_file()

    def get_matrix_data(self):
        '''
        Retorna uma matriz de dados.
        '''

        matrix = []

        for k in self.data.keys():

            element = [k] + self.data[k]
            matrix.append(element)

        return matrix

    def get_data(self):
        '''
        Retorna os dados
        '''

        return self.data

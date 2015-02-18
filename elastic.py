#-*- coding: utf-8 -*-

'''
Uma micro biblioteca para simplificar a comunicação com o Elastic Search.
'''

from elasticsearch import Elasticsearch, TransportError
import time


class ElasticSync(object):
    '''
    Esta classe serve para encapsular e simplificar as operações básicas
    necessárias para fazer a comunicação com o Elastic Search.
    No momento, tem a coleção 'superdupertable' por padrão já no código.
    '''
    es = None
    index_name = None
    doc_type = 'superdupertable'

    def __init__(self, index_name):
        self.es = Elasticsearch()
        self.index_name = index_name
        self.es.indices.create(
            self.index_name,
            {"settings": {"number_of_shards": 1, "number_of_replicas": 1}},
            ignore=400)

    def select(self, uid):
        '''
        Recupera um objeto com base na chave primária (uid/_id).
        '''
        while True:
            try:
                res = self.es.get(
                    index=self.index_name,
                    doc_type=self.doc_type,
                    id=unicode(uid),
                    ignore=404
                )
                break
            except TransportError:
                time.sleep(1)

        if not res['found']:
            return None
        return res['_source']

    def select_all(self, last_change, end_time):
        '''
        Recupera todos os objetos entre o período de tempo
        especificado.
        '''
        res = self.es.search(
            index=self.index_name,
            doc_type=self.doc_type,
            body={
                'query': {
                    'range': {
                        'last_change': {'gte': last_change, 'lte': end_time}
                    }
                }
            }
        )
        return res['hits']

    def update(self, data, _id):
        '''
        Atualiza, ou insere se não existerem, os dados de `data`
        na coleção.
        Se o `_id` for especificado vai buscar o objeto exato na
        coleção (parâmetro colocado para evitar geração de duplicidades).
        '''

        res = self.es.index(
            op_type='index',
            index=self.index_name,
            doc_type=self.doc_type,
            body=data,
            id=_id)
        time.sleep(0.5)
        return res

    def insert(self, data, _id=None):
        '''
        Insere se não existerem, os dados de `data`
        na coleção.
        Se o `_id` for especificado vai buscar o objeto exato na
        coleção (parâmetro colocado para evitar geração de duplicidades).
        '''

        res = self.es.index(
            index=self.index_name,
            doc_type=self.doc_type,
            body=data,
            id=_id or data['uid'],
            refresh=True)
        time.sleep(0.5)
        return res

#-*- coding: utf-8 -*-

'''
Uma micro biblioteca para simplificar a comunicação com o Cassandra.
'''

from cassandra import InvalidRequest
from cassandra.cluster import Cluster
from cassandra.query import dict_factory

from datetime import datetime
from helpers import unitime
import uuid


class CassandraSync(object):
    '''
    Esta classe serve para encapsular e simplificar as operações básicas
    necessárias para fazer a comunicação com o Cassandra.
    No momento, tem tabela 'superdupertable' por padrão já no código.
    '''
    cluster = None
    session = None
    keyspace = None

    def __init__(self, keyspace):
        self.cluster = Cluster()
        self.keyspace = keyspace
        self.session = self.cluster.connect(self.keyspace)
        self.session.row_factory = dict_factory

    def __del__(self):
        self.cluster.shutdown()

    def select(self, uid):
        '''
        Recupera um objeto com base na chave primária (uid).
        '''
        row = self.session.execute(
            '''SELECT *
            FROM superdupertable
            WHERE uid = %s;
            ''', (uid,))
        if len(row) == 0:
            return None
        return row[0]

    def select_all(self, last_change, end_time):
        '''
        Recupera todos os objetos entre o período de tempo
        especificado.
        '''
        rows = self.session.execute(
            '''SELECT *
            FROM superdupertable
            WHERE last_change >= %s
            AND last_change <= %s
            ALLOW FILTERING;
            ''', (last_change, end_time))
        return rows

    def insert(self, data):
        if isinstance(data['uid'], basestring):
            data['uid'] = uuid.UUID(data['uid'])
        if isinstance(data['last_change'], basestring):
            data['last_change'] = datetime.strptime(
                data['last_change'], '%Y-%m-%dT%H:%M:%S.%f')

        self.session.execute(
            '''INSERT INTO superdupertable (uid, name, body, last_change)
            VALUES (%s, %s, %s, %s)''',
            (data['uid'], data['name'], data['body'], data['last_change'])
        )

    def delete(self, uid):
        '''
        Apaga um objeto com base na chave primária (uid).
        '''
        if isinstance(uid, basestring):
            uid = uuid.UUID(uid)

        self.session.execute(
            '''DELETE FROM superdupertable
            WHERE uid = %s''',
            (uid,)
        )

    def update(self, data):
        '''
        Atualiza, ou insere se não existerem, os dados de `data`
        na tabela (seria mais correto chamar de upsert).
        '''
        if isinstance(data['uid'], basestring):
            data['uid'] = uuid.UUID(data['uid'])
        if isinstance(data['last_change'], basestring):
            data['last_change'] = unitime(data['last_change'])

        try:
            self.session.execute(
                '''UPDATE superdupertable
                SET name = %s, body = %s, last_change = %s
                WHERE uid = %s''',
                (data['name'], data['body'], data['last_change'], data['uid'])
            )
        except InvalidRequest:
            #cassandra não aceita update de chaves primárias
            #então, apaga e recria objeto com os dados atualizados
            self.delete(data['uid'])
            self.insert(data)

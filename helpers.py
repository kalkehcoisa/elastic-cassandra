#-*- coding: utf-8 -*-

'''
Funções auxiliares para o uso e desenvolvimento do script.
'''

from datetime import datetime
from random import randint


def unitime(data):
    '''
    Converte unicode "padrão" - unicode(datetime) - de volta para datetime.
    '''
    return datetime.strptime(data, '%Y-%m-%dT%H:%M:%S.%f')


def new_cassandra_item(cass, uid):
    '''
    Gera um item, mais ou menos, aleatório no cassandra para
    testar o funcionamento do sistema de sincronização.
    '''
    return cass.insert({
        'uid': uid,
        'name': 'cassandra: ' + str(randint(1000, 5000000)),
        'body': 'asdhgahkjsdhskad askdjhjaskdhj',
        'last_change': datetime.now()})


def new_elastic_item(elas, uid):
    '''
    Gera um item, mais ou menos, aleatório no elastic search
    para testar o funcionamento do sistema de sincronização.
    '''
    return elas.es.create(
        index=elas.index_name,
        doc_type=elas.doc_type,
        id=unicode(uid),
        body={
            'uid': unicode(uid),
            'name': 'elastic: ' + str(randint(1000, 5000000)),
            'body': 'asdhgahkjsdhskad askdjhjaskdhj',
            'last_change': datetime.now()})

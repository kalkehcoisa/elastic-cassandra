#-*- coding: utf-8 -*-

'''
Este é um pequeno projeto que faz a sincronização de dados entre o
Elastic Search 1.4.3 e o Cassandra 2.0.9-1 utilizando Python 2.7.

A sincronização é feita entre a tabela "superdupertable" do keyspace
"mykeyspace" do Cassandra com a coleção "superdupertable" do índice
"mykeyspace" do Elastic Search.

Obs: os nomes são iguais, mas nada impede de editá-los no código. O script
não os recebe como parâmetros/configurações. Poderia ser um próximo update.
'''

from cass import CassandraSync
from datetime import datetime
from elastic import ElasticSync
from helpers import unitime
import sys
import time
import uuid


def sync(start_time, end_time, interval, cass, elas):
    '''
    Sincroniza os dados entre o Cassandra e o Elastic Search.
    `start_time`: datetime de início para filtrar objetos por last_change
    `end_time`: datetime de término para filtrar objetos por last_change
    `cass`: objeto CassandraSync.
    `elas`: objeto ElasticSync.

    Obs: se dois objetos tiverem o last_change idêntico, são considerados
    idênticos e não são sincronizados.
    '''

    #sincroniza os dados do elastic para o cassandra
    #percorre todos os dados novos/atualizados do elastic
    #a partir de start_time até end_time (agora)
    #elastic primeiro por ser mais lento com os inserts, replicações, etc
    for hit in elas.select_all(start_time, end_time)['hits']:
        hit['_source']['uid'] = uuid.UUID(hit['_source']['uid'])
        there = cass.select(hit['_source']['uid'])
        if there is not None:
            #se encontrou no cassandra, verifica em que lado será o update
            hit_time = unitime(hit['_source']['last_change'])
            if there['last_change'] <= hit_time:
                #elastic tem o mais recente
                cass.update(hit['_source'])
                print 'EC: Update de E -> C: %s' % hit['_source']['uid']
            elif there['last_change'] > hit_time:
                #cassandra tem o mais recente
                elas.update(there, hit['_id'])
                print 'EC: Update de C -> E: %s' % hit['_source']['uid']
        else:
            #se não encontrou ninguém, insert
            cass.insert(hit['_source'])
            print 'EC: Insert no Cassandra: %s' % hit['_source']['uid']

    time.sleep(interval)

    #sincroniza os dados do cassandra para o elasticsearch
    #percorre todos os dados novos/atualizados do cassandra
    #a partir de start_time até end_time (agora)
    for row in cass.select_all(start_time, end_time):
        there = elas.select(row['uid'])
        row['uid'] = unicode(row['uid'])
        if there:
            #se encontrou no elastic, verifica em que lado será o update
            hit_time = unitime(there['last_change'])
            if hit_time <= row['last_change']:
                #cassandra tem o mais recente
                elas.update(row, there['uid'])
                print 'CE: Update de C -> E: %s' % row['uid']
            elif hit_time > row['last_change']:
                #elastic tem o mais recente
                cass.update(there)
                print 'CE: Update de E -> C: %s' % row['uid']
        else:
            #se não encontrou ninguém, insert
            elas.insert(row)
            print 'CE: Insert no Elastic: %s' % row['uid']


if __name__ == '__main__':
    #inicia a data inicial de varredura em 0
    #assim, varre todos os valores da tabela/coleção na primeira execução
    START_TIME = datetime.fromtimestamp(0)

    #intervalo em segundos entre uma sincronização e outra
    #obtido a partir da linha de comando python task.py [tempo]
    #padrão: 1 segundo
    SYNC_INTERVAL = float(sys.argv[1] or 100) if len(sys.argv) > 1 else 1

    cass = CassandraSync('mykeyspace')
    elas = ElasticSync('mykeyspace')

    #laço de repetição sem fim para criar um "daemon"
    while True:
        #valor usado para limitar a varredura a todos os dados
        #inseridos até o momento atual
        NEW_TIME = datetime.now()

        print 'Syncing... %s - %s' % (START_TIME, NEW_TIME), '\n'
        sync(START_TIME, NEW_TIME, SYNC_INTERVAL, cass, elas)

        #move o espaço de varredura para a próxima execução
        START_TIME = NEW_TIME

        #fica parado por um tempo até rodar de novo
        time.sleep(SYNC_INTERVAL)
        print '\n\n'

    del cass
    del elas

#-*- coding: utf-8 -*-

from cass import CassandraSync
from cassandra.cluster import Cluster
from datetime import datetime
from elastic import ElasticSync
from elasticsearch import Elasticsearch
from task import sync
import time
import unittest
import uuid


class UnitTestViews(unittest.TestCase):
    cass = None
    elas = None
    keyspace = 'testkeyspace'
    index_name = 'testkeyspace'

    def setUp(self):
        temp = Cluster(['127.0.0.1']).connect()
        temp.execute('''
            CREATE KEYSPACE IF NOT EXISTS %s
            WITH REPLICATION = {
                'class' : 'SimpleStrategy',
                'replication_factor' : 1 };
        ''' % (self.keyspace))

        temp = Cluster(['127.0.0.1']).connect(self.keyspace)
        temp.execute('''
            DROP TABLE IF EXISTS superdupertable;
        ''')
        temp.execute('''
            CREATE TABLE IF NOT EXISTS superdupertable (
              uid UUID,
              name text,
              body text,
              last_change timestamp,
              PRIMARY KEY (uid, last_change)
            );
        ''')
        self.cass = CassandraSync(self.keyspace)

        temp = Elasticsearch()
        temp.indices.create(
            self.index_name,
            {"settings": {"number_of_shards": 2, "number_of_replicas": 1}},
            ignore=400)
        self.elas = ElasticSync(self.index_name)

    def tearDown(self):
        self.cass.session.execute('''
            DROP KEYSPACE IF EXISTS %s;
        ''' % (self.keyspace))
        del self.cass

        self.elas.es.indices.delete(
            index=self.index_name,
            ignore=[400, 404])
        del self.elas

    def test_run(self):
        '''
        Testa uma execução simples do script.
        '''
        START_TIME = 0
        NEW_TIME = datetime.now()
        sync(START_TIME, NEW_TIME, self.cass, self.elas)

    def test_insert_cass_to_elas(self):
        '''
        Testa sincronização de dados de inserções no Cassandra
        para o Elastic Search.
        '''

        from helpers import new_cassandra_item
        for i in xrange(10):
            uid = uuid.uuid4()
            new_cassandra_item(self.cass, uid)
            response = self.cass.select(uid)
            self.assertTrue('body' in response)

        START_TIME = datetime.fromtimestamp(0)
        NEW_TIME = datetime.now()

        itens = self.elas.select_all(START_TIME, NEW_TIME)
        self.assertEqual(itens['total'], 0)

        sync(START_TIME, NEW_TIME, self.cass, self.elas)

        itens = self.elas.select_all(START_TIME, NEW_TIME)
        self.assertEqual(itens['total'], 10)

    def test_insert_elas_to_cass(self):
        '''
        Testa sincronização de dados de inserções no Elastic
        Search para o Cassandra.
        '''

        from helpers import new_elastic_item
        for i in xrange(10):
            uid = uuid.uuid4()
            new_elastic_item(self.elas, uid)
            response = self.elas.select(uid)
            self.assertTrue('body' in response)
        time.sleep(5)

        START_TIME = datetime.fromtimestamp(0)
        NEW_TIME = datetime.now()

        itens = self.cass.select_all(START_TIME, NEW_TIME)
        self.assertEqual(len(itens), 0)

        sync(START_TIME, NEW_TIME, self.cass, self.elas)

        itens = self.cass.select_all(START_TIME, NEW_TIME)
        self.assertEqual(len(itens), 10)

    def test_insert_both(self):
        '''
        Testa sincronização de dados inseridos em ambos.
        '''

        from helpers import new_elastic_item, new_cassandra_item

        for i in xrange(10):
            uid = uuid.uuid4()
            new_cassandra_item(self.cass, uid)
            uid = uuid.uuid4()
            new_elastic_item(self.elas, uid)
        time.sleep(5)

        START_TIME = datetime.fromtimestamp(0)
        NEW_TIME = datetime.now()
        SYNC_INTERVAL = 2

        itens = self.cass.select_all(START_TIME, NEW_TIME)
        self.assertEqual(len(itens), 10)
        itens = self.elas.select_all(START_TIME, NEW_TIME)
        self.assertEqual(itens['total'], 10)

        for i in xrange(3):
            NEW_TIME = datetime.now()
            sync(START_TIME, NEW_TIME, SYNC_INTERVAL, self.cass, self.elas)
            START_TIME = NEW_TIME
            time.sleep(SYNC_INTERVAL)

        itens = self.cass.select_all(datetime.fromtimestamp(0), datetime.now())
        self.assertEqual(len(itens), 20)
        itens = self.elas.select_all(datetime.fromtimestamp(0), datetime.now())
        self.assertEqual(itens['total'], 20)

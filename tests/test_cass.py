#-*- coding: utf-8 -*-

from datetime import datetime
from cass import CassandraSync
from cassandra.cluster import Cluster
import time
import unittest
import uuid


class UnitTestViews(unittest.TestCase):
    cass = None
    keyspace = 'testkeyspace'

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

    def tearDown(self):
        self.cass.session.execute(
            '''DROP KEYSPACE IF EXISTS testkeyspace;''')
        del self.cass

    def test_insert(self):
        '''
        Testa a inserção de um item aleatório.
        '''
        from helpers import new_cassandra_item
        uid = uuid.uuid4()
        new_cassandra_item(self.cass, uid)
        response = self.cass.select(uid)
        self.assertTrue('body' in response)

    def test_select_all(self):
        '''
        Testa inserir e recuperar vários itens.
        '''
        from helpers import new_cassandra_item

        for i in xrange(500):
            new_cassandra_item(self.cass, uuid.uuid4())

        time.sleep(1)
        start = datetime.now()
        for i in xrange(500):
            new_cassandra_item(self.cass, uuid.uuid4())
        end = datetime.now()
        time.sleep(1)

        for i in xrange(500):
            new_cassandra_item(self.cass, uuid.uuid4())

        time.sleep(5)
        response = self.cass.select_all(0, datetime.now())
        self.assertEqual(len(response), 1500)

        response = self.cass.select_all(start, end)
        self.assertEqual(len(response), 500)

    def test_update(self):
        '''
        Testa update de um item.
        '''
        from helpers import new_cassandra_item

        uid = uuid.uuid4()
        item = new_cassandra_item(self.cass, uid)
        item = self.cass.select(uid)

        name = 'updated1 \o/'
        item['name'] = name
        self.cass.update(data=item)
        item = self.cass.select(uid=uid)
        self.assertEqual(item['name'], name)

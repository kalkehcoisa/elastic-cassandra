#-*- coding: utf-8 -*-

from datetime import datetime
from elastic import ElasticSync
from elasticsearch import Elasticsearch
import time
import unittest
import uuid


class UnitTestViews(unittest.TestCase):
    elas = None
    index_name = 'testkeyspace'

    def setUp(self):
        temp = Elasticsearch()
        temp.indices.create(
            self.index_name,
            {"settings": {"number_of_shards": 2, "number_of_replicas": 1}},
            ignore=400)
        self.elas = ElasticSync(self.index_name)

    def tearDown(self):
        self.elas.es.indices.delete(
            index=self.index_name,
            ignore=[400, 404])
        del self.elas

    def test_create_delete_index(self):
        '''
        Testa a criação e remoção de um índice.
        '''
        response = self.elas.es.indices.create(
            index=self.index_name,
            ignore=400)
        self.assertTrue('status' in response)

        response = self.elas.es.indices.delete(
            index=self.index_name,
            ignore=[400, 404])
        self.assertTrue(response['acknowledged'])

    def test_insert(self):
        '''
        Testa a inserção de um item aleatório.
        '''
        from helpers import new_elastic_item
        uid = uuid.uuid4()
        response = new_elastic_item(self.elas, uid)
        self.assertTrue(response['created'])

    def test_get(self):
        '''
        Testa recuperar um item.
        '''
        from helpers import new_elastic_item
        uid = uuid.uuid4()
        response = new_elastic_item(self.elas, uid)
        self.assertTrue(response['created'])

        response = self.elas.select(uid)
        self.assertNotEqual(response, None)

    def test_select_all(self):
        '''
        Testa inserir e recuperar vários itens.
        '''
        from helpers import new_elastic_item

        for i in xrange(500):
            new_elastic_item(self.elas, uuid.uuid4())

        time.sleep(1)
        start = datetime.now()
        for i in xrange(500):
            new_elastic_item(self.elas, uuid.uuid4())
        end = datetime.now()
        time.sleep(1)

        for i in xrange(500):
            new_elastic_item(self.elas, uuid.uuid4())

        time.sleep(5)
        response = self.elas.select_all(0, datetime.now())
        self.assertEqual(response['total'], 1500)

        response = self.elas.select_all(start, end)
        self.assertEqual(response['total'], 500)

    def test_update(self):
        '''
        Testa update de um item.
        '''
        from helpers import new_elastic_item

        uid = uuid.uuid4()
        item = new_elastic_item(self.elas, uid)
        item = self.elas.select(uid)

        name = 'updated1 \o/'
        item['name'] = name
        self.elas.update(_id=uid, data=item)
        item = self.elas.select(uid=uid)
        self.assertEqual(item['name'], name)

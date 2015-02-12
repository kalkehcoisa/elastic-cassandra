#-*- encoding: utf-8 -*-

from cassandra.cluster import Cluster
from datetime import datetime
import uuid
cluster = Cluster()
session = cluster.connect('mykeyspace')

#testando inserts
session.execute(
    """
    INSERT INTO superdupertable (uid, name, body, insert_time)
    VALUES (%s, %s, %s, %s)
    """,
    (uuid.uuid4(), "John O'Reilly", 'Some body content', datetime.now())
)

#testando selects
rows = session.execute('SELECT uid, name, body FROM superdupertable')
for row in rows:
    print row.uid, row.name, row.body
cluster.shutdown()


############## elastic search ###############
#sim, este arquivo está uma baita bagunça
from elasticsearch import Elasticsearch
es = Elasticsearch()

# WRITE TO ES
doc = {
    'uid': unicode(uuid.uuid4()),
    'name': 'fuin',
    'body': u'béééééééééééé béééééééééééé',
    'insert_time': datetime.now()
}

#cria/atualiza um documento
res = es.index(index="mykeyspace", doc_type='superdupertable', id=1, body=doc)
print res

es.indices.refresh(index="mykeyspace")

#recupera um documento por id
res = es.get(index="mykeyspace", doc_type='superdupertable', id=1)
print(res['_source'])

#busca documentos
res = es.search(
    index='mykeyspace',
    doc_type='superdupertable',
    body={
        'query': {
            'range': {
                'insert_time': {'from': '20100101', 'to': '20140101'}
            }
        }
    }
)

print("Got %d Hits" % res['hits']['total'])

for hit in res['hits']['hits']:
    print("%(postDate)s %(user)s: %(message)s" % hit["_source"])

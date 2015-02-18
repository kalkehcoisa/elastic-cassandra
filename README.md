Sincronizador Python
========================
  
### Sobre

 Este é um pequeno projeto que faz a sincronização de dados entre o Elastic Search 1.4.3 e o Cassandra 2.0.9-1 utilizando Python 2.7.  
 A sincronização é feita entre a tabela "superdupertable" do keyspace "mykeyspace" do Cassandra com a coleção "superdupertable" do índice "mykeyspace" do Elastic Search.  
   
 Obs: os nomes são iguais, mas nada impede de editá-los no código. O script não os recebe como parâmetros/configurações. Poderia ser um próximo update. Outra melhoria seria paginar os dados ao invés de pegar todos de uma vez, para evitar estouro de memória. Também poderia utilizar uma única rotina para fazer todo o processo e reduzir o número de acessos a ambas as bases, mas isso já atrapalharia a paginação e geraria diversas novas implicações quanto ao ambiente. Enfim. Implementei da maneira mais simples que encontrei.



### Instalação

 Copie o repositório com:  
 <code>git clone https://github.com/kalkehcoisa/elastic-cassandra.git</code>
  

 Entre no diretório criado e, para distribuições Debian, execute o script deploy.sh:  
 <code>sh deploy.sh</code>  
  

 O deploy.sh vai criar um virtualenv chamado simbiose em `/var/virtual_envs/simbiose/`. Inicie-o com:  
 <code>source /var/virtual_envs/simbiose/bin/activate</code>
  
  
 Por garantia, inicie os serviços sempre antes de executar o script python com:   
 <code>sudo service elasticsearch start   
 sudo service cassandra start</code>   
   
   
 Tudo pronto, instalado. Para começar a sincronizar é só executar:  
 <code>python task.py [intervalo de execução em segundos]</code>  
 O intervalo de execução é opcional e tem como padrão 1 segundo.
  
  
 Caso você esteja em algum sistema operacional ou distribuição diferente, você terá que ver os requisitos do projeto e instalá-los manualmente. Somente os pacotes python que ainda podem ser instalados de forma automatizada utilizando:  
 <code>pip install -r pip-reqs.txt</code>   
   

 Além disso, temos o `create_db.cql` que cria o keyspace e a tabela no Cassandra para podermos usar o script task.py:   
 <code>cqlsh < create_db.cql</code>   
   
   
   
### Requisitos

 - Elastic Search 1.4.3
 - Cassandra 2.0.9-1
 - Python 2.7
 - Java JDK e JRE 1.8
 - Java Native Access (JNA) (opcional)
  

### Funcionamento
  
 O script cria o comportamento de "daemon" com um `while True`. Dentro dele há duas rotinas: uma para levar os dados do Cassandra para o Elastic Search e outra para fazer o caminho oposto. Ambas são praticamente idênticas, exceto por umas pequenas adaptações devido as diferenças no formato dos dados.   
   
 O funcionamento é bem simples. O script usa duas variáveis para delimitar os dados a serem sincronizados:
 - START_TIME: limite inferior (começa com o valor 0 para varrer a base toda na primeira iteração e recebe o valor de NEW_TIME ao final de cada iteração)
 - NEW_TIME: limite superior (sempre recebe o horário atual ao iniciar uma iteração do laço)
 Com o uso dessas duas variáveis, a sincronização é usada sempre com os dados no mesmo intervalo de tempo e evita que dados inseridos durante a execução sejam incluídos e possam causar comportamentos indesejados como conflitos ou dados sendo ignorados por não terem sido recuperados na consulta que já foi realizada. Para isso, há um atributo `last_change` em todos os dados, que marca quando foi a última alteração nele.   
   
 Quanto as duas rotinas, elas recuperam todos os dados da base inseridos/atualizados no intervalo de tempo [START_TIME:NEW_TIME] e percorre esses dados verificando um por um se estão na outra base. Se não estiver, é inserido lá. Se estiver, verifica qual é o dado mais recente e sobrescreve o mais antigo.   
 Após executar as rotinas, define NEW_TIME com o horário atual e espera pelo tempo que foi passado como parâmetro para o script para executar as rotinas novamente.
  
  
  
### Testes

 Temos alguns testes unitários armazenados no diretório `tests`.   
 Para executá-los, basta utilizar o nose, ou algum outro pacote compatível. No caso do nose, é só executar dentro do diretório do projeto:   
 <code> nosetests . </code>   

 Só não se esqueça de instalá-lo antes:   
 <code> pip install nose </code>
   
   
   
### Materiais utilizados

 Estas são as principais fontes que utilizei para estudo e implementação deste script.

#### Instalação: 
   - https://gist.github.com/hengxin/8e5040d7a8b354b1c82e
   - http://www.elasticsearch.org/guide/en/elasticsearch/reference/current/setup-repositories.html

#### Cassandra e cqlsh: 
  - https://wiki.apache.org/cassandra/GettingStarted
  - https://cassandra.apache.org/doc/cql3/CQL.html

#### cassandra-driver:
   - http://datastax.github.io/python-driver/getting_started.html
   - http://planetcassandra.org/getting-started-with-cassandra-and-python/

#### Elastic Search:
  - http://joelabrahamsson.com/elasticsearch-101/
  - http://www.elasticsearch.org/guide/en/kibana/current/using-kibana-for-the-first-time.html

#### elasticsearch-py:
  - http://blog.arisetyo.com/?p=332
  - https://elasticsearch-py.readthedocs.org/en/master/

from conexion.mongo_queries import MongoQueries
import pandas as pd

PRINTA_DEBUG = True

MENU_PRINCIPAL = """Menu Principal
1 - Relatórios
2 - Inserir Registros
3 - Atualizar Registros
4 - Remover Registros
5 - Sair
"""

MENU_RELATORIOS = """Relatórios
1 - Relatório de Clientes
2 - Relatório de Contas
3 - Relatório de Movimentações Gerais das Contas
4 - Relatório de Tipo de Contas Por Cliente
5 - Relatório de Visão Geral de Contas
0 - Sair
"""

MENU_ENTIDADES = """Entidades
1 - CLIENTES
2 - CONTAS
3 - MOVIMENTAÇÃO
"""

MENU_CONTINUA = """Deseja continuar?
0 - NÃO
1 - SIM
"""

MENU_DESEJA = """Deseja mesmo excluir o registro?
0 - NÃO
1 - SIM
"""

# Consulta de contagem de registros por tabela
def query_count(collection_name):
   mongo = MongoQueries()
   mongo.connect()

   my_collection = mongo.db[collection_name]
   total_documentos = my_collection.count_documents({})
   mongo.close()
   df = pd.DataFrame({f"total_{collection_name}": [total_documentos]})
   return df

def count_collection(flag:bool,collection_name_a:str="contas", collection_name_b:str="movimentacoes" , pid:int=None) -> list:
   mongo = MongoQueries()
   mongo.connect()
   pid = int(pid)
   returnlist = [0,0]
   total_mov = 0
   llistacontas = list()
   novallistacontas = list()

   my_collection = mongo.db[collection_name_a]
   if flag:
    qtd_contas = len(pd.DataFrame(my_collection.find({"id_cliente": pid}, {"id": 1, "_id": 0})))
    df_contas = pd.DataFrame(my_collection.find({"id_cliente": pid}, {"numero": 1, "_id": 0}))
   else:
    qtd_contas = len(pd.DataFrame(my_collection.find({"numero": pid}, {"numero": 1, "_id": 0})))
    df_contas = pd.DataFrame(my_collection.find({"numero": pid}, {"numero": 1, "_id": 0}))

   print_debug(df_contas,PRINTA_DEBUG)

   if not df_contas.empty:
     llistacontas = list(df_contas.numero.values)

   for conta in llistacontas:
    novallistacontas.append(int(conta))

   returnlist[0] = qtd_contas

   print_debug(novallistacontas,PRINTA_DEBUG)

   my_collection = mongo.db[collection_name_b]
   df_mov = pd.DataFrame(my_collection.find({"numero_conta": {'$in': novallistacontas}}, {"id": 1, "_id": 0}))
   if not df_mov.empty:
    total_mov = int(df_mov.id.count())
   else:
      total_mov = 0

   returnlist[1] = total_mov

   print_debug(returnlist,PRINTA_DEBUG)

   mongo.close()
   return returnlist


def clear_console(wait_time:int=3):
    '''
       Esse método limpa a tela após alguns segundos
       wait_time: argumento de entrada que indica o tempo de espera
    '''
    import os
    from time import sleep
    sleep(wait_time)
    os.system("clear")

class Recupera:
    def __init__(self):
        self.mongo = MongoQueries()
    
        '''def recupera_prox_id(self, pcollection:str=None, external:bool=True) -> int:
        if external:
            # Cria uma nova conexão com o banco que permite alteração
            self.mongo.connect()

        # Recupera próximo id para tabela informada
        px_id = 0
        df_px_id = pd.DataFrame(self.mongo.db[pcollection].find().sort("id", -1).limit(1))
        px_id = df_px_id.id.values[0] + 1
        
        if external:
            # Fecha a conexão com o Mongo
            self.mongo.close()

        return px_id'''

    def recupera_prox_id(self, pcollection:str=None, external:bool=True) -> int:
        if external:
            # Cria uma nova conexão com o banco que permite alteração
            self.mongo.connect()

        # Recupera próximo id para tabela informada
        px_id = 0
        seq = "sequence"+pcollection
        df_px_id = pd.DataFrame(self.mongo.db["counters"].find({"_id": f"{seq}"}))
        df_px_id = int(df_px_id.sequence.values[0])
        px_id = df_px_id + 1
        self.mongo.db["counters"].update_one({"_id": f"{seq}"}, {"$set": {"sequence": px_id}})
        
        if external:
            # Fecha a conexão com o Mongo
            self.mongo.close()

        return df_px_id

def print_debug(pvar,flag:bool=False) -> None:
    if flag:
        print(pvar)
        print(type(pvar))
        from time import sleep
        sleep(10)

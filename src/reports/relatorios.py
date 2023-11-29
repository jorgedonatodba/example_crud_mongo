from conexion.mongo_queries import MongoQueries
import pandas as pd
from pymongo import ASCENDING, DESCENDING

class Relatorio:
    def __init__(self):
        pass

    def get_relatorio_tipo_de_conta_por_cliente(self):
        # Cria uma nova conexão com o banco
        mongo = MongoQueries()
        mongo.connect()
        # Recupera os dados transformando em um DataFrame
        query_result = mongo.db.contas.aggregate([              
                                                    {
                                                            '$group':{
                                                                '_id': { 'id_cliente' : "$id_cliente", 'tipo': "$tipo" },
                                                            "qtd_tipo": {"$sum": 1}
                                                        }
                                                    },
                                                        {
                                                        '$lookup': {
                                                            'from': 'clientes', 
                                                            'localField': '_id.id_cliente', 
                                                            'foreignField': 'id', 
                                                            'as': 'cliente'
                                                        }
                                                    }, {
                                                        '$unwind': {
                                                            'path': '$cliente'
                                                        }
                                                    }, {
                                                        '$project': {
                                                            'Nome': '$cliente.nome',
                                                            'Tipo': '$_id.tipo',
                                                            'Quantidade de Contas': '$qtd_tipo', 
                                                            '_id': 0
                                                        }
                                                    }, {
                                                        '$sort': {
                                                            'Nome': 1
                                                        }
                                                    }])
        
        df_tipo_conta = pd.DataFrame(list(query_result))
        # Fecha a conexão com o Mongo
        mongo.close()
        # Exibe o resultado
        print(df_tipo_conta[["Nome", "Tipo", "Quantidade de Contas"]])
        input("Pressione Enter para Sair do Relatório de Tipo de Contas Por Cliente")

    def get_relatorio_saldo_qtd_mov_conta(self):
        # Cria uma nova conexão com o banco
        mongo = MongoQueries()
        mongo.connect()
        # Recupera os dados transformando em um DataFrame
        query_result = mongo.db["movimentacoes"].aggregate([
               
                                                    {
                                                            "$group":{"_id":"$numero_conta",
                                                            "qtd_movs": {"$sum": 1}
                                                        }
                                                    },
                                                        {
                                                            '$lookup': {
                                                            'from': 'contas', 
                                                            'localField': '_id', 
                                                            'foreignField': 'numero', 
                                                            'as': 'conta'
                                                        }
                                                    }, {
                                                        '$unwind': {
                                                            'path': '$conta'
                                                        }
                                                    }, {
                                                        '$project': {
                                                            'cid_cliente': '$conta.id_cliente',
                                                            'csaldo': '$conta.saldo',
                                                            'cnumero_conta': '$conta.numero',
                                                            'cqtd_movs': '$qtd_movs', 
                                                            '_id': 0
                                                        }
                                                    }, 
                                                        {
                                                        '$lookup': {
                                                            'from': 'clientes', 
                                                            'localField': 'cid_cliente', 
                                                            'foreignField': 'id', 
                                                            'as': 'cliente'
                                                        }
                                                    }, {
                                                        '$unwind': {
                                                            'path': '$cliente'
                                                        }
                                                    }, {
                                                        '$project': {
                                                            'Nome': '$cliente.nome',
                                                            'Numero da Conta': '$cnumero_conta',
                                                            'Movimentacoes': '$cqtd_movs', 
                                                            'Saldo': '$csaldo', 
                                                            '_id': 0
                                                        }
                                                    }, {
                                                        '$sort': {
                                                            'Nome': 1
                                                        }
                                                    }])        
        df_cliente_conta_mov = pd.DataFrame(list(query_result))
        
        # Fecha a conexão com o Mongo
        mongo.close()
        # Exibe o resultado
        print(df_cliente_conta_mov[["Nome", "Numero da Conta", "Movimentacoes","Saldo"]])
        input("Pressione Enter para Sair do Relatório de Visão Geral de Contas")

    def get_relatorio_contas(self):
        # Cria uma nova conexão com o banco
        mongo = MongoQueries()
        mongo.connect()
        # Recupera os dados transformando em um DataFrame
        query_result = mongo.db["contas"].find({}, 
                                                 {"numero": 1,
                                                  "tipo": 1,
                                                  "saldo": 1,
                                                  "limite": 1,
                                                  "id_cliente": 1,
                                                  "_id": 0
                                                 }).sort("numero", ASCENDING)
        
        df_contas = pd.DataFrame(list(query_result))
        # Fecha a conexão com o Mongo
        mongo.close()
        # Exibe o resultado
        print(df_contas)        
        input("Pressione Enter para Sair do Relatório de Contas")

    def get_relatorio_clientes(self):
        # Cria uma nova conexão com o banco
        mongo = MongoQueries()
        mongo.connect()
        # Recupera os dados transformando em um DataFrame
        query_result = mongo.db["clientes"].find({}, 
                                                 {"id": 1,
                                                  "nome": 1,
                                                  "cpf": 1,
                                                  "endereco": 1,
                                                  "telefone": 1,  
                                                  "_id": 0
                                                 }).sort("nome", ASCENDING)
        df_cliente = pd.DataFrame(list(query_result))
        # Fecha a conexão com o mongo
        mongo.close()
        # Exibe o resultado
        print(df_cliente)
        input("Pressione Enter para Sair do Relatório de Clientes")

    def get_relatorio_movimentacoes(self):
        # Cria uma nova conexão com o banco
        mongo = MongoQueries()
        mongo.connect()
        # Recupera os dados transformando em um DataFrame
        query_result = mongo.db["movimentacoes"].find({}, 
                                                 {"numero_conta": 1,
                                                  "data": 1,
                                                  "descricao": 1,
                                                  "valor": 1,
                                                  "saldo_anterior": 1,  
                                                  "saldo_atual": 1,
                                                  "_id": 0
                                                 }).sort("numero_conta", ASCENDING)
        df_mov = pd.DataFrame(list(query_result))
        # Fecha a conexão com o mongo
        mongo.close()
        # Exibe o resultado
        print(df_mov)        
        input("Pressione Enter para Sair do Relatório de Movimentações")

    def get_relatorio_pedidos(self):
        # Cria uma nova conexão com o banco
        mongo = MongoQueries()
        mongo.connect()
        # Recupera os dados transformando em um DataFrame
        query_result = mongo.db["pedidos"].aggregate([
                                                    {
                                                        '$lookup': {
                                                            'from': 'fornecedores', 
                                                            'localField': 'cnpj', 
                                                            'foreignField': 'cnpj', 
                                                            'as': 'fornecedor'
                                                        }
                                                    }, {
                                                        '$unwind': {
                                                            'path': '$fornecedor'
                                                        }
                                                    }, {
                                                        '$project': {
                                                            'codigo_pedido': 1, 
                                                            'data_pedido': 1, 
                                                            'empresa': '$fornecedor.nome_fantasia', 
                                                            'cpf': 1, 
                                                            '_id': 0
                                                        }
                                                    }, {
                                                        '$lookup': {
                                                            'from': 'clientes', 
                                                            'localField': 'cpf', 
                                                            'foreignField': 'cpf', 
                                                            'as': 'cliente'
                                                        }
                                                    }, {
                                                        '$unwind': {
                                                            'path': '$cliente'
                                                        }
                                                    }, {
                                                        '$project': {
                                                            'codigo_pedido': 1, 
                                                            'data_pedido': 1, 
                                                            'empresa': 1, 
                                                            'cliente': '$cliente.nome', 
                                                            '_id': 0
                                                        }
                                                    }, {
                                                        '$lookup': {
                                                            'from': 'itens_pedido', 
                                                            'localField': 'codigo_pedido', 
                                                            'foreignField': 'codigo_pedido', 
                                                            'as': 'item'
                                                        }
                                                    }, {
                                                        '$unwind': {
                                                            'path': '$item', 'preserveNullAndEmptyArrays': True
                                                        }
                                                    }, {
                                                        '$project': {
                                                            'codigo_pedido': 1, 
                                                            'data_pedido': 1, 
                                                            'empresa': 1, 
                                                            'cliente': 1, 
                                                            'item_pedido': '$item.codigo_item_pedido', 
                                                            'quantidade': '$item.quantidade', 
                                                            'valor_unitario': '$item.valor_unitario', 
                                                            'valor_total': {
                                                                '$multiply': [
                                                                    '$item.quantidade', '$item.valor_unitario'
                                                                ]
                                                            }, 
                                                            'codigo_produto': '$item.codigo_produto', 
                                                            '_id': 0
                                                        }
                                                    }, {
                                                        '$lookup': {
                                                            'from': 'produtos', 
                                                            'localField': 'codigo_produto', 
                                                            'foreignField': 'codigo_produto', 
                                                            'as': 'produto'
                                                        }
                                                    }, {
                                                        '$unwind': {
                                                            'path': '$produto', 'preserveNullAndEmptyArrays': True
                                                        }
                                                    }, {
                                                        '$project': {
                                                            'codigo_pedido': 1, 
                                                            'data_pedido': 1, 
                                                            'empresa': 1, 
                                                            'cliente': 1, 
                                                            'item_pedido': 1, 
                                                            'quantidade': 1, 
                                                            'valor_unitario': 1, 
                                                            'valor_total': 1, 
                                                            'produto': '$produto.descricao_produto', 
                                                            '_id': 0
                                                        }
                                                    }, {
                                                        '$sort': {
                                                            'cliente': 1,
                                                            'item_pedido': 1
                                                        }
                                                    }
                                                ])
        df_pedido = pd.DataFrame(list(query_result))
        # Fecha a conexão com o Mongo
        mongo.close()
        print(df_pedido[["codigo_pedido", "data_pedido", "cliente", "empresa", "item_pedido", "produto", "quantidade", "valor_unitario", "valor_total"]])
        input("Pressione Enter para Sair do Relatório de Pedidos")
    
    def get_relatorio_itens_pedidos(self):
        # Cria uma nova conexão com o banco
        mongo = MongoQueries()
        mongo.connect()
        # Realiza uma consulta no mongo e retorna o cursor resultante para a variável
        query_result = mongo.db['itens_pedido'].aggregate([{
                                                            '$lookup':{'from':'produtos',
                                                                       'localField':'codigo_produto',
                                                                       'foreignField':'codigo_produto',
                                                                       'as':'produto'
                                                                      }
                                                           },
                                                           {
                                                            '$unwind':{"path": "$produto"}
                                                           },
                                                           {'$project':{'codigo_pedido':1, 
                                                                        'codigo_item_pedido':1,
                                                                    'codigo_produto':'$produto.codigo_produto',
                                                                    'descricao_produto':'$produto.descricao_produto',
                                                                    'quantidade':1,
                                                                    'valor_unitario':1,
                                                                    'valor_total':{'$multiply':['$quantidade','$valor_unitario']},
                                                                    '_id':0
                                                                    }}
                                                          ])
        # Converte o cursos em lista e em DataFrame
        df_itens_pedido = pd.DataFrame(list(query_result))
        # Troca o tipo das colunas
        df_itens_pedido.codigo_item_pedido = df_itens_pedido.codigo_item_pedido.astype(int)
        df_itens_pedido.codigo_pedido = df_itens_pedido.codigo_pedido.astype(int)
        # Fecha a conexão com o mongo
        mongo.close()
        # Exibe o resultado
        print(df_itens_pedido[["codigo_pedido", "codigo_item_pedido", "codigo_produto", "descricao_produto", "quantidade", "valor_unitario", "valor_total"]])
        input("Pressione Enter para Sair do Relatório de Itens de Pedidos")
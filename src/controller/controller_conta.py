import pandas as pd
from bson import ObjectId
from utils.config import Recupera

import utils.config as cf

from reports.relatorios import Relatorio

from model.contas import Conta
from model.clientes import Cliente
from conexion.mongo_queries import MongoQueries
from controller.controller_cliente import Controller_Cliente

class Controller_Conta:
    def __init__(self):
        self.ctrl_cliente = Controller_Cliente()
        self.recupera = Recupera()
        self.mongo = MongoQueries()
        self.relatorio = Relatorio()

        
    def inserir_conta(self) -> Conta:
        
        # Cria uma nova conexão com o banco
        self.mongo.connect()

        # Solicita ao usuario o novo CNPJ
        nconta = int(input("N. Conta (Nova): "))

    
        if  self.verifica_existencia_conta(nconta):
            # Solicita ao usuario o tipo da conta
            tipo = input("Tipo Conta (corrente, poupanca, credito) (Nova): ")
            # Solicita ao usuario o saldo da nova conta
            saldo = input("Saldo Inicial (Nova): ")
            # Solicita ao usuario o saldo da nova conta
            limite = input("Limite de Crédito (Nova): ")
            
            # Recupera dos clientes criado transformando em um DataFrame
            df_cliente = pd.DataFrame(list(self.mongo.db["clientes"].find({}, {"id":1, 
                                                                            "nome": 1, 
                                                                             "cpf": 1, 
                                                                             "endereco": 1, 
                                                                             "telefone": 1, 
                                                                             "_id": 0})))

            for i in range(df_cliente.index.size):
                # Cria um novo objeto Cliente
                ncliente = Cliente(df_cliente.id.values[i], df_cliente.cpf.values[i], df_cliente.nome.values[i], df_cliente.endereco.values[i], df_cliente.telefone.values[i])
                # Exibe os atributos do novo cliente
                print(ncliente.to_string())

            ncpf = input('Favor, informar CPF para a nova conta: ')

            dfclientid = self.ctrl_cliente.recupera_cliente(ncpf,True)
            codcli = int(dfclientid.id.values[0])
            
            novo_id = int(self.recupera.recupera_prox_id("contas"))

            # Insere e persiste a nova conta
            self.mongo.db["contas"].insert_one({"id": novo_id, "numero": nconta, "tipo": tipo, "saldo": saldo, "limite": limite, "id_cliente": codcli})

            # Recupera os dados do novo conta criado transformando em um DataFrame
            df_conta = self.recupera_conta(nconta)
            # Cria um novo objeto conta
            nova_conta = Conta(df_conta.id.values[0], df_conta.numero.values[0], df_conta.tipo.values[0], df_conta.saldo.values[0], df_conta.limite.values[0], df_conta.id_cliente.values[0])
            # Exibe os atributos do novo conta
            print(nova_conta.to_string())
            # Retorna o objeto novo_conta para utilização posterior, caso necessário
            return nova_conta
        else:
            print(f"A Conta {nconta} já está cadastrada.")
            return None

    def atualizar_conta(self) -> Conta:
        # Cria uma nova conexão com o banco que permite alteração
        self.mongo.connect()

        # Solicita ao usuário o código do conta a ser alterado
        nconta = int(input("Número da conta que deseja atualizar: "))

        # Verifica se o conta existe na base de dados
        if not self.verifica_existencia_conta(nconta):
            # Solicita ao usuario o novo tipo da Conta
            ntipo = input("Tipo Conta (corrente, poupanca, credito): ")
            # Solicita ao usuario a nova razão social
            nlimite = input("Novo Limite: ")
           
            # Updating fan quantity from 10 to 25.
            filter = { 'numero': nconta }
 
            # Values to be updated.
            newvalues = {"$set": {"tipo": ntipo, "limite": nlimite}}
            # Atualiza o nome do conta existente
            self.mongo.db["contas"].update_one(filter, newvalues)
            # Recupera os dados do novo conta criado transformando em um DataFrame
            df_conta = self.recupera_conta(nconta)
            # Cria um novo objeto conta
            conta_atualizada = Conta(df_conta.id.values[0],df_conta.numero.values[0], df_conta.tipo.values[0], df_conta.saldo.values[0], df_conta.limite.values[0], df_conta.id_cliente.values[0])
            # Exibe os atributos do novo conta
            print(conta_atualizada.to_string())
            # Retorna o objeto conta_atualizado para utilização posterior, caso necessário
            return conta_atualizada
        else:
            print(f"A conta {nconta} não existe.")
            return None

    def excluir_conta(self):
        # Cria uma nova conexão com o banco que permite alteração
        self.mongo.connect()

        # Solicita ao usuário o numero do conta a ser alterado
        nconta = int(input("Informar Número do conta que irá excluir: "))

        # Verifica se o conta existe na base de dados
        if not self.verifica_existencia_conta(nconta):            
            # Recupera os dados do novo conta criado transformando em um DataFrame
            df_conta = self.recupera_conta(nconta)
            
            cf.clear_console(1)
            print(cf.MENU_DESEJA)
            # Exibe os atributos do novo cliente
            opcao_deseja = int(input("Escolha uma opção [0-1]: "))        

            if opcao_deseja == 0:
                print("Registro não será excluído")
                self.mongo.close()
                return None
            
            print("Atenção, caso a conta possua movimentações, a mesma não poderá ser excluída!")
            numconta = df_conta.numero.values[0]
            llistadel = cf.count_collection(flag=False, pid=int(numconta))
            if llistadel[1] > 0:
                print("Atenção, conta com movimentações não pode ser excluída!")
                print("Exclusão de Movimentação não pode ser realizada - Normativa do Banco Central")
                self.mongo.close()
                return None
                        
            # Revome a conta da tabela
            self.mongo.db["contas"].delete_one({"id": int(df_conta.id.values[0])})
            print("Conta excuída com sucesso!")
            # Cria um novo objeto conta para informar que foi removida
            conta_excluida = Conta(df_conta.id.values[0],df_conta.numero.values[0], df_conta.tipo.values[0], df_conta.saldo.values[0], df_conta.limite.values[0], df_conta.id_cliente.values[0])
            self.mongo.close()
            # Exibe os atributos do produto excluído
            print(conta_excluida.to_string())
        else:
            print(f"A Conta {nconta} não existe.")

    def verifica_existencia_conta(self, nconta:int=None, external:bool=False) -> bool:
        if external:
            # Fecha a conexão com o Mongo
            self.mongo.connect()

        # Recupera os dados do novo conta criado transformando em um DataFrame
        df_conta = self.recupera_conta_codigo(codigo=nconta)

        if external:
            # Fecha a conexão com o Mongo
            self.mongo.connect()

        return df_conta.empty
    
    def recupera_conta_codigo(self, codigo:int=None) -> pd.DataFrame:

        # Recupera os dados da nova conta criada transformando em um DataFrame
        df_codigo = pd.DataFrame(list(self.mongo.db["contas"].find({"numero": codigo}, {"id": 1,  
                                                                                                          "numero": 1, 
                                                                                                          "tipo": 1, 
                                                                                                          "saldo": 1, 
                                                                                                          "limite": 1,
                                                                                                          "id_cliente": 1,
                                                                                                          "_id": 0})))
        '''if external:
            # Fecha a conexão com o Mongo
            self.mongo.close()'''
        
        return df_codigo

    def recupera_conta(self, nconta:int=None, external:bool=False) -> pd.DataFrame:
        if external:
            # Cria uma nova conexão com o banco que permite alteração
            self.mongo.connect()

        # Recupera os dados do novo cliente criado transformando em um DataFrame
        df_conta = pd.DataFrame(list(self.mongo.db["contas"].find({"numero": nconta}, {"id": 1, "numero": 1, "tipo": 1, "saldo": 1, "limite": 1, "id_cliente": 1, "_id": 0})))

        if external:
            # Fecha a conexão com o Mongo
            self.mongo.close()

        return df_conta

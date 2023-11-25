import pandas as pd
from model.movimentacoes import Movimentacao
from model.contas import Conta
from controller.controller_conta import Controller_Conta
from conexion.mongo_queries import MongoQueries
from reports.relatorios import Relatorio
from datetime import datetime

class Controller_Movimentacao:
    def __init__(self):
        self.ctrl_conta = Controller_Conta()
        self.mongo = MongoQueries()
        self.relatorio = Relatorio()
        
    def inserir_movimentacao(self) -> Movimentacao:
        # Cria uma nova conexão com o banco
        self.mongo.connect()

        # Lista as contas existentes para inserir uma nova movimentação
        self.listar_contas(external=True)
        lnumero = int(input("Digite o número da Conta: "))
        nconta = self.valida_conta(lnumero)
        if nconta == None:
            return None

        data_hoje = datetime.today().strftime("%m-%d-%Y")
        tipomov = input("Informar o Tipo da Movimemtação (C)rédito ou (D)ébito: ")

        vvalor = float(input("Informar o Valor da Movimentação: "))

        if (vvalor.__lt__(0)):
            print("Valor inválido - não pode ser negativo")
            return None

        vcontaid = nconta.get_id()
        vcontasaldo = nconta.get_saldo()
        vcontalimite = nconta.get_limite()
        vnumeroconta = nconta.get_numero()
        vsaldoatu = 0

        if tipomov.upper() == 'C':
            vdesc = 'CREDITO EM CONTA'
            vsaldoant = vcontasaldo
            vsaldoatu = vcontasaldo + vvalor
        elif tipomov.upper() == 'D':
            vdesc = 'DÉBITO EM CONTA'
            vsaldoant = vcontasaldo
            vsaldoatu = vcontasaldo - vvalor
            vvalor = vvalor*-1
        else:
            print("Favor, informar (C)rédito ou (D)ébito.")
            return None

        if (vcontalimite*-1) <= vsaldoatu:
            # Cria uma nova conexão com o banco que permite alteração
            self.mongo.connect()
            # Insere e persiste o novo saldo e movimento
            df_idmov = int(self.recupera.recupera_prox_id("movimentacoes"))
            # Cria um novo objeto conta
            idmov = df_idmov.id.values[0]
            self.mongo.db["contas"].update_one({"numero": f"{vnumeroconta}"}, {"$set": {"saldo": vsaldoatu}})            
            self.mongo.db["movimentacoes"].insert_one({"id": idmov, "data": data_hoje, "descricao": vdesc, "valor": vvalor, "saldo_anterior": vsaldoant, "saldo_atual": vsaldoatu, "numero_conta": vnumeroconta})
            # Recupera os dados da nova movimentacão criado transformando em um DataFrame
            df_mov = self.mongo.db["movimentacoes"].aggregate([
            { 
                '$match': 
                    {"id": f"{idmov}"}
             },
            {
        '       $project': {
            "num": { '$literal' : f"{vnumeroconta}" },"id": 1,"data": 1,"descricao": 1,"valor": 1,"saldo_anterior": 1,"saldo_atual": 1 
                }
            }
            ])
            # Cria um novo objeto conta
            nova_mov = Movimentacao(df_mov.id.values[0], df_mov.data.values[0], df_mov.descricao.values[0], df_mov.valor.values[0], df_mov.saldo_anterior.values[0],df_mov.saldo_atual.values[0],nconta)
            # Exibe os atributos do novo conta
            print(nova_mov.to_string())
            # Retorna o objeto novo_conta para utilização posterior, caso necessário
            return nova_mov
        else:
            print(f"A Movimentação não pode ser executada - Conta {vnumeroconta} - Limite de {vcontalimite} excedido.")
            return None


    def atualizar_movimentacao(self):
        print("Alterações em Movimentação não podem ser realizadas - Normativa do Banco Central")
        return None

    
    def excluir_movimentacao(self):
        print("Exclusão de Movimentação não pode ser realizada - Normativa do Banco Central")
        return None

    def listar_contas(self, nconta:int=None, external:bool=False) -> pd.DataFrame:
        if external:
            # Cria uma nova conexão com o banco que permite alteração
            self.mongo.connect()

        # Recupera os dados do novo cliente criado transformando em um DataFrame
        df_conta = pd.DataFrame(list(self.mongo.db["contas"].find({}, {"id": 1, "numero": 1, "tipo": 1, "saldo": 1, "limite": 1, "id_cliente": 1, "_id": 0})))
        
        if external:
            # Fecha a conexão com o Mongo
            self.mongo.close()

        return df_conta


    def valida_conta(self,pnumero:int=None) -> Conta:
        if self.ctrl_conta.verifica_existencia_conta(pnumero):
            print(f"A Conta {pnumero} informada não existe na base.")
            return None
        else:
            df_conta = self.ctrl_conta.recupera_conta(pnumero,external=True)
            nconta = Conta(df_conta.id.values[0], df_conta.numero.values[0], df_conta.tipo.values[0], df_conta.saldo.values[0], df_conta.limite.values[0], df_conta.id_cliente.values[0])
            return nconta
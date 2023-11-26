import logging
from conexion.mongo_queries import MongoQueries
from conexion.oracle_queries import OracleQueries
import json

LIST_OF_COLLECTIONS = ["counters","clientes", "contas","movimentacoes"]
logger = logging.getLogger(name="Example_CRUD_MongoDB")
logger.setLevel(level=logging.WARNING)
mongo = MongoQueries()

def createCollections(drop_if_exists:bool=False):
    """
        Lista as coleções existentes, verificar se as coleções padrão estão entre as coleções existentes.
        Caso exista e o parâmetro de exclusão esteja configurado como True, irá apagar a coleção e criar novamente.
        Caso não exista, cria a coleção.
        
        Parameter:
                  - drop_if_exists: True  -> apaga a tabela existente e recria
                                    False -> não faz nada
    """
    mongo.connect()
    existing_collections = mongo.db.list_collection_names()
    for collection in LIST_OF_COLLECTIONS:
        if collection in existing_collections:
            if drop_if_exists:
                mongo.db.drop_collection(collection)
                logger.warning(f"{collection} droped!")
                mongo.db.create_collection(collection)
                logger.warning(f"{collection} created!")
        else:
            mongo.db.create_collection(collection)
            logger.warning(f"{collection} created!")
    mongo.close()

def insert_many(data:json, collection:str):
    mongo.connect()
    mongo.db[collection].insert_many(data)
    mongo.close()

def extract_and_insert(plista:list=None) -> list:
    oracle = OracleQueries()
    oracle.connect()
    sql1 = "select * from ivie.{table}"
    for collection in LIST_OF_COLLECTIONS:
        if collection != "counters":
            df = oracle.sqlToDataFrame(sql1.format(table=collection))
            if collection == "movimentacoes":
                df["data"] = df["data"].dt.strftime("%m-%d-%Y")

            sql2 = f"select seq_{collection}_id.nextval as num from dual"
            df_qtd1 = oracle.sqlToDataFrame(sql2)

            sql3 = f"select seq_{collection}_id.currval +1 as num from dual"
            df_qtd = oracle.sqlToDataFrame(sql3)
            qtd = int(df_qtd.num.values[0])
            plista.append(qtd)

            logger.warning(f"data extracted from database Oracle ivie.{collection}")
            records = json.loads(df.T.to_json()).values()
            logger.warning("data converted to json")
            insert_many(data=records, collection=collection)
            logger.warning(f"documents generated at {collection} collection")
    return plista

def setar_sequences(plista:list=None) -> None:
    i = -1
    mongo.connect()
    for collection in LIST_OF_COLLECTIONS:
        if collection != "counters":
            i = i +1
            mongo.db["counters"].insert_one({"_id": f"sequence{collection}","sequence": plista[i]})

    mongo.close()


if __name__ == "__main__":
    qtds = list()
    logging.warning("Starting")
    createCollections(drop_if_exists=True)
    llista = extract_and_insert(qtds)
    setar_sequences(llista)
    logging.warning("End")

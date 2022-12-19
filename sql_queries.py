import pandas as pd
from sqlalchemy import create_engine

## Create Connection to database
db = 'crtbp.sql'
##db = 'mysql://root:123456@localhost/crtbp'
conn = create_engine(db)

# Function return bodies with satelites
    
def main_bodies(conn):
    query = 'SELECT * FROM bodies WHERE Primary_ID = 10 or Primary_ID = 0'
    df = pd.read_sql_query(query, conn,index_col = 'ID body')
    df_copy = df
    for i in range(len(df)):
        query = 'SELECT * FROM bodies WHERE Primary_ID = {}'.format(df.index[i])
        satelites = pd.read_sql_query(query, conn, index_col = 'ID body')
        if len(satelites) == 0:
            df_copy = df_copy.drop(df.index[i], axis = 0)
    return df_copy

# Satelites of selected body

def system(conn,main_id):
    query = 'SELECT * FROM bodies WHERE Primary_ID = {}'.format(main_id)
    df = pd.read_sql_query(query, conn)
    return df

# All possible families

def families(conn):
    query = 'SELECT * FROM families'
    df = pd.read_sql_query(query, conn)
    return df

# Orbits with caracteristics
def orbits(conn,body_id,family,args = [[],[],[]]):
    jacobi = args[0]
    period = args[1]
    stab = args[2]
    query = 'SELECT * FROM orbits WHERE  `ID body` = {} '.format(body_id)
    if family != -1:
        query += 'AND family = {} '.format(family)
    if jacobi:
        query += 'AND `JC-3` > {} AND `JC-3` < {} '.format(float(jacobi[0])-3,float(jacobi[1])-3)
    if period:
        query += 'AND period > {} AND period < {} '.format(period[0],period[1])
    if stab:
        query += 'AND stabA > {} AND stabA < {} '.format(stab[0],stab[1])
    df = pd.read_sql_query(query, conn)
    return df

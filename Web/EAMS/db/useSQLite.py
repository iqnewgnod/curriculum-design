# -*- coding: utf-8 -*-
import sqlite3


def OpenDb():
    database = "./EAMS.db"
    conn = sqlite3.connect(database)
    # conn.row_factory = sqlite3.Row
    return conn


def GetSql(conn, sql):
    cur = conn.cursor()
    cur.execute(sql)
    # fields = []
    # for field in cur.description:
    #     fields.append(field[0])

    result = cur.fetchall()
    # for item in result:
    #     print(item)
    cur.close()
    # return result, fields
    return result


def GetHead(conn, sql):
    cur = conn.cursor()
    cur.execute(sql)
    fields = []
    for field in cur.description:
        fields.append(field[0])
    cur.close()
    return fields


def CloseDb(conn):
    conn.close()


def query(sql):
    conn = OpenDb()
    result = GetSql(conn, sql)
    CloseDb(conn)
    return result


def query_head(tb):
    conn = OpenDb()
    sql = "select * from %s" % tb
    fields = GetHead(conn, sql)
    CloseDb(conn)
    return fields

def query_head_diy(sql):
    conn = OpenDb()
    fields = GetHead(conn, sql)
    CloseDb(conn)
    return fields

def UpdateData(data, tablename):
    conn = OpenDb()
    values = []
    cusor = conn.cursor()
    idName = list(data)[0]
    for v in list(data)[1:]:
        values.append("%s='%s'" % (v, data[v]))
    sql = "update %s set %s where %s='%s'" % (tablename, ",".join(values), idName, data[idName])
    # print (sql)
    cusor.execute(sql)
    conn.commit()
    cusor.close()
    CloseDb(conn)

def insertOrDeleteOrUpdate(sql):
    conn = OpenDb()
    cusor = conn.cursor()
    cusor.execute(sql)
    conn.commit()
    cusor.close()
    CloseDb(conn)

def InsertData(data, tablename):
    conn = OpenDb()
    values = []
    cusor = conn.cursor()
    fieldNames = list(data)
    for v in fieldNames:
        values.append(data[v])
    sql = "insert into  %s (%s) values( %s) " % (tablename, ",".join(fieldNames), ",".join(["?"] * len(fieldNames)))
    # print(sql)
    cusor.execute(sql, values)
    conn.commit()
    cusor.close()
    CloseDb(conn)


def DelDataById(id, value, tablename):
    conn = OpenDb()
    cusor = conn.cursor()
    sql = "delete from %s  where %s=?" % (tablename, id)
    # print (sql)
    cusor.execute(sql, (value,))
    conn.commit()
    cusor.close()
    CloseDb(conn)

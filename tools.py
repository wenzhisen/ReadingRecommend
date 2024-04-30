from langchain.tools import tool
import pymysql
from globals import filename2faiss


def ExecuteSQL(sql: str) -> str:
    """Query data in the database."""
    try:
        connect = pymysql.Connect(
            host='localhost',
            port=3306,
            user="root",
            passwd="Orange2020",
            db="reading_plateform",
        )
        cursor = connect.cursor()
        cursor.execute(sql)
        res = list(cursor.fetchall())
        cursor.close()
        connect.close()
        return str(res)
    except Exception as e:
        return str(e)


@tool
def queryStuHistory(stu_name, stu_id) -> str:
    """Query the reading history of a student."""
    sql = f"select * from student where student_name = '{stu_name}' and student_id = {stu_id}"
    return ExecuteSQL(sql)


@tool
def queryBookByISBN(ISBN: str) -> str:
    """Query books by ISBN."""
    sql = f"select * from book_info where ISBN = '{ISBN}'"
    return ExecuteSQL(sql)


@tool
def queryBookByChara(chara: str) -> str:
    """Query books by character."""
    sql = f"select * from book_info where mainly_affects_character = '{chara}'"
    return ExecuteSQL(sql)


@tool
def matchBookByEmb(desc: str) -> str:
    """Match books by embedding."""
    return "This tool is under development."


@tool
def listAllCharacter() -> str:
    """List all characters."""
    sql = "select distinct mainly_affects_character from book_info"
    return ExecuteSQL(sql)


@tool
def getStudentChara(stu_name: str, stu_id: int) -> str:
    """Get the character information of a student."""
    sql = f"select * from student where student_name = '{stu_name}' and student_id = {stu_id}"
    return ExecuteSQL(sql)


@tool
def search(text: str) -> str:
    """Search on the Internet. Not implemented yet."""
    return "This tool is under development."


@tool
def matchCorpusInFaissByEmb(filename: str, text: str) -> str:
    """Match corpus in the FAISS by embedding."""
    faiss = filename2faiss.get(filename)
    if faiss is None:
        return "File name not found."
    return faiss.similarity_search(text, k=3)

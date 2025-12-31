from sqlalchemy import Column,Integer,String
from Common.DBCommon.sqlLiteCom import BASE_MAP

#样例
class User(BASE_MAP["user_db"]):
    __tablename__ = "user"  # 数据库表名
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), nullable=False)
    age = Column(Integer, default=0)
    email = Column(String(100), default="")

class Student(BASE_MAP["user_db"]):
    __tablename__ = "student"  # 数据库表名
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), nullable=False)
    age = Column(Integer, default=0)
    email = Column(String(100), default="")
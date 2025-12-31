import importlib
import os
import sys
from typing import Dict, Tuple
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from Common.utils import initLogger, getAbsolutePath, loadYmlFile

##用的时候初始化好
#数据库别名 路径
DB_CONFIG: Dict[str, str] = {}
#数据库引擎
ENGINE_MAP: Dict[str, create_engine] = {}
#会话
SESSION_MAP: Dict[str, sessionmaker] = {}
#模型基类
BASE_MAP: Dict[str, declarative_base] = {}
#调试模式
DEBUG_MODE = False

#Db初始化
def initDb():
    logger = initLogger()
    configPath = getAbsolutePath("../Config/config.yml")
    config = loadYmlFile(configPath)
    dbList = config["sqllite"]["db_name"]
    for dbAlias in dbList:
        DB_CONFIG[dbAlias] = getAbsolutePath(f"../DBFile/{dbAlias}.db")
        initEachDb(dbAlias)
    #加载Model中对应的table
    model_dir = getAbsolutePath("../Model")
    if not os.path.exists(model_dir):
        logger.error(f"Model dir {model_dir} not exists.Initialization failing!")
        raise FileNotFoundError(f"Model dir {model_dir} not exists.Initialization failing!")
    for file_name in os.listdir(model_dir):
        file_path = os.path.join(model_dir, file_name)
        if not os.path.isfile(file_path):
            continue
        if not file_name.endswith(".py"):
            continue
        module_name = os.path.splitext(os.path.basename(file_path))[0]
        # 动态加载模块
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)  # 执行模块代码（此时实例会被创建）
    for dbAlias in dbList:
        createAllTables(dbAlias)

#初始化各个数据库
def initEachDb(dbAlias: str) -> Tuple[declarative_base, sessionmaker]:
    logger = initLogger()
    #初始化指定别名的数据库（创建引擎、会话类、模型基类）
    # 若已初始化，直接返回缓存的基类和会话类
    if dbAlias in BASE_MAP and dbAlias in SESSION_MAP:
        return BASE_MAP[dbAlias], SESSION_MAP[dbAlias]
    # 1. 获取数据库连接 URL
    db_path = DB_CONFIG[dbAlias]
    db_url = f"sqlite:///{db_path}"

    # 2. 创建引擎（存入引擎映射表）
    engine = create_engine(
        db_url,
        echo=DEBUG_MODE,
        pool_size=20,  # 连接池大小
        max_overflow=50  # 最大溢出连接数
    )
    ENGINE_MAP[dbAlias] = engine

    # 3. 创建该数据库专属的模型基类（存入基类映射表）
    base = declarative_base()
    BASE_MAP[dbAlias] = base

    # 4. 创建会话类（存入会话映射表）
    session_cls = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine
    )
    SESSION_MAP[dbAlias] = session_cls
    logger.info(f"Initializing database {dbAlias} successfully!")
    return base, session_cls

#获取会话实例
def getDbSession(dbAlias: str):
    if dbAlias not in DB_CONFIG:
        initEachDb(dbAlias)
    session_cls = SESSION_MAP[dbAlias]
    dbSession = session_cls()
    try:
        yield dbSession #返回生成器，next()触发了
    finally:
        dbSession.close()

def createAllTables(db_alias: str):
    logger = initLogger()
    #创建数据库中所有表
    if db_alias not in BASE_MAP or db_alias not in ENGINE_MAP:
        initEachDb(db_alias)
    base = BASE_MAP[db_alias]
    engine = ENGINE_MAP[db_alias]
    base.metadata.create_all(engine)  # 创建所有绑定该基类的模型表
    table_names = list(base.metadata.tables.keys())
    if table_names:
        table_names_str = ", ".join(table_names)
        logger.info(f"Create tables for {db_alias} successfully! Table names: {table_names_str}")
    else:
        logger.info(f"No tables to create for {db_alias}!")



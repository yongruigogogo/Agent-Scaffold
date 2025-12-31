import inspect
import logging
import os
from datetime import datetime
import yaml
import colorlog

def getAbsolutePath(relativePath:str) -> str:
    currentFilePath = os.path.abspath(__file__)
    currentDir = os.path.dirname(currentFilePath)
    configPath = os.path.join(currentDir, relativePath)
    configPath = os.path.normpath(configPath)
    return configPath

#读取yml文件
def loadYmlFile(path:str):
    with open(path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    return config

#日志系统
def initLogger():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    logger.handlers.clear()
    #控制台日志
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_formatter = colorlog.ColoredFormatter(
        '%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        log_colors={
            'DEBUG': 'green',
            'INFO': 'green',
            'WARNING': 'yellow',
            'CRITICAL': 'red',
        }
    )
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)  # 控制台只输出≥DEBUG级别的日志
    console_handler.setFormatter(console_formatter)
    #持久化保存
    # 1. DEBUG级别专属文件
    logFilePathDebug = getAbsolutePath("../Log/debugLog.log")
    debugFileHandler = logging.FileHandler(
        filename=logFilePathDebug,  # DEBUG日志文件路径
        mode='a',  # 保留你原有追加模式
        encoding='utf-8'  # 保留你原有编码配置
    )
    debugFileHandler.setLevel(logging.DEBUG)  # 先设为最低级别，确保能捕获DEBUG
    debugFileHandler.setFormatter(formatter)  # 绑定你原有格式化器
    # 自定义过滤器：仅保留DEBUG级别日志
    class DebugFilter(logging.Filter):
        def filter(self, record):
            return record.levelno == logging.DEBUG

    debugFileHandler.addFilter(DebugFilter())  # 绑定DEBUG过滤器

    # 2. INFO级别专属文件：仅保存INFO日志（对应你的需求）
    logFilePathInfo = getAbsolutePath("../Log/infoLog.log")
    infoFileHandler = logging.FileHandler(
        filename=logFilePathInfo,  # INFO日志文件路径
        mode='a',
        encoding='utf-8'
    )
    infoFileHandler.setLevel(logging.INFO)  # 保留你原有级别配置
    infoFileHandler.setFormatter(formatter)

    # 自定义过滤器：仅保留INFO级别日志
    class InfoFilter(logging.Filter):
        def filter(self, record):
            return record.levelno == logging.INFO
    infoFileHandler.addFilter(InfoFilter())  # 绑定INFO过滤器
    # 3. 剩余级别（WARNING/ERROR/CRITICAL）合并文件：保存这三类日志
    logFilePathError = getAbsolutePath("../Log/errorLog.log")
    otherFileHandler = logging.FileHandler(
        filename=logFilePathError,  # 剩余级别日志文件路径
        mode='a',
        encoding='utf-8'
    )
    otherFileHandler.setLevel(logging.WARNING)  # 捕获≥WARNING级别日志
    otherFileHandler.setFormatter(formatter)

    # 自定义过滤器：仅保留WARNING/ERROR/CRITICAL级别
    class OtherFilter(logging.Filter):
        def filter(self, record):
            return record.levelno >= logging.WARNING

    otherFileHandler.addFilter(OtherFilter())  # 绑定过滤器，确保精准分流
    ##
    logger.addHandler(console_handler)
    logger.addHandler(debugFileHandler)
    logger.addHandler(infoFileHandler)
    logger.addHandler(otherFileHandler)
    return logger


if __name__ == '__main__':
    pass
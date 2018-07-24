# -*- coding:utf-8 -*-

import logging
import logging.handlers
import functools
import time
import os


STD_FORMAT = "%(asctime)s TID[%(thread)d] %(filename)s[fn:%(funcName)s][line:%(lineno)d][%(levelname)s] %(message)s"

TIME_LEVEL_CONTENT = "%(asctime)s %(levelname)-8s: %(message)s"
CLASSIC_FORMAT = "%(asctime)s %(filename)s line:%(lineno)d [%(levelname)s] : %(message)s"


FMT_TIME = "%(asctime)s"
FMT_FILE_NAME = "%(filename)s"
FMT_FUNC_NAME = "%(funcName)s"
FMT_LEVEL_NAME = "%(levelname)s"
FMT_LEVEL_NO = "%(levelno)s"
FMT_LINE_NO = "%(lineno)d"
FMT_MODULE = "%(module)s"
FMT_LOGGER_NAME = "%(name)s"
FMT_PATH_NAME = "%(pathname)s"
FMT_PROCESS_ID = "%(process)d"
FMT_PROCESS_NAME = "%(processName)s"
FMT_THREAD_ID = "%(thread)d"
FMT_THREAD_NAME = "%(threadName)s"
FMT_LOG_CONTENT = "%(message)s"

ROTATE_LOG_UNIT_SECOND = "s"
ROTATE_LOG_UNIT_MINUTE = "m"
ROTATE_LOG_UNIT_HOUR = "h"
ROTATE_LOG_UNIT_DAY = "d"

SULOG_DEBUG = logging.DEBUG
SULOG_INFO = logging.INFO
SULOG_WARN = logging.WARN
SULOG_WARNING = logging.WARNING
SULOG_ERROR = logging.ERROR
SULOG_FATAL = logging.FATAL
SULOG_CRITICAL = logging.CRITICAL


def _singleton(cls):
    ins = {}

    @functools.wraps(cls)
    def get_inst(*args, **kwargs):
        if cls not in ins:
            ins[cls] = cls(*args, **kwargs)
        return ins[cls]
    return get_inst


def make_std_log_format(*args):
    fmt = FMT_LOG_CONTENT
    if len(args) > 0:
        fmt = ""
        for extra_fmt in args:
            fmt = "%s %s" % (fmt, extra_fmt)
    return fmt


def make_custom_log_format(fmt_str):
    lst = [
        "FMT_TIME", "FMT_FILE_NAME", "FMT_FUNC_NAME", "FMT_LEVEL_NAME", "FMT_LEVEL_NO",
        "FMT_LINE_NO", "FMT_MODULE", "FMT_LOGGER_NAME", "FMT_PATH_NAME", "FMT_PROCESS_ID",
        "FMT_PROCESS_NAME", "FMT_THREAD_ID", "FMT_THREAD_NAME", "FMT_LOG_CONTENT"
    ]
    ret = fmt_str
    for each in lst:
        ret = ret.replace(each, eval(each))
    return ret


def _wrap_parent(func):
    @functools.wraps(func)
    def func_wrapper(*args, **kwargs):
        # print(inspect.stack()[1][3])
        print(func.__name__)
        return func(*args, **kwargs)
    return func_wrapper


def _ensure_init(func):
    @functools.wraps(func)
    def func_wrapper(self, *args, **kwargs):
        if not self.init:
            raise RuntimeError("Must Call init_basic_console_log_fmt first")
        return func(self, *args, **kwargs)
    return func_wrapper


@_singleton
class _SuLog(object):

    def __init__(self):
        super().__init__()
        self._is_init = False
        self._basic_logger = logging.getLogger("_basic_std_")

    def init_basic_console_log_fmt(
            self, console_output_level=SULOG_DEBUG, console_fmt=CLASSIC_FORMAT,
            enable_file_log = False, file_log_level=SULOG_INFO,
            file_fmt=CLASSIC_FORMAT, file_log_dir = "./"
    ):
        console = logging.StreamHandler()
        console.setLevel(console_output_level)
        formatter = logging.Formatter(console_fmt)
        console.setFormatter(formatter)
        self._basic_logger.setLevel(SULOG_DEBUG)
        self._basic_logger.addHandler(console)

        if enable_file_log:
            f_name =time.strftime("%Y%m%d_%H%M%S", time.localtime())
            if not os.path.exists(file_log_dir):
                os.makedirs(file_log_dir)
            fdl = logging.FileHandler("%s%s.log" % (file_log_dir, f_name), encoding="utf-8")
            fdl.setLevel(file_log_level)
            fdl.setFormatter(logging.Formatter(file_fmt))
            self._basic_logger.addHandler(fdl)

        self._is_init = True

    @property
    def init(self):
        return self._is_init

    def add_normal_file_logger(
            self, logger_name, log_file_path, fmt=CLASSIC_FORMAT,
            file_log_level=SULOG_INFO, file_mode='a',
            enable_console_output=True, console_output_level=SULOG_DEBUG
    ):
        fd, _ = os.path.split(log_file_path)
        if not os.path.exists(fd):
            os.makedirs(fd)

        hdl = logging.FileHandler(log_file_path, mode=file_mode, encoding='utf-8')
        hdl.setLevel(file_log_level)
        hdl_fmt = logging.Formatter(fmt)
        hdl.setFormatter(hdl_fmt)
        logger = logging.getLogger(logger_name)
        logger.setLevel(SULOG_DEBUG)
        logger.addHandler(hdl)

        if enable_console_output:
            console = logging.StreamHandler()
            console.setLevel(console_output_level)
            formatter = logging.Formatter(fmt)
            console.setFormatter(formatter)
            logger.addHandler(console)

        self.__setattr__(logger_name, logger)

    def add_rotate_file_logger(
            self, logger_name, log_file_path, fmt=CLASSIC_FORMAT,
            file_log_level=SULOG_INFO, rotate_unit=ROTATE_LOG_UNIT_DAY,
            log_period=1, keep_backup=5,
            enable_console_output=True, console_output_level=SULOG_DEBUG
    ):
        fd, _ = os.path.split(log_file_path)
        if not os.path.exists(fd):
            os.makedirs(fd)

        hdl = logging.handlers.TimedRotatingFileHandler(
            log_file_path, rotate_unit, log_period, keep_backup, encoding='utf-8'
        )
        hdl.setLevel(file_log_level)
        hdl_fmt = logging.Formatter(fmt)
        hdl.setFormatter(hdl_fmt)
        logger = logging.getLogger(logger_name)
        logger.setLevel(SULOG_DEBUG)
        logger.addHandler(hdl)

        if enable_console_output:
            console = logging.StreamHandler()
            console.setLevel(console_output_level)
            formatter = logging.Formatter(fmt)
            console.setFormatter(formatter)
            logger.addHandler(console)

        self.__setattr__(logger_name, logger)

    @_ensure_init
    def __getattr__(self, item):
        if item in ["debug", "info", "warn", "warning", "error", "fatal", "critical"]:
            return eval('logging.getLogger("_basic_std_").%s' % item)
        else:
            raise RuntimeError("No such attribute")


slog = _SuLog()


if __name__ == '__main__':

    slog.init_basic_console_log_fmt(enable_file_log=True)
    slog.debug("DDDDDebug")

    slog.info("Can't take my eyes off you")

    slog.add_normal_file_logger("mateB", "./mateB.log", file_log_level=SULOG_DEBUG)
    slog.mateB.debug("Separate log")
    slog.mateB.info("Output to File")

    slog.add_rotate_file_logger("mateC", "./mateC.log", fmt=TIME_LEVEL_CONTENT)
    slog.mateC.info("Hello world")

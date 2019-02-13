# -*- coding:utf-8 -*-

import sys
import logging
import functools
import datetime
import io
import threading


LOG_LEVEL_DEBUG = logging.DEBUG
LOG_LEVEL_INFO  = logging.INFO
LOG_LEVEL_WARN  = logging.WARNING
LOG_LEVEL_ERROR = logging.ERROR
LOG_LEVEL_FATAL = logging.FATAL

SIMPLE_FMT = "%(asctime)s [%(levelname)s] %(message)s"


_DEFAULT_LOGGER_NAME = "_default_root_"
_LOCK = threading.RLock()


def _singleton(cls):
    ins = {}

    @functools.wraps(cls)
    def get_inst(*args, **kwargs):
        if cls not in ins:
            ins[cls] = cls(*args, **kwargs)
        return ins[cls]
    return get_inst


class _BaseLogger(object):

    def __init__(self, name, level, fmt, toggle_log_file_path, toggle_log_fn_name, toggle_log_fn_lineno):
        super().__init__()
        self._logger_name = name
        self._log_level = level
        self._fmt = fmt
        self._toggle_log_file_path = toggle_log_file_path
        self._toggle_log_fn_name = toggle_log_fn_name
        self._toggle_log_fn_lineno = toggle_log_fn_lineno

    @property
    def name(self):
        return self._logger_name

    @property
    def level(self):
        return self._log_level

    @property
    def logger_format(self):
        return self._fmt

    def _build_msg(self, msg):
        frame = sys._getframe().f_back.f_back.f_back.f_back.f_back
        buf = io.StringIO()
        buf.write(" ")
        FIB = frame.f_code
        if self._toggle_log_file_path:
            buf.write("[P:%s]" % FIB.co_filename)
        if self._toggle_log_fn_name:
            buf.write("[F:%s]" % FIB.co_name)
        if self._toggle_log_fn_lineno:
            buf.write("[L:%s]" % frame.f_lineno)
        buf.write(" %s" % msg)
        return buf.getvalue().strip()

    def log_debug(self, msg):
        full_msg = "   %s" % self._build_msg(msg)
        logging.getLogger(self.name).debug(full_msg)

    def log_info(self, msg):
        full_msg = "    %s" % self._build_msg(msg)
        logging.getLogger(self.name).info(full_msg)

    def log_warn(self, msg):
        full_msg = " %s" % self._build_msg(msg)
        logging.getLogger(self.name).warning(full_msg)

    def log_error(self, msg):
        full_msg = "   %s" % self._build_msg(msg)
        logging.getLogger(self.name).error(full_msg)

    def log_fatal(self, msg):
        full_msg = self._build_msg(msg)
        logging.getLogger(self.name).fatal(full_msg)


class ConsoleLogger(_BaseLogger):

    def __init__(
            self, name=_DEFAULT_LOGGER_NAME, level=LOG_LEVEL_DEBUG, fmt=SIMPLE_FMT,
            toggle_log_file_path=False, toggle_log_fn_name=False, toggle_log_fn_lineno=False
    ):
        super().__init__(name, level, fmt, toggle_log_file_path, toggle_log_fn_name, toggle_log_fn_lineno)


class FileLogger(_BaseLogger):

    def __init__(
            self, name=_DEFAULT_LOGGER_NAME, level=LOG_LEVEL_DEBUG, file_path=None,
            enable_console_output=True, fmt=SIMPLE_FMT,
            toggle_log_file_path=False, toggle_log_fn_name=False, toggle_log_fn_lineno=False
    ):
        super().__init__(name, level, fmt, toggle_log_file_path, toggle_log_fn_name, toggle_log_fn_lineno)
        self._log_file_path = file_path
        self._enable_console_output=enable_console_output
        if self._log_file_path is None:
            now = datetime.datetime.now()
            self._log_file_path = "./%04d%02d%02d_%02d%02d%02d.log" % (
                now.year, now.month, now.day, now.hour, now.minute, now.second
            )

        self._file_handle = None

    @property
    def file_path(self):
        return self._log_file_path

    @property
    def enable_std_output(self):
        return self._enable_console_output


@_singleton
class LogManager(object):

    def __init__(self):
        super().__init__()
        self._logger_dict = {}

    def append_logger(self, logger_obj: FileLogger):
        if isinstance(logger_obj, _BaseLogger):
            if logger_obj.name in self._logger_dict:
                raise RuntimeError("You have already assigned an logger which name is '%s'" % logger_obj.name)
        else:
            raise RuntimeError("Not a valid Logger")
        if isinstance(logger_obj, ConsoleLogger):
            console = logging.StreamHandler()
            console.setLevel(logger_obj.level)
            formatter = logging.Formatter(logger_obj.logger_format)
            console.setFormatter(formatter)
            logger = logging.getLogger(logger_obj.name)
            logger.setLevel(LOG_LEVEL_DEBUG)
            logger.addHandler(console)
        elif isinstance(logger_obj, FileLogger):
            hdl = logging.FileHandler(logger_obj.file_path, mode="a", encoding='utf-8')
            hdl.setLevel(logger_obj.level)
            hdl_fmt = logging.Formatter(logger_obj.logger_format)
            hdl.setFormatter(hdl_fmt)
            logger = logging.getLogger(logger_obj.name)
            logger.setLevel(LOG_LEVEL_DEBUG)
            logger.addHandler(hdl)
            if logger_obj.enable_std_output:
                console = logging.StreamHandler()
                console.setLevel(logger_obj.level)
                formatter = logging.Formatter(logger_obj.logger_format)
                console.setFormatter(formatter)
                logger.addHandler(console)
        else:
            raise RuntimeError("Not a valid Logger")
        self._logger_dict[logger_obj.name] = logger_obj

    def log_debug(self, logger_name, msg):
        if logger_name in self._logger_dict:
            self._logger_dict[logger_name].log_debug(msg)

    def log_info(self, logger_name, msg):
        if logger_name in self._logger_dict:
            self._logger_dict[logger_name].log_info(msg)

    def log_warn(self, logger_name, msg):
        if logger_name in self._logger_dict:
            self._logger_dict[logger_name].log_warn(msg)

    def log_error(self, logger_name, msg):
        if logger_name in self._logger_dict:
            self._logger_dict[logger_name].log_error(msg)

    def log_fatal(self, logger_name, msg):
        if logger_name in self._logger_dict:
            self._logger_dict[logger_name].log_fatal(msg)


def _thread_safe(fn):
    @functools.wraps(fn)
    def func(*args, **kwargs):
        _LOCK.acquire()
        try:
            ret = fn(*args, **kwargs)
        finally:
            _LOCK.release()
        return ret
    return func


@_thread_safe
def append_logger(log_obj):
    LogManager().append_logger(log_obj)


@_thread_safe
def log_debug(msg):
    LogManager().log_debug(_DEFAULT_LOGGER_NAME, msg)


@_thread_safe
def log_info(msg):
    LogManager().log_info(_DEFAULT_LOGGER_NAME, msg)


@_thread_safe
def log_warn(msg):
    LogManager().log_warn(_DEFAULT_LOGGER_NAME, msg)


@_thread_safe
def log_error(msg):
    LogManager().log_error(_DEFAULT_LOGGER_NAME, msg)


@_thread_safe
def log_fatal(msg):
    LogManager().log_fatal(_DEFAULT_LOGGER_NAME, msg)


@_thread_safe
def ilog_debug(inst_name, msg):
    LogManager().log_debug(inst_name, msg)


@_thread_safe
def ilog_info(inst_name, msg):
    LogManager().log_info(inst_name, msg)


@_thread_safe
def ilog_warn(inst_name, msg):
    LogManager().log_warn(inst_name, msg)


@_thread_safe
def ilog_error(inst_name, msg):
    LogManager().log_error(inst_name, msg)


@_thread_safe
def ilog_fatal(inst_name, msg):
    LogManager().log_fatal(inst_name, msg)


def log_test():

    log_debug("Hi I am IRON Man")
    log_info("Info")
    log_warn("warn")
    log_error("error")
    log_fatal("fatal")
    ilog_debug("another", "I am Tony")
    ilog_info("another", "I am Stark")
    ilog_warn("another", "I am Wolfrine")
    ilog_error("another", "This is the Marvel Universe??")
    ilog_fatal("another", "Why Wolfrine here??")


if __name__ == '__main__':

    append_logger(ConsoleLogger(toggle_log_fn_name=True, toggle_log_fn_lineno=True))
    append_logger(FileLogger("another", level=LOG_LEVEL_WARN, enable_console_output=True))
    log_test()

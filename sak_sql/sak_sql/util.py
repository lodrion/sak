import contextlib
import logging
from typing import Any, Dict, Iterable, List, Optional, Union, NoReturn

from sqlalchemy import text
from sqlalchemy.engine import Connection, Engine
from sqlalchemy.orm import sessionmaker


ClassesWithExecute = Union[Connection, Engine]
logger = logging.getLogger(__name__)


def run_query(
    executor: ClassesWithExecute, query: text, **kwargs: Dict[str, Any]
) -> Iterable[Dict[str, Any]]:
    """Execute query parameterized by kwargs returning a generator of dicts"""
    result_generator = executor.execute(query, kwargs)
    keys = result_generator.keys()
    for res in result_generator:
        yield {key: res[key] for key in keys}


@contextlib.contextmanager
def autosession(engine: Engine) -> Iterable:
    """Ssession context manager with autocommit and autorollback on errors"""
    session = sessionmaker(bind=engine)()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error('Rolling back because of underlying: {}'.format(repr(e)))
        raise
    finally:
        session.close()

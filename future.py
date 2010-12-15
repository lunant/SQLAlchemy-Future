""":mod:`future` --- SQLAlchemy-Future
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
import threading
import sqlalchemy.orm.query


class Query(sqlalchemy.orm.query.Query):

    def promise(self):
        return Future(self)


class Future(object):

    __slots__ = "query", "_iter", "_head", "_thread"

    def __init__(self, query):
        if not isinstance(query, sqlalchemy.orm.query.Query):
            raise TypeError("query must be an instance of sqlalchemy.orm."
                            "query.Query, not " + type(query).__name__)
        self.query = query
        self._iter = None
        self._head = None
        thread_name = "{0}-{1}".format(type(self).__name__, id(self))
        self._thread = threading.Thread(target=self.execute_promise,
                                        name=thread_name)
        self._thread.start()

    def execute_promise(self):
        self._iter = iter(self.query)
        try:
            val = self._iter.next()
        except StopIteration:
            self._head = ()
        else:
            self._head = val,

    def __iter__(self):
        if self._iter is None or self._head is None:
            self._thread.join()
        if not self._head:
            return
        yield self._head[0]
        for value in self._iter:
            yield value

    def all(self):
        return list(self)


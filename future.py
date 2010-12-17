""":mod:`future` --- SQLAlchemy-Future
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
import threading
import sqlalchemy.orm.query


class Query(sqlalchemy.orm.query.Query):
    """The subtype of :class:`sqlalchemy.orm.query.Query` class, that provides
    the :meth:`promise()` method.

    You can make this the default query class of your session::

        from sqlalchemy.orm import sessionmaker
        import future
        Session = sessionmaker(query_cls=future.Query)

    """

    def promise(self):
        """Makes a promise and returns a :class:`Future`.

        :returns: the promised future
        :rtype: :class:`Future`

        """
        return Future(self)


class Future(object):
    """Promoise future query.

    :param query: the query to promise
    :type query: :class:`sqlalchemy.orm.query.Query`

    .. warning::
    
       It is not a subtype of :class:`Query`, so it does not provide any
       method of :class:`Query` like :meth:`~Query.filter()`.

    """

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
        """Returns the results promised as a :class:`list`. This blocks the
        underlying execution thread until the execution has finished if it
        is not yet.

        :returns: the results promised
        :rtype: :class:`list`

        """
        return list(self)


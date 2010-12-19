""":mod:`future` --- SQLAlchemy-Future
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

SQLAlchemy-Future is a SQLAlchemy_ extension that introduces `future/promise`_
into query.

.. _SQLAlchemy: http://www.sqlalchemy.org/
.. _future/promise: http://en.wikipedia.org/wiki/Futures_and_promises


How to setup
============

In order to make :class:`future.Query <Query>` the default query class, use
the ``query_cls`` parameter of the
:func:`~sqlalchemy.orm.session.sessionmaker()` function::

    import future
    from sqlalchemy.orm.session import sessionmaker
    Session = sessionmaker(query_cls=future.Query)

Or you can make :class:`future.Query <Query>` the query class of a session
instance optionally::

    session = Session(query_cls=future.Query)


How to promise
==============

How to promise a future query is not hard. Just call the
:meth:`~Query.promise()` method::

    posts = session.query(Post).promise()

Its return type is :class:`Future` (note that it is not a subtype of
:class:`Query`, so you cannot use rich facilities of :class:`Query` like
:meth:`~sqlalchemy.orm.query.Query.filter`)::

    assert isinstance(posts, future.Future)

Then, iterate this future query (``posts`` in the example) when you really
need it::

    for post in posts:
        print post.title, "by", post.author

If the ``posts`` finished the execution in the another thread, it fetches the
result set immediately. If its execution hasn't finished, the another thread
joins the main thread and it has blocked until its execution has finished.


References
==========

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
    """Promoised future query result.

    :param query: the query to promise
    :type query: :class:`sqlalchemy.orm.query.Query`

    .. note::
    
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


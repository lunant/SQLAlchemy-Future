.. SQLAlchemy-Future documentation master file, created by
   sphinx-quickstart on Sat Dec 18 01:26:19 2010.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

SQLAlchemy-Future
~~~~~~~~~~~~~~~~~

SQLAlchemy-Future is a SQLAlchemy_ extension that introduces `future/promise`_
into query.

.. _SQLAlchemy: http://www.sqlalchemy.org/
.. _future/promise: http://en.wikipedia.org/wiki/Futures_and_promises


What it improves
================

Assume we are building a web application that depends on SQLAlchemy_. Typical
web applications are structured by models, controllers and templates (views).
Most of operations that depend on models are finished in controllers. ::

    def list_posts():
        session = Session()
        posts = session.query(Post).order_by(Post.created_at.desc()).all()
        return render_template('list_posts.html', posts=posts)

Codes like this pattern cause a *blank screen* when the browser are loading it.
Then, the result list are rendered suddenly at once.

.. image:: _static/eager-loading.gif

To avoid the *blank screen*, we can make queries lazy::

    def list_posts():
        session = Session()
        posts = session.query(Post).order_by(Post.created_at.desc())
        return render_template('list_posts.html', posts=posts)

See the difference between both second lines of the former example code and the
current. The first example calls the :meth:`~sqlalchemy.orm.query.Query.all()`
method of the query object, but the second does not. SQLAlchemy's query objects
don't execute itself and fetch its result until it has *realized*
(for example, looped under :keyword:`for` statement, or applied to
:func:`list()` or :func:`tuple()`), and the only purpose of the
:meth:`~sqlalchemy.orm.query.Query.all()` method is just to realize the query.
In short, query objects are *implicitly* executed when they are *really needed*.

So, execution and fetching the result set of the ``posts`` query happen while
the template is being rendered. As a result, the browser renders whole result
list slightly slowly but gradually. This *lazy* approach helps hasty users
to feel that they are waiting less, but total elapsed time still doesn't become
shorter.

.. image:: _static/lazy-loading.gif

What SQLAlchemy-Future does is helping programmers to parallelize queries
easily. What you have to do is just to place :meth:`~future.Query.promise()`
methods where :meth:`~sqlalchemy.orm.query.Query.all()` methods may come::

    def list_posts():
        session = Session()
        posts = session.query(Post).order_by(Post.created_at.desc()).promise()
        return render_template('list_posts.html', posts=posts)

When the :meth:`~future.Query.promise()` method is called, it creates an
another thread for the future. And the execution of the query has started
running in the created underneath thread. The ``posts`` object, the return
value which is an instance of :class:`~future.Future`, is similar to the lazy
result set object explained above. It is not a real result set physically,
but the *promised* result set. If iteration over ``posts``,
promised result set, has tried, it fetches immediately the *real* result set
of the execution which is run from the underneath thread, or if the result set
isn't prepared, it waits for the underneath thread to finish its query
execution (that may be some prepared already).

As result, similarly to the lazy approach of the above, the browser renders
result list gradually, but unlike to the lazy approach, relatively fast.

.. image:: _static/promised-loading.gif


How to setup
============

In order to make :class:`future.Query` the default query class, use the
``query_cls`` parameter of the :func:`~sqlalchemy.orm.session.sessionmaker()`
function::

    import future
    from sqlalchemy.orm.session import sessionmaker
    Session = sessionmaker(query_cls=future.Query)

Or you can make :class:`future.Query` the query class of a session instance
optionally::

    session = Session(query_cls=future.Query)


How to promise
==============

How to promise a future query is not hard. Just call the
:meth:`~future.Query.promise()` method::

    posts = session.query(Post).promise()

Its return type is :class:`~future.Future` (note that it is not a subtype of
:class:`~future.Query`, so you cannot use rich facilities of
:class:`~future.Query` like :meth:`~sqlalchemy.orm.query.Query.filter`)::

    assert isinstance(posts, future.Future)

Then, iterate this future query (``posts`` in the example) when you really
need it::

    for post in posts:
        print post.title, "by", post.author

If the ``posts`` finished the execution in the another thread, it fetches the
result set immediately. If its execution hasn't finished, the another thread
joins the main thread and it has blocked until its execution has finished.


.. module:: future

:mod:`future` --- References
============================

.. autoclass:: future.Query
  :members:
  :show-inheritance:

.. autoclass:: future.Future
  :members:
  :show-inheritance:


Further informations
====================

It is written by `Hong Minhee`_ and distributed under `MIT license`_.

The source code can be found from the GitHub project page and checked out
via Git.

https://github.com/lunant/SQLAlchemy-Future

.. sourcecode:: bash

   $ git clone git://github.com/lunant/SQLAlchemy-Future.git

.. _Hong Minhee: http://dahlia.kr/
.. _MIT license: http://www.opensource.org/licenses/mit-license.php


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


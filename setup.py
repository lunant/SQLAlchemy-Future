try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


setup(name="SQLAlchemy-Future",
      version="0.1",
      description="SQLAlchemy extension that introduces future and promise "
                  "for query",
      author="Hong Minhee",
      author_email="dahlia" "@" "lunant.com",
      py_modules=["future"],
      install_requires=["SQLAlchemy>=0.6"],
      license="MIT License",
      long_description="Its primary purpose slightly improve the performance "
                       "your applications that uses SQLAlchemy as their ORM "
                       "by introducing *future* and *promise*.",
      classifiers=["Development Status :: 1 - Planning",
                   "Intended Audience :: Developers",
                   "License :: OSI Approved :: MIT License",
                   "Programming Language :: Python",
                   "Topic :: Database :: Front-Ends",
                   "Operating System :: OS Independent"])


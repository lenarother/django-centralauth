django-centralauth
==================

.. image:: https://img.shields.io/pypi/v/django-centralauth.svg
   :target: https://pypi.org/project/django-centralauth/
   :alt: Latest Version

.. image:: https://github.com/lenarother/django-centralauth/workflows/Test/badge.svg?branch=master
   :target: https://github.com/lenarother/django-centralauth/actions?workflow=Test
   :alt: CI Status

.. image:: https://codecov.io/gh/lenarother/django-centralauth/branch/master/graph/badge.svg
   :target: https://codecov.io/gh/lenarother/django-centralauth
   :alt: Coverage Status

.. image:: https://readthedocs.org/projects/django-centralauth/badge/?version=latest
   :target: https://django-centralauth.readthedocs.io/en/stable/?badge=latest
   :alt: Documentation Status


django-centralauth solves the problem of managing user access and permissions
from multiple projects in one central place.


Features
--------

* based on OAuth2 standard.
* provider app to set up your own user-management application.
* client app for delegating authentication and permissions management to provider.


Requirements
------------

django-centralauth supports Python 3 only and requires at least Django 2. and django-oauth-toolkit.


Prepare for development
-----------------------

.. code-block:: shell

    $ poetry install


Now you're ready to run the tests:

.. code-block:: shell

    $ poetry run py.test


Resources
---------

* `Documentation <https://django-centralauth.readthedocs.io>`_
* `Bug Tracker <https://github.com/moccu/django-centralauth/issues>`_
* `Code <https://github.com/moccu/django-centralauth/>`_

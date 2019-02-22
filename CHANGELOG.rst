Changelog
=========

1.2.0 (2019-02-22)
------------------

* django-centralauth now depends on requests-oauthlib >= 1.2.0 and therefore oauthlib >= 3.0
* Fixed some race conditions in middleware (when tokens are refreshed twice)

1.1.2 (2019-02-12)
------------------

* Fix bug in get_or_create of permission sync api endpoint


1.1.1 (2019-01-10)
------------------

* Fix permissions sync - remove deleted permissions


1.1.0 (2018-11-26)
------------------

* Improve permission updates on user sync (don't use clear, just merge source and target set)


1.0.0 (2018-11-22)
------------------

* Initial release of `django-centralauth`

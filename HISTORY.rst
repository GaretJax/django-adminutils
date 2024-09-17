=======
History
=======

0.0.21 - 2024-09-18
===================

* Add ability to hide button in the UI.
* Update styles and HTML for Django 5.


0.0.20 - 2024-09-14
===================

* Support arguments to the `object_action` decorator.
* Allow the buttons to be hidden from the admin interface.


0.0.19 - 2024-09-13
===================

* Save the request object on the ModelAdmin instance (useful if needed when
  rendering fields).


0.0.18 - 2024-02-17
===================

* Add support for ``current_app`` when reversing admin URLs.


0.0.17 - 2023-09-06
===================

* Allow nullables in ``linked_relation`` chains.


0.0.16 - 2023-01-31
===================

* Improve validation of actions.


0.0.15 - 2022-12-23
===================

* Improved form actions.


0.0.14 - 2022-11-27
===================

* Release again as wheel is not built correctly.


0.0.13 - 2022-11-24
===================

* Do not make log_* functions available from the module namespace.


0.0.12 - 2022-11-24
===================

* Support custom action in ``admin_detail_link``.
* Use date widget also in DateRange fields.
* Do not raise an error if ``easy_thumbnails`` is not installed and it is not
  used.
* Nicer lists styling.
* Add support for admin log entries.


0.0.11 - 2022-01-30
===================

* Drop support for Python 2.7.
* Support Django 4.
* Dropped six dependency.
* Added ``pop_fields``, ``EditOnlyInlineMixin``, ``image_preview``, and
  ``formatted_json`` utilities.
* Code linting with black and isort.


0.0.10 - 2020-09-09
===================

* Remove AdminURLFieldWidget which has meanwhile been released upstream.


0.0.9 - 2020-09-09
==================

* Replace ``load staticfiles`` with ``load static``.


0.0.8 - 2020-03-25
==================

* Make easy_thumbnails an optional dependency, again.


0.0.7 - 2020-03-16
==================

* Added a generic form processing action.
* Add an option to not use forms to submit actions.
* Compatibility with Django 2.


0.0.6 - 2017-12-02
==================

* Initial python 2 backport.


0.0.5 - 2017-12-02
==================

* Make easy_thumbnails an optional dependency.


0.0.4 - 2017-11-23
==================

* Fix manifest


0.0.3 - 2017-11-23
==================

* Initial release

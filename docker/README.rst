
===============
 Docker README
===============


Bring the dev server up
=======================

::
   docker compose up

Note that you may have to initialize the python venv manually, see the
Dockerfile.


Manually work with the container
================================

Launch a shell within the container::

  docker compose run --rm --service-ports dev-edms

Launch it with development settings::

   . ~/venv/bin/activate
   cd ~/src/mayan-edms
   ./manage.py runserver --settings=botech.edms_dev.settings 0.0.0.0:8000

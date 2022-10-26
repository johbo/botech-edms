
===============
 Docker README
===============

Launch a shell within the container::

  docker compose run dev-edms

Launch it with development settings::

   . ~/venv/bin/activate
   cd ~/src/mayan-edms
   ./manage.py runserver --settings=botech.edms_dev.settings 0.0.0.0:8000



TODO
====

- [ ] Allow to run dev server via docker compose

IATI-Implementation-Schedules
=============================

Small flask app to view XML implementation schedules. Makes extensive use of
https://github.com/Bjwebb/iati-implementationxml

Copyright (C) 2012 Ben Webb <bjwebb67@googlemail.com>

AGPL v3.0 Licensed

License: AGPL v3.0
==================

Copyright (C) 2012 contributors

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as
    published by the Free Software Foundation, either version 3 of the
    License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

Installation
============

Clone the repository:

    git clone git@github.com:markbrough/IATI-Implementation-Schedules.git

Change into the directory:

    cd IATI-Implementation-Schedules

Set up a virtualenv:

    virtualenv ./pyenv

Activate the virtualenv:

    source ./pyenv/bin/activate

Install the requirements:

    pip install -r requirements.txt

Copy and edit the config.py.tmpl:

    cp config.py.tmpl config.py

Run the server:

    python manage.py runserver

In a production environment, edit and run `fcgi.py`

Import Scripts
==============

Once you've started the environment, the first thing you need to do is to set up the database. You can do that easily. Assuming you're running on http://127.0.0.1:5000 just visit the following pages:

Get the tests:

    http://127.0.0.1:5000/setup

Parse the XML files, located in /xml: 

    http://127.0.0.1:5000/parse

Import new schedules (must be available from a publicly accessible URL): 

    http://127.0.0.1:5000/import

Visit the main page and you should be able to browse your implementation schedules: 

    http://127.0.0.1:5000/

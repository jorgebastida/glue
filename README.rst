Glue is a simple command line tool to generate CSS sprites::

    $ glue source output

The latest documentation is available on http://glue.readthedocs.org

For example using the gorgeous `famfamfam icons <http://www.famfamfam.com/lab/icons/silk/>`_ (4.2Mb) we will get
the following ``icons.png`` (401Kb).

.. image:: https://github.com/jorgebastida/glue/raw/master/docs/_static/famfamfam1.png


And also a ``icons.css`` with all the neccesary CSS classes for this sprite::

    .sprite-icons-zoom_out{ background:url('sprites/icons/icons.png'); top:0; left:0; no-repeat;}
    .sprite-icons-zoom_in{ background:url('sprites/icons/icons.png'); top:0; left:-16; no-repeat;}
    .sprite-icons-zoom{ background:url('sprites/icons/icons.png'); top:-16; left:0; no-repeat;}
    .sprite-icons-xhtml_valid{ background:url('sprites/icons/icons.png'); top:-16; left:-16; no-repeat;}
    ...

# odmltables-for-ldh

odMLtables - Local Data Hub Extension

--------------------------------------

An interface to convert odML structures to and from table-like representations, such as spreadsheets. This Extension of the odMLtables GUI supports semi-automatic uploading of odML-meta-data of
microneurography recordings to the [Local Data Hubs by NFDI4Health](https://www.nfdi4health.de/service/local-data-hub.html). They can be installed using [Docker Deployment LDH](https://github.com/nfdi4health/ldh-deployment). More information about the LDH can be found on [Local Data Hub - Homepage](https://www.nfdi4health.de/service/local-data-hub.html)

The current version supports the streaming to the LDHs only for odML-files that comply to the Experiment and Recording template, which can be found in the [odMLtablesForMNG](https://github.com/Digital-C-Fiber/odMLtablesForMNG/tree/master)
repository. 

odMLtables provides a set of functions to simplify the setup, maintenance and usage of a metadata
management structure using [odML](https://g-node.github.io/python-odml/).
In addition to the [Python API](https://www.python.org/), odMLtables provides its main functionality also
via a graphical user interface.


Execution
-------------

```python odmltables-guy.py```


Dependencies
------------

This extension is based on the original [odMLtables](https://github.com/INM-6/python-odmltables) modified by the [odMLtablesForMNG](https://github.com/Digital-C-Fiber/odMLtablesForMNG/tree/master) extension. 
Which are based on [odML](https://github.com/G-Node/python-odml).


License
---------------------
BSD-3-Clause license

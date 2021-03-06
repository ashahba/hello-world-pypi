Hello World PyPi Project
------------------------

To use this package, simply run::

    >>> import hello_world
    >>> print(hello_world.hello())

To build the project
--------------------
```bash
virtualenv -p python3 .venv3
. .venv3/bin/activate
python setup.py bdist_wheel
```
This will create a the wheel under `dist` folder.


Prepare for PyPi uploading
--------------------------
Create a file name `.pypirc` on your home directory, unless you already have it.
```
[distutils]
index-servers=
    pypitest
#    pypi

[pypitest]
repository = https://test.pypi.org/legacy/
username = <TEST_PYPI_USERNAME>
password = <TEST_PYPI_PASSWORD>

[pypi]
repository: https://upload.pypi.org/legacy/
username = <PYPI_USERNAME>
password = <PYPI_PASSWORD>
```
Ensure `.pypirc` has read/write permission allowed only for current user.

Upload to PyPi
--------------
```
$ twine upload --repository-url https://test.pypi.org/legacy/ dist/ashahba_hello_world-0.0.2-py3-none-any.whl 
Uploading distributions to https://test.pypi.org/legacy/
Enter your username: ashahba 
Enter your password: 
Uploading ashahba_hello_world-0.0.2-py3-none-any.whl
100%|██████████████████████████████████████████████████████████| 6.63k/6.63k [00:02<00:00, 3.29kB/s]

View at:
https://test.pypi.org/project/ashahba-hello-world/0.0.2/
```

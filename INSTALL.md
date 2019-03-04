1. Requirements

     - python >= 3.0
     - numpy

2. Download

        git clone https://github.com/zoeseeger/qcp-python-module

3. Install with python using distutils - requires numpy to be installed

    The original tar.gz is made by 'python3 setup.py sdist' and can be untarred and installed by:

        cd qcp-python-module
        path/to/python3 -m setup_distutils install

    The 'install' step first calls build which copies the source files to parent-directory/build/lib.
It then installs by copying all of these lib files to a standard location for third-party Python
modules if no installation directory has been chosen. This means that all python functions of qcp
can be accessed when in an interactive python session. Install also creates a folder called
build/excecutables in scripts-x.x. The executable uses the version of python used to install qcp.

4. Install with python using setuptools - requires setuptools to be installed

    Setuptools will install all dependencies (numpy) for you

        cd qcp-python-module
        path/to/python3 setup.py install

    See above to see what the install command does.



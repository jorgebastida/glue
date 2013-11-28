FAQ
===

Errors compiling PIL in Snow Leopard
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    /usr/libexec/gcc/powerpc-apple-darwin10/4.2.1/as: assembler (/usr/bin/../libexec/as/ppc/as or
    /usr/bin/../local/libexec/as/ppc/as) for architecture ppc not installed

    Installed assemblers are:

    /usr/bin/../libexec/as/x86_64/as for architecture x86_64

    /usr/bin/../libexec/as/i386/as for architecture i386

    /usr/bin/../libexec/as/arm/as for architecture arm

    _imaging.c:3017: warning: initialization from incompatible pointer type

    _imaging.c:3077: warning: initialization from incompatible pointer type

    _imaging.c:3281: fatal error: error writing to -: Broken pipe

    compilation terminated.

    _imaging.c:3017: warning: initialization from incompatible pointer type

    _imaging.c:3077: warning: initialization from incompatible pointer type

    lipo: can't open input file: /var/tmp//ccsCS1Iv.out (No such file or directory)

    error: command 'gcc-4.2' failed with exit status 1

The reason for this error is that Apple has removed from Xcode the assembler for PPC, while the core system retains their PPC images in the fat binaries.  If you run ``file /usr/bin/python`` you will likely find the following::

    /usr/bin/python: Mach-O universal binary with 3 architectures
    /usr/bin/python (for architecture x86_64):  Mach-O 64-bit executable x86_64
    /usr/bin/python (for architecture i386):    Mach-O executable i386
    /usr/bin/python (for architecture ppc7400): Mach-O executable ppc

Python compiles C extensions with the same compiler flags that Python itself was compiled with.

The solution? Install ``glue`` using this line::

    $ sudo env ARCHFLAGS='-arch i386 -arch x86_64' pip install glue


Usage
=====

Launching the Chat Console and Connecting to Kernels
----------------------------------------------------

Start Chat Console with::

    chconsole

or::

    jupyter chconsole

After starting the console will ask the user to choose a connection file. The user may choose an existing file
or cancel. If an existing file is chosen, the console will attach to a running Jupyter kernel specified by the file.
Otherwise, the console will launch its own kernel.

The console tries to guess a suitable user name when starting, usually the user's login name. Having a unique
user name is useful when several users collaborate while connected to one kernel. It is possible to specify
the user name explicitly when launching the console with the user option::

    chconsole --user <user name>

where <user name> stands for the user name to be used.

For convenience, the script::

    chc-python

launches an IPython kernel to which consoles may connect. After starting the script, the user can choose
an existing connection file or a new file name. If the connection file already exists then the script attempts
to start a kernel with the specifications of the connection file. Otherwise, a new connection file will be created.

SSH Tunnels to Kernels
----------------------

To establish connections between the kernel and the console, the kernel, that is, its ip address,
must be accessible from the console. Sometimes, for example, if the kernel is behind a firewall, it may be necessary
to create an ssh tunnel to the kernel. The Jupyter framework contains helpful options for creating such an ssh tunnel.
See the documentation of Jupyter `qtconsole <http://qtconsole.readthedocs.org/en/latest/#ssh-tunnels>`_
for details on this process.

Connections through ssh can be configured in the configuration file as well as on the command line.
In the configuration file, specify the required ssh key with JupyterConsoleApp.sshkey and the ip address
of the ssh server with JupyterConsoleApp.sshserver. The ssh server can also be given on the command line with
the option '--ssh'. If the user's login name on the client running the console differs from the login name
on the ssh server, specify the server-side login name as part of the ip address: name @ ip address.

Connecting to a Sage Appliance
------------------------------

`Sage <http://www.sagemath.org/>`_ is a mathematics software system that runs on an IPython kernel.
It is possible to connect Chat Console, as any other Jupyter clients, to a running Sage notebook.
Ensure that the Sage virtual machine accepts ssh login, as it is explained in the Sage documentation.
As of version 7.0 of Sage, after starting the notebook, the connection file of the notebook can be found in
the folder /home/sage/.local/share/jupyter/runtime. Copy the connection file to the computer to run
the console and establish a connection to the notebook through an ssh tunnel with login name sage.

Chat and Command Entry
----------------------

For command entry Chat Console provides all the features, users who know Jupyter
`qtconsole <http://qtconsole.readthedocs.org/en/latest/>`_ may expect.
However, unlike qtconsole, all input is entered in a special input field at the bottom of the console's window.
This feature allows showing inputs by other users immediately when they have been entered.

In addition, Chat Console provides features supporting chat communications among multiple users
connected to the same kernel which qtconsole lacks.
The view menu provides an option which shows and hides the names of the users
responsible for the corresponding inputs.
Furthermore, when the cursor is at the beginning of the entry field, hitting the tab key switches between
chat and command entry modes. Chat messages can also be sent in command entry mode by starting them with a
pound sign, such as::

    # Hello, is there anybody?

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

Sharing the Connection File
---------------------------

When multiple users connect to the same kernel, the consoles used for connecting need to have access to
the connection file of the kernel. Therefore the connection file must be shared among the users.
There are different ways of sharing. For example, the file can be distributed by e-mail.
However, another convenient possibility is to create a shared network folder
which is accessible to all users and where the kernel saves its connection file. The included script
chc-python for starting the IPython kernel allows to browse for any accessible location to store the
connection file. Alternatively, when the IPython kernel is launched on the command line with 'ipython kernel',
the '-f' option allows to specify the connection file, including its desired path.

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
As of Sage's version 7.0, after starting the notebook, the connection file of the notebook can be found in
the folder /home/sage/.local/share/jupyter/runtime. Copy the connection file to the computer to run
the console and establish a connection to the notebook through an ssh tunnel with login name 'sage'.

Chat and Command Entry
----------------------

For command entry Chat Console provides all the features, users who know Jupyter
`qtconsole <http://qtconsole.readthedocs.org/en/latest/>`_ may expect.
However, unlike qtconsole, all input is entered in a special input field at the bottom of the console's window.
This feature allows showing inputs by other users immediately when they have been entered.

In addition, Chat Console supports chat communications among multiple users
connected to the same kernel which qtconsole lacks.
When the cursor is at the beginning of the entry field, hitting the tab key switches between
chat and command entry modes. Chat messages can also be sent in command entry mode by starting them with a
pound sign, such as::

    # Hello, is there anybody?

Furthermore, the view menu provides an option which shows and hides the names of the users
responsible for the corresponding chat and command inputs.

Special Key Strokes
-------------------

When in the entry area, various key strokes have special effects.

**Command entry**

Enter
    Execute the text that has been entered

Shift-Enter
    Execute the entered text even if it may have syntax errors

Ctrl-Enter
    Enter a new line and do not execute

Alt-<
    Move the cursor to the start of the input field

Alt->
    Move the cursor to the end of the input field

Alt-B
    Move the cursor to the start of the current word

Alt-F
    Move the cursor to the end of the current word

Alt-Backspace
    Delete from the cursor position to the beginning of the current word and save the deleted text in the kill ring

Alt-D, Alt-Delete or Ctrl-Delete
    Delete from the cursor position to the end of the current word and save the deleted text in the kill ring

Alt-Y
    Rotate the kill ring after retrieving the first entry from the kill ring with Ctrl-Y

Ctrl-I
    Interrupt the kernel

Ctrl-G
    Restart the kernel

Ctrl-O
    Release focus and move to the area where the commands  and outputs are show

Ctrl-D or Delete
    Delete the current character at the cursor position

Ctrl-K
    Delete until the end of the line and store the deleted text in the kill ring

Ctrl-U
    Delete until the beginning of the line, clear any text selection and store the deleted text in the kill ring

Ctrl-Y
    Retrieve the last text saved in the kill ring

Ctrl-Backspace
    Delete until the beginning of the line and store the deleted text in the kill ring

Tab
    If the cursor is at the beginning of the entry field, switch to chat mode; otherwise try to
    complete the code contained in the entry field; otherwise insert spaces for indentation

Esc
    Clear the entry field

**Chat entry**

Most of the key strokes for navigation and editing from command entry are available.
However, the kill ring is not used and the corresponding key strokes are disabled.

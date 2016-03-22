__author__ = 'Manfred Minimair <manfred@minimair.org>'

from zz_scratch.zz_console_split.modified_qtconsole import qtconsoleapp


#-----------------------------------------------------------------------------
# Main entry point
#-----------------------------------------------------------------------------

def main():
    #qtconsoleapp.JupyterQtConsoleApp.existing = 'tester'
    qtconsoleapp.main()

if __name__ == '__main__':
    main()


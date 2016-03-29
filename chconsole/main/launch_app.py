from chconsole.main.chat_console_app import ChatConsoleApp

__author__ = 'Manfred Minimair <manfred@minimair.org>'


# -----------------------------------------------------------------------------
# Main entry point
# -----------------------------------------------------------------------------

def main():
    #Use if existing kernel: kernel-tester.json
    # ChatConsoleApp.existing = 'tester'
    ChatConsoleApp.launch_instance()

if __name__ == '__main__':
    main()

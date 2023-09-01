from window_terminal import WindowTerminal
from datetime import datetime

class LogWindow:
    '''A window terminal that shows the log info and save log files.'''

    def __init__(self, logfile='log.log'):
        self.window = WindowTerminal.create_window()
        self.logfile = logfile
        self._isopen = False

    def open_window(self):
        '''Open the LogWindow.'''
        self.window.open()
        self.window.print('Log Window opened...')
        self.window.print(f'Log file will be written to {self.logfile}...')
        self._isopen = True

    def wait_for_enter(self):
        '''Wait until user press enter key.'''
        if not self._isopen:
            self.log('')
            return 
        self.window.input('Enter to continue...')
    
    def log(self, message: str, type='log'):
        '''Print the log message on the log window and save the message to the logfile. 
        When the type is specified as "error" or part of it, the print message will be 
        red in foreground and white in background.'''
        now = datetime.now()
        if not self._isopen:
            print('Log window not open!')
            with open(self.logfile, 'a+', encoding='utf-8') as f:
                f.write(now.strftime('%Y-%m-%d %H:%M:%S\n'))
                f.write('[ERROR] Log window not open!\n\n')
            return
        
        self.window.print(now.strftime('\n%Y-%m-%d %H:%M:%S'))

        # \033[47m is red foreground and \033[31m is white background.
        if type.lower() in 'error':
            self.window.print('\033[47m\033[31m', end='')
        self.window.print(f'{type.upper()}: {message}\033[0m')
        
        with open(self.logfile, 'a+', encoding='utf-8') as f:
            f.write(now.strftime('%Y-%m-%d %H:%M:%S\n'))
            if type.lower() in 'error':
                f.write('[ERROR] ')
            f.write(f'{message}\n\n')

# This is an instance of LogWindow that can be use directly.
log_wd = LogWindow()
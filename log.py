from window_terminal import WindowTerminal
from datetime import datetime

class LogWindow:
    def __init__(self, logfile='log.log'):
        self.window = WindowTerminal.create_window()
        self.logfile = logfile
        self._isopen = False

    def open_window(self):
        self.window.open()
        self.window.print('Log Window opened...')
        self.window.print(f'Log file will be written to {self.logfile}...')
        self._isopen = True

    def wait_for_enter(self):
        if not self._isopen:
            self.log('')
            return 
        self.window.input('Enter to continue...')
    
    def log(self, message: str, type='log'):
        now = datetime.now()
        if not self._isopen:
            print('Log window not open!')
            with open(self.logfile, 'a+', encoding='utf-8') as f:
                f.write(now.strftime('%Y-%m-%d %H:%M:%S\n'))
                f.write('[ERROR] Log window not open!\n\n')
            return
        
        self.window.print(now.strftime('\n%Y-%m-%d %H:%M:%S'))

        if type.lower() in 'error':
            self.window.print('\033[47m\033[31m', end='')
        self.window.print(f'{type.upper()}: {message}\033[0m')
        
        with open(self.logfile, 'a+', encoding='utf-8') as f:
            f.write(now.strftime('%Y-%m-%d %H:%M:%S\n'))
            if type.lower() in 'error':
                f.write('[ERROR] ')
            f.write(f'{message}\n\n')

log_wd = LogWindow()
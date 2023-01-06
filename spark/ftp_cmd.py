from FTP_manager import FTP

ftp = FTP()
ftp.load_info()
ftp.connect()

file_infos = []

while True:
    cmd = input('>> ')
    if cmd == 'quit': break
    elif cmd == 'nlst': print(ftp.session.nlst())
    elif cmd == 'dir': ftp.session.dir()
    elif cmd == 'list': 
        ftp.session.retrlines(cmd, file_infos.append)
        print('file_infos:', file_infos)
    else: print(f'  res: {ftp.session.voidcmd(cmd)}')

ftp.close()
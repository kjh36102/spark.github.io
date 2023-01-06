import ftplib
import os

class FTP:
    def __init__(self) -> None:
        self.session = ftplib.FTP()
        self.hostname = None
        self.username = None
        self.password = None
        self.basepath = '/'
        self.port = 21
        self.encoding = 'utf-8'
    
    def connect(self):
        self.session.connect(host=self.hostname, port=int(self.port))
        self.session.encoding = self.encoding
        self.session.login(user=self.username, passwd=self.password)

        self.session.cwd(self.basepath)

    def close(self):
        try: self.session.quit()
        except Exception as e:
            print('Failed to close FTP: ', e)
            self.session.close()

    def load_info(self):
        #ftp_info.yml 있는지 확인하기
        info_found_state = os.path.isfile('spark/ftp_info.yml')

        if info_found_state:
            #파일 읽어서 변수 초기화
            print('[! Loading FTP info from ftp_info.yml...]')

            f_ftp_info = open('spark/ftp_info.yml', 'r')

            while True:
                line = f_ftp_info.readline()
                if not line: break

                raw_line = line[:-1]

                if 'hostname:'  in raw_line: self.hostname = raw_line.split(' ') [1]
                if 'username:'  in raw_line: self.username = raw_line.split(' ') [1]
                if 'password:'  in raw_line: self.password = raw_line.split(' ') [1]
                if 'basepath:'  in raw_line: self.basepath = raw_line.split(' ') [1]
                if 'port:'      in raw_line: self.port     = raw_line.split(' ') [1]
                if 'encoding:'  in raw_line: self.encoding = raw_line.split(' ') [1]

            print('\t...Done')
        else: self.configure()

    def configure(self):
        print("[! Please input your web FTP info. Don't worry. It will not shown to public.]")
        hostname = input('hostname : ')
        username = input('username : ')
        password = input('password : ')
        basepath = input('basepath (ex=/HDD1/embed): ')
        port = input('port (default=21) : ')
        encoding = input('encoding (default=utf-8) : ')

        self.hostname = hostname
        self.username = username
        self.password = password
        if basepath != '': self.basepath = basepath
        if port     != '': self.port = port
        if encoding != '': self.encoding = encoding

        f_ftp_info = open('spark/ftp_info.yml', 'w')

        f_ftp_info.write(f'hostname: {self.hostname}\n')
        f_ftp_info.write(f'username: {self.username}\n')
        f_ftp_info.write(f'password: {self.password}\n')
        f_ftp_info.write(f'basepath: {self.basepath}\n')
        f_ftp_info.write(f'port:     {self.port}\n')
        f_ftp_info.write(f'encoding: {self.encoding}\n')

        f_ftp_info.close()

        print('[! Your FTP info is saved into ftp_info.yml.]')
    

def load_ftp_info(init=False):
    #ftp_info.yml 있는지 확인하기
    info_found_state = os.path.isfile('spark/ftp_info.yml')

    #init일 때
    

    #ftp_info.yml 없으면 사용자로부터 로그인 정보 수집
    if info_found_state == False or init == True:
        print("[! Please input your web FTP info. Don't worry. It will not shown to public.]")
        hostname = input('hostname : ')
        username = input('username : ')
        password = input('password : ')
        basepath = input('basepath (ex=/HDD1/embed): ')
        port = input('port (default=21) : ')
        encoding = input('encoding (default=utf-8) : ')

        if basepath == '': basepath = '/'
        if port == '': port = '21'
        if encoding == '': encoding = 'utf-8'

        #파일로 저장할지 물어보기
        print('[? Do you want to save this in ftp_info.yml? It will not pushed to repository.]')
        print('  (Only recommend on your PC)')
        save_flag = input('save? (y/n) >> ')

        #대답이 y면 저장하기
        if save_flag == 'y':
            f_ftp_info = open('spark/ftp_info.yml', 'w')

            f_ftp_info.write('hostname: ' + hostname + '\n')
            f_ftp_info.write('username: ' + username + '\n')
            f_ftp_info.write('password: ' + password + '\n')

            f_ftp_info.write('basepath: ' + basepath + '\n')
            f_ftp_info.write('port: ' + port + '\n')
            f_ftp_info.write('encoding: ' + encoding + '\n')

            f_ftp_info.close()

            print('[! Your FTP info successfully saved into ftp_info.yml.]')

    #ftp_info.yml 이 존재하면 정보 불러오기
    print('[! Loading FTP info from ftp_info.yml...]')
    f_ftp_info = open('spark/ftp_info.yml', 'r')
    while True:
        line = f_ftp_info.readline()
        if not line: break

        raw_line = line[:-1]

        if 'hostname:' in raw_line: hostname = raw_line.split(' ') [1]
        if 'username:' in raw_line: username = raw_line.split(' ') [1]
        if 'password:' in raw_line: password = raw_line.split(' ') [1]
        if 'basepath:' in raw_line: basepath = raw_line.split(' ') [1]
        if 'port:' in raw_line: port = raw_line.split(' ') [1]
        if 'encoding:' in raw_line: encoding = raw_line.split(' ') [1]

    print('\t...Done')

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
from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer


def main():
    authorizer = DummyAuthorizer()
    # authorizer.add_user("user", "123456", ".", perm="elr")  # user:用户名设置；   123456：密码  perm:权限
    authorizer.add_anonymous(".")  # 设置访问目录（.:表示当前目录）
    handler = FTPHandler
    handler.authorizer = authorizer
    server = FTPServer(("192.168.4.114", 21), handler)  # 设置ftp的ip和端口（默认21）
    server.serve_forever()


if __name__ == '__main__':
    main()

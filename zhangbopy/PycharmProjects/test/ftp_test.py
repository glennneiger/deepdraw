from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer


def main():
    authorizer = DummyAuthorizer()
    authorizer.add_user("user","123456",".",perm="elr")
    handler = FTPHandler
    handler.authorizer = authorizer
    server = FTPServer(("192.168.4.114",21),handler)
    server.serve_forever()


if __name__ == '__main__':
    main()

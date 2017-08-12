from Commander import Commander, Command
import socket
from threading import Thread

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = ("ec2-54-190-25-113.us-west-2.compute.amazonaws.com", 8888)

print('connecting to %s port %s' % server_address)
sock.connect(server_address)


class TestCmd(Command):
    def send(self, message):
        sock.send(message.encode())

    def do_echo(self, *args):
        '''echo - Just echos all arguments'''
        return ' '.join(args)
    def do_raise(self, *args):
        raise Exception('Some Error')


commander = Commander('Test', cmd_cb=TestCmd())




def run():
    while 1:
        data = sock.recv(1024)
        if not data: break
        data = data.decode().replace("\n", "")
        commander.output(data)

t = Thread(target=run)
t.daemon = True
t.start()

# start main loop
commander.loop()







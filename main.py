import asyncio
import json

clients = []

COLORS = ["magenta", "green", "purple", "pink"]

BANNER = """
Welcome To RezChat!

Commands
-------
/who           | List Connected People
/help          | List This Menu
/nick <name>   | Change Your Nick
/color <color> | Change Your Name Color (magenta, green, purple, pink)
-------
"""

log = open("log.txt", "a")


class ClientProtocol(asyncio.Protocol):
    def __init__(self):
        self.name = None
        self.name_color = None
        self.current_room = 0
        clients.append(self)

    def connection_made(self, transport):
        peername = transport.get_extra_info('peername')
        print('Connection from {}'.format(peername))
        self.transport = transport
        self.get_name()

    def data_received(self, data):
        message = data.decode().replace("\n", "")

        if self.name is not None:
            print("{} SENT {}".format(self.name, message))
            log.write("{} SENT {}".format(self.name, message) + "\n")

        if self.name is None:
            self.name = message[:20].replace(" ", "")
            self.write("Your Name Has Been Set To: {}".format(self.name))
            self.broadcast("{} Has Connected!".format(self.name))
            print("{} JOIN".format(self.name))

        elif message in "":
            pass

        elif message in "/who":
            self.write("Online Users\n-----------")
            for client in clients:
                self.write(client.name)
            self.write("-----------")

        elif message in "/help":
            self.write(BANNER)

        elif message.startswith("/nick "):
            self.change_nick(message)

        elif message.startswith("/color "):
            self.change_color(message)

        else:
            self.broadcast(self.name + ": " + message[:100])

    def connection_lost(self, exc):
        print("{} DC".format(self.name))
        self.broadcast("{} Has Disconnected".format(self.name) )
        self.transport.close()

        for i, client in enumerate(clients):
            if client == self:
                clients.pop(i)

    def write(self, message):
        print("{} WRITE".format(self.name))
        data = {
            "message": (message + "\n"),
            "color": self.name_color
        }
        self.transport.write(json.dumps(data).encode())

    def get_name(self):
        self.write(BANNER)
        self.write("Please Enter A Name:")

    def broadcast(self, message):
        print("{} BROADCAST".format(self.name))
        for client in clients:
            client.write(message)

    def change_nick(self, message):
        nick = message.split(" ")[1]
        self.write("{} has changed their name to {}".format(self.name, nick))
        self.name = nick

    def change_color(self, message):
        color = message.split(" ")[1].lower()
        if color not in COLORS:
            self.write("Invalid Color")
            return
        self.name_color = color
        self.write("Color Updated")

loop = asyncio.get_event_loop()
# Each client connection will create a new protocol instance
coro = loop.create_server(ClientProtocol, '0.0.0.0', 8888)
server = loop.run_until_complete(coro)

# Serve requests until Ctrl+C is pressed
print('Serving on {}'.format(server.sockets[0].getsockname()))
try:
    loop.run_forever()
except KeyboardInterrupt:
    pass

# Close the server
server.close()
loop.run_until_complete(server.wait_closed())
loop.close()
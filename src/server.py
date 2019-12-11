#  Created by Artem Manchenkov
#  artyom@manchenkoff.me
#
#  Copyright © 2019
#
#  Сервер для обработки сообщений от клиентов
#
#  Ctrl + Alt + L - форматирование кода
#
from twisted.internet import reactor
from twisted.internet.protocol import ServerFactory, connectionDone
from twisted.protocols.basic import LineOnlyReceiver

globalhistory = []

class ServerProtocol(LineOnlyReceiver):
    factory: 'Server'
    login: str = None
    def send_history(self):
        # lastMessages = globalhistory[-10:]
        for m in globalhistory[-10:]:
            self.sendLine(m.encode())
    def connectionMade(self):
        # Потенциальный баг для внимательных =)
        self.factory.clients.append(self)

    def connectionLost(self, reason=connectionDone):
        self.factory.clients.remove(self)

    def lineReceived(self, line: bytes):
        content = line.decode()
        if self.login is not None:
            if content == 'bye':
                for user in self.factory.clients:
                    if user is not self:
                        user.sendLine((self.login + " kaput..").encode())  # предупреждаем остальных
                self.connectionDone()
            else:
                content = f"{self.login} sagt: {content}"
                globalhistory.append(content)
                for user in self.factory.clients:
                    if user is not self:
                        user.sendLine(content.encode())
        else:
            # login:admin -> admin
            if content.startswith("login:"):
                # всячесие проверки:
                maybename = content.replace("login:", "")
                if maybename != "":  # страхуемся от пустого имени
                    da = False
                    for user in self.factory.clients:
                        da |= (maybename == user.login)
                    if (da):  # если в списке
                        self.sendLine("Dieser Name ist bereits vergeben!".encode())  # этот уже есть
                    elif maybename == "admin":
                            self.sendLine("Willst du auf den Arsch bekommen?".encode())  # этот притворяется админом
                    else:
                            for user in self.factory.clients:
                                user.sendLine((maybename + " ist da!").encode())  # предупреждаем остальных
                            self.login = maybename
                            self.factory.clients.append(self)
                            self.sendLine(("Willkommen, " + self.login).encode())  # привет бобёр!
                            self.send_history()
                else:
                    self.sendLine("Login ist leer!".encode())
            else:
                self.sendLine("Falsches Login!".encode())

class Server(ServerFactory):
    protocol = ServerProtocol
    clients: list

    def startFactory(self):
        self.clients = []
        print("Server started")

    def stopFactory(self):
        print("Server closed")


reactor.listenTCP(1234, Server())
reactor.run()

import socket
import base64
from hashlib import md5
import time
import sys
from config import getConfig
from exceptions import *

# Diccionario de comandos del protocolo
protocolCommands = {
  "hello": "helloiam",
  "length": "msglen",
  "message": "givememsg",
  "checksum": "chkmsg",
  "bye": "bye"
}

def decodeUTF(message):
    return message.decode('utf-8').strip('\n')

def decodeBase64(message):
    return decodeUTF((base64.b64decode(message)))

def getCheckSum(message):
    return md5(message.encode('utf-8')).hexdigest()

def getException(message):
    if (type(protocolErrors.get(message))==type(object)):
        raise protocolErrors.get(message)

def createTCPSocket(serverAddress, serverPort, tcpTimeout):
    try:
        socketTCP = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socketTCP.settimeout(tcpTimeout)
        socketTCP.connect((serverAddress, serverPort))
        return socketTCP
    except ConnectionRefusedError:
        print('Ocurrió un problema conectandose con el servidor')
        return sys.exit()
    except socket.timeout:
        print('Se excedió el máximo tiempo de espera al servidor')
        return sys.exit()


def createUDPSocketListener(clientAddress, clientPort, udpTimeout):
    socketUDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    socketUDP.settimeout(udpTimeout)
    socketUDP.bind((clientAddress, clientPort))
    return socketUDP

def commandHello(socketTCP, username):
    try:
        command = protocolCommands['hello']
        socketTCP.send(f"{command} {username}".encode())
        data = socketTCP.recv(1024)
        data = decodeUTF(data)
        getException(data)
    except InvalidUserName as error:
        print(error.message)
        return sys.exit()
    except InvalidSrcIp as error:
        print(error.message)
        return sys.exit()
    except socket.timeout:
        print('Se excedió el máximo tiempo de espera al servidor')
        return sys.exit()
    except Exception:  
        print('Ocurrió un problema en la conexión con el servidor')
        return sys.exit()

def commandLength(socketTCP):
    try:
        command = protocolCommands['length']
        socketTCP.send(command.encode())
        data = socketTCP.recv(1024)
        data = decodeUTF(data)
        if (data):
            return data.split()[1]
    except socket.timeout:
        print('Se excedió el máximo tiempo de espera al servidor')
        return sys.exit()
    except Exception:
        print('Ocurrió un problema en la conexión con el servidor')
        return sys.exit()

def commandMessage(socketTCP, clientAddress, portUDP, udpTimeout, length, retriesNumer):
    tryNumber = 1
    while (tryNumber <= retriesNumer):
        try:
            command = protocolCommands['message']
            socketTCP.send((f"{command} {portUDP}").encode())
            socketUDP = createUDPSocketListener(clientAddress, portUDP, udpTimeout)
            data = socketTCP.recv(1024)
            data = decodeUTF(data)
            getException(data)
            data = socketUDP.recv(1024)
            message = decodeBase64(data)
            if (len(message)==int(length)):
                return message
            else:
                tryNumber += 1
        except InvalidUdpPort as error:
            print(error.message)
            return sys.exit()
        except socket.timeout:
            pass
        except Exception:
            print('Ocurrió un problema en la conexión con el servidor')
            return sys.exit()
        finally:
            socketUDP.close()
            tryNumber += 1

def commandCheckSum(socketTCP,checkSum):
    try:
        command = protocolCommands['checksum']
        socketTCP.send((f"{command} {checkSum}").encode())
        data = socketTCP.recv(1024)
        data = decodeUTF(data)
        getException(data)
    except InvalidCheckSumFormat as error:
        print(error.message)
        return sys.exit()
    except BadCheckSum as error:
        print(error.message)
        return sys.exit()
    except socket.timeout:
        print('Se excedió el máximo tiempo de espera al servidor')
        return sys.exit()
    except Exception:
        print('Ocurrió un problema en la conexión con el servidor')
        return sys.exit()

def commandBye(socketTCP):
    try:
        command = protocolCommands['bye']
        socketTCP.send(command.encode())
        data = socketTCP.recv(1024)
        data = decodeUTF(data)
    except socket.timeout:
        print('Se excedió el máximo tiempo de espera al servidor')
        return sys.exit()
    except Exception:
        print('Ocurrió un problema en la conexión con el servidor')
        return sys.exit()

def client(config, username, serverAddress, serverPort):
    USERNAME = username
    SERVER_ADDRESS = serverAddress
    SERVER_PORT = serverPort
    CLIENT_ADDRESS = config['CLIENT_ADDRESS']
    UDP_CLIENT_PORT = config['UDP_CLIENT_PORT']
    RETRIES_NUMBER = config['RETRIES_NUMBER']
    TCP_SOCKET_TIMEOUT = config['TCP_SOCKET_TIMEOUT']
    UDP_SOCKET_TIMEOUT = config['UDP_SOCKET_TIMEOUT']

    socketTCP = createTCPSocket(SERVER_ADDRESS, SERVER_PORT, TCP_SOCKET_TIMEOUT)

    try:
        commandHello(socketTCP, USERNAME)
        length = commandLength(socketTCP)
        message = commandMessage(socketTCP, CLIENT_ADDRESS, UDP_CLIENT_PORT, UDP_SOCKET_TIMEOUT, length, RETRIES_NUMBER)
        checkSum = getCheckSum(message)
        commandCheckSum(socketTCP,checkSum)
        commandBye(socketTCP)
        print(message)
    except socket.timeout:
        print('Se excedió el máximo tiempo de espera al servidor')
    finally:
        socketTCP.close()


if __name__ == "__main__":
    config = getConfig()
    if (len(sys.argv)>=2):
        username = sys.argv[1]
    else:
        username = config['USERNAME']
    if (len(sys.argv)>=3):
        serverAddress = sys.argv[2]
    else:
        serverAddress = config['SERVER_ADDRESS']
    if (len(sys.argv)>=4):
        serverPort = int(sys.argv[3])
    else:
        serverPort = config['SERVER_PORT']
    client(config, username, serverAddress, serverPort)

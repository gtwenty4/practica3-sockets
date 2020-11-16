# Excepción para cuando el username es inválido
class InvalidUserName(Exception):

    def __init__(self):
        self.message = "El usuario introducido es inválido"

# Excepción para cuando la ip de origen del usuario es inválido
class InvalidSrcIp(Exception):

    def __init__(self):
        self.message = "La ip de origen no coincide con la ip del usuario"

# Excepción para cuando el puerto UDP del cliente es inválido
class InvalidUdpPort(Exception):

    def __init__(self):
        self.message = "El puerto UDP del cliente no es valido"

# Excepción para cuando el formato del checksum es invalido
class InvalidCheckSumFormat(Exception):

    def __init__(self):
        self.message = "El formato de checksum enviado es inválido"

# Excepción para cuando el checksum está malo
class BadCheckSum(Exception):

    def __init__(self):
        self.message = "El checksum no coincide con el checksum del mensaje enviado"

# Diccionario de excepciones
protocolErrors = {
  "error invalid user name": InvalidUserName,
  "error invalid src ip": InvalidSrcIp,
  "error invalid udp port": InvalidUdpPort,
  "error invalid checksum format": InvalidCheckSumFormat,
  "error bad checksum": BadCheckSum
}
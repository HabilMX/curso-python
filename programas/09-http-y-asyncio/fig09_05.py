# fig09_05.py
import socket
from urllib.request import urlopen

print("tiempo límite global:", socket.getdefaulttimeout())

try:
    urlopen("http://127.0.0.1:8099/notificaciones", timeout=1)
except TimeoutError as error:
    print("se acabó el tiempo:", error)

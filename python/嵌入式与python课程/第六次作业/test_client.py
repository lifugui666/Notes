import socket

client = socket.socket()
client.connect(('localhost', 12345))

file = open('./send.txt', 'rb')
data = file.read(1024)
client.send(data)

file.close()
client.close()
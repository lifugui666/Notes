import socket

server = socket.socket()
server.bind(('localhost',12345))
server.listen(5)

print("listening...")

client, addr = server.accept()
print("connection from ", addr)

file = open("./received.txt", "wb")
data = client.recv(1024)
file.write(data)

file.close()
client.close()
server.close()
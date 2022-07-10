#!usr/bin/python3
import socket
import sys
import binascii


def send_udp_message(message, address, port):
    message = message.replace(" ", "").replace("\n", "")
    server_address = (address, port)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.sendto(binascii.unhexlify(message), server_address)
        data, _ = sock.recvfrom(4096)
    finally:
        sock.close()
        
    return binascii.hexlify(data).decode("utf-8")

def createQueryMessage(userInput):
    urlArr=userInput.split(".")

    hexQuery=""
    for i in urlArr:
        curr="0"+str(len(i)) if len(str(len(i)))==1 else str(len(i))

        hexQuery=hexQuery+curr+" "
        for j in i:
            hexQuery=hexQuery+str(hex(ord(j)))[2:]+" "    
    return hexQuery

def getName(url):
    headerJunkInitial="AA AA 01 00 00 01 00 00 00 00 00 00 "
    headerJunkFinal=" 00 00 01 00 01"


    message=headerJunkInitial+createQueryMessage(url)+headerJunkFinal

    response = send_udp_message(message, "8.8.8.8", 53)

    answerCount=int(response[14:16])

    ipRough=[]
    for i in range(answerCount):
        curridx=i*32
        ipAsHex=(response[(len(response)-8-curridx):(len(response)-curridx)])
        ipRough.append([int(ipAsHex[0:2],16),int(ipAsHex[2:4],16),int(ipAsHex[4:6],16),int(ipAsHex[6:8],16)])
    
    
    ip=""

    for i in ipRough:
        address=""

        for j in i:
            address=address+str(j)+"."

        ip=ip+(address[:-1])+","
        
    ip=ip[:-1]

    return ip



port=int(sys.argv[1])

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((socket.gethostname(), port))
    s.listen()
    connectionsocket, address = s.accept()
    with connectionsocket:
        print(f"Client connected: {address}")
        while True:
            data = connectionsocket.recv(1024)
            if not data:
                break

            data=getName(data.decode('utf-8'))

            # data=' '.join(getName(data.decode('utf-8')))
            connectionsocket.sendall(data.encode('utf-8'))

connectionsocket.close()
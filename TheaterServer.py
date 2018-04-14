import socket, threading, time
from _thread import *

numTickets = 50
kioskCounter = 0
ticketLock = threading.Lock()

def ticketSale(connection):
    global kioskCounter
    global numTickets
    global movieSocket
    while True:
        data = connection.recv(1024).decode()

        if data:
            if data == "kioskhandshake":
                connection.sendall(str(kioskCounter).encode())
                print("Handshake completed with kiosk #" + str(kioskCounter))
                kioskCounter += 1

            else:
                currentKiosk, ticketType, num = data.split(":", 2)

                if currentKiosk == "movieServer":
                    if ticketType == "play":
                        print("Request for " + num + " tickets forwarded from movie server")
                else:
                    print("Request for " + num + " tickets received from kiosk #" + currentKiosk)

                num = int(num)

                if ticketType == "movie":
                    data = "theaterServer:" + ticketType + ":" + str(num)

                    #time.sleep(5)
                    sendMovieSocket.sendall(data.encode())
                    print("Request for " + str(num) + " tickets forwarded to movie server")
                    receipt = sendMovieSocket.recv(1024).decode()
                    connection.sendall(receipt.encode())

                elif ticketType == "play":
                    ticketLock.acquire()
                    if numTickets >= num:
                        numTickets -= num
                        receipt = "theaterServer:success:" + str(num)
                    else:
                        receipt = "theaterServer:failed:" + str(num)
                    ticketLock.release()
                    connection.sendall(receipt.encode())

                #time.sleep(5)
        else:
            connection.close()

def Main():
    requestListener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    requestListener.bind(("", 8001))
    requestListener.listen(1)   # Change later

    global sendMovieSocket
    sendMovieSocket, address = requestListener.accept()
    recvMovieSocket, address = requestListener.accept()
    start_new_thread(ticketSale, (recvMovieSocket,))

    while True:
        connection, address = requestListener.accept()
        start_new_thread(ticketSale, (connection,))

    kioskListener.close()

if __name__ == '__main__':
    Main()
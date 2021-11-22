import socket
import os
import random
import pathlib


HEADER = 64
PORT = 5050
SERVER = socket.gethostbyname(socket.gethostname())  # gets the ip for me automatically (actually returns home)
AADR = (SERVER, PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(AADR)


def send(msg, conn):
    message = msg.encode(FORMAT)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    conn.send(send_length)
    conn.send(message)


def receive(conn):
    msg_length = conn.recv(HEADER)  # stops here until client connects (that's why threads are used)
    msg_length = msg_length.decode(FORMAT)
    if msg_length:
        msg_length = int(msg_length)
        msg = conn.recv(msg_length).decode(FORMAT)
        return msg


def clear_list(lines):
    # clears a string list of \n
    for line in lines:
        if line == '\n' or line == '':
            lines.remove(line)
        elif '\n' in line:
            line.remove('\n')
    return lines


def average_list(lst):
    if len(lst) == 0:
        return 0
    else:
        sum = 0
        for i in range(len(lst)):
            sum += lst[i]
        return sum / len(lst)

def main():
    print("starting server")
    server.listen()
    print(f"server is listening on {SERVER}")
    while True:
        conn, addr = server.accept()
        connected = True
        while connected:
            print(f"connected on: {AADR}")
            right = []
            quit = False
            dir_path = pathlib.Path(__file__).parent.resolve()
            while not quit:
                while True:
                    path = os.path.join(dir_path, "lyrics/")  # path to the lyrics folder
                    file_names = os.listdir(path)
                    name = random.choice(file_names)  # get the file's name
                    file_path = os.path.join(path, name)  # full name for accessing the file
                    if name.split('.')[1] == "txt":  # if the file isn't a txt file search again
                        break
                file = open(file_path)  # open the file
                lines = file.readlines()  # create an array of the individual lines in the file
                lines = [s.rstrip() for s in lines]  # remove the empty lines (\n) from the array
                lines = clear_list(
                    lines)  # remove the completely empty lines ("") from the array and remove \n from all the lines
                line = random.choice(lines)  # pick a random line
                print(line)  # print it
                send(line, conn)  # send it to the client
                send("Guess song name: ", conn)  # send "Guess song name: " to the client
                user_input = receive(conn)  # receive answer from client
                print(f"user_input: {user_input}")
                if user_input == "quit":
                    send("quitting program", conn)
                    print("quitting program")
                    connected = False
                    quit = True
                elif user_input == '\n' or ' ' in user_input or '' == user_input:
                    send("try again", conn)
                    print("try again")
                elif user_input in name:
                    send("right", conn)
                    print("right")
                    right.append(1)
                else:
                    send("wrong", conn)
                    print("wrong")
                    right.append(0)
                file.close()
            score = average_list(right) * 100
            send(f"score:{score}%", conn)
            print(f"score:{score}%")

        conn.close()


if __name__ == '__main__':
    main()

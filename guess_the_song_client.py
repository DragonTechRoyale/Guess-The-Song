import tkinter as tk
import socket
import time
import threading
from queue import Queue

HEADER = 64
PORT = 5050
SERVER = socket.gethostbyname(socket.gethostname())  # gets the ip for me automatically (actually returns home)
AADR = (SERVER, PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"


def retrieve_input(textbox, song_row, wrong_or_right, q, song_row_q, wrong_or_right_q):
    textbox_input = textbox.get("1.0", 'end-1c')
    print(f"TEXTBOX_INPUT: {textbox_input}")
    q.put(textbox_input)
    song_row_text = song_row_q.get()
    song_row['text'] = song_row_text
    print(f"song_row_text: {song_row_text}")
    wrong_or_right_text = wrong_or_right_q.get()
    wrong_or_right['text'] = wrong_or_right_text
    print(f"wrong_or_right_text: {wrong_or_right_text}")
    textbox.delete("1.0", 'end-1c')


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


def behind_the_curtain(sock, q, song_row_q, wrong_or_right_q, score_q):
    user_input = ""

    while user_input != "quit":
        song_row = receive(sock)
        song_row_q.put(song_row)
        print(f"song_row: {song_row}")
        receive(sock)
        user_input = q.get()
        send(user_input, sock)
        print(f"user_input: {user_input}")
        wrong_or_right = receive(sock)
        wrong_or_right_q.put(wrong_or_right)
        print(f"wrong_or_right: {wrong_or_right}")
    score = receive(sock)
    score_q.put(score)
    print(score)


def quit_game(root, q, score_q, song_row_title, song_row, answer, wrong_or_right,  send_answer_button, quit_game_button,
              textbox):
    q.put("quit")
    song_row_title.destroy()
    song_row.destroy()
    answer.destroy()
    wrong_or_right.destroy()
    time.sleep(0.1)  # wait for the score to come from the server
    if score_q.empty():
        score_label = tk.Label(root, text="No score yet")
        print(f"score_label_text: No score yet")
    else:
        score_label_text = score_q.get()
        score_label = tk.Label(root, text=score_label_text)
        print(f"score_label_text: {score_label_text}")
    score_label.config(font=("Courier", 14))
    score_label.pack()
    send_answer_button.destroy()
    quit_game_button.destroy()
    textbox.destroy()
    exit_button = tk.Button(root, text="Exit", command=lambda: quit())
    exit_button.pack()


def main():
    q = Queue()  # queue for communicating between the GUI and networking code in the textbox
    song_row_q = Queue()  # queue for communicating between the GUI and networking code in the song row
    wrong_or_right_q = Queue()  # queue for communicating between the GUI and networking code in the Answer
    score_q = Queue()  # list for communicating between the GUI and networking code in the Score

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(AADR)

    back = threading.Thread(target=behind_the_curtain, args=(sock, q, song_row_q, wrong_or_right_q, score_q, ))
    back.start()

    root = tk.Tk()

    root.geometry("300x300")

    textbox = tk.Text(root, height=5, width=52)

    title = tk.Label(root, text="Guess The Song")  # title of the program
    title.config(font=("Courier", 20))
    song_row_title = tk.Label(root, text="Song Row:")  # title for "Song Row:"
    song_row_title.config(font=("Courier", 16))
    song_row = tk.Label(root, text="No song row *")  # the row that the server sends
    song_row.config(font=("Courier", 14))
    answer = tk.Label(root, text="Answer:")  # title for "Answer:"
    answer.config(font=("Courier", 16))
    wrong_or_right = tk.Label(root, text="wrong or right answer *")  # the wrong or write answer frm the server
    wrong_or_right.config(font=("Courier", 14))

    send_answer_button = tk.Button(root, text="send answer", command=lambda: retrieve_input(textbox, song_row,
                                                                                            wrong_or_right, q,
                                                                                            song_row_q,
                                                                                            wrong_or_right_q))
    quit_game_button = tk.Button(root, text="Quit game", command=lambda: quit_game(root, q, score_q, song_row_title,
                                                                                   song_row, answer, wrong_or_right,
                                                                                   send_answer_button, quit_game_button,
                                                                                   textbox))

    title.pack()
    song_row_title.pack()
    song_row.pack()
    textbox.pack()
    answer.pack()
    wrong_or_right.pack()
    send_answer_button.pack()
    quit_game_button.pack()

    song_row_text = song_row_q.get()
    song_row['text'] = song_row_text
    print(f"song_row_text: {song_row_text}")

    tk.mainloop()


if __name__ == '__main__':
    main()

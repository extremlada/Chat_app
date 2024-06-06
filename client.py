import threading
import socket
import argparse
import os
import sys
import tkinter as tk

class Send(threading.Thread):

    # Listens for user input from command line

    # Sock the connection sock object

    # name (str) : The username provided by the user

    def __init__(self, sock, name):
        super().__init__()
        self.sock = sock
        self.name = name

    def run(self) -> None:
        # Listen for user input from the command line and send it to the
        # Typing "Quit" will close the connection and exit the app

        while True:
            print('{}: '.format(self.name), end='')
            sys.stdout.flush()
            message = sys.stdin.readline()[:-1]

            # if we type "Quit" we leave the chatroom

            if message == "Quit":
                self.sock.sendall('Server: {} has left the chat'.format(self.name).encode('UTF-8'))
                break

            # send message to server for broadcasting

            else:
                self.sock.sendall('{}: {} '.format(self.name, message).encode('UTF-8'))

        print('\nQuitting...')
        self.sock.close()
        os._exit(0)

class Receive(threading.Thread):

    # Listens to incoming message from the server

    def __init__(self, sock, name):
        super().__init__()
        self.sock = sock
        self.name = name
        self.messages = None

    def run(self) -> None:

        # Receives data from the server and displays it on the gui

        while True:
            message = self.sock.recv(1024).decode('UTF-8')

            if message:
                if self.messages:
                    self.messages.insert(tk.END, message)
                    print('\r{}\n{}: '.format(message, self.name), end='')

                else:
                    print('\r{}\n{}: '.format(message, self.name), end='')

            else:
                print('\n No. We have lost connection to the server!')
                print('\nQuitting...')
                self.sock.close()
                os.exit(0)

class Client:

    # Management of client-server connection and integration of GUI

    def __init__(self, host, port):

        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.name = None
        self.messages = None

    def start(self):

        print('Trying to connect to {}:{}...'.format(self.host, self.port))

        self.sock.connect((self.host, self.port))

        print('Successfully connected to {}:{}'.format(self.host, self.port))


        print()
        self.name = input('Your name: ')

        print()

        print('Welcome, {}! Getting ready to send and receive messages...'.format(self.name))

        # Create send and receive threads

        send = Send(self.sock, self.name)

        receive = Receive(self.sock, self.name)

        # Start the send and receive thread

        send.start()
        receive.start()

        self.sock.sendall('Server: {} has joined the chat. say hi'.format(self.name).encode('UTF-8'))
        print("\rReady! Leave the chatroom anytime by typing 'Quit'\n")
        print('{}: '.format(self.name), end='')

        return receive

    def send(self, textInput):

        # Sends textInput data from the GUI
        message = textInput.get()
        textInput.delete(0, tk.END)
        self.messages.insert(tk.END, '{}: {}'.format(self.name, message))

        # Type 'Quit' to Leave the chatroom
        if message == "Quit":
            self.sock.sendall('Server: {} has left the chat'.format(self.name))
            print('\nQuitting...')
            self.sock.close()
            os.exit(0)

        # SEND message to the server for broadcasting
        else:
            self.sock.sendall('{}: {}'.format(self.name, message).encode('UTF-8'))


def main(host, ports):
    # Initialize and run our GUI app

    client = Client(host, ports)
    receive = client.start()

    window = tk.Tk()
    window.title("Chatting")

    fromMessage = tk.Frame(master=window)
    scrollBar = tk.Scrollbar(master=fromMessage)
    messages = tk.Listbox(master=fromMessage, yscrollcommand=scrollBar.set)
    scrollBar.pack(side=tk.RIGHT, fill=tk.Y, expand=False)
    messages.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    client.messages = messages
    receive.messages = messages

    fromMessage.grid(row=0, column=0, columnspan=2, sticky="nsew")
    fromEntry = tk.Frame(master=window)
    textInput = tk.Entry(master=fromEntry)

    textInput.pack(fill=tk.BOTH, expand=True)
    textInput.bind("<Return>", lambda x: client.send(textInput))
    textInput.insert(0, "Your message here")

    btnSend = tk.Button(master=window, text='Send', command=lambda: client.send(textInput))
    fromEntry.grid(row=1, column=0, padx=10, sticky="ew")
    btnSend.grid(row=1, column=1, pady=10, sticky="ew")

    window.rowconfigure(0, minsize=500, weight=1)
    window.rowconfigure(1, minsize=50, weight=0)
    window.columnconfigure(0, minsize=500, weight=1)
    window.columnconfigure(1, minsize=200, weight=0)

    window.mainloop()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Chatroom Server")
    parser.add_argument('host', help=('Interface the server listens at'))
    parser.add_argument('-p', metavar='PORT', type=int, default=1060, help=('TCP port(default 1060)'))

    args = parser.parse_args()

    main(args.host, args.p)
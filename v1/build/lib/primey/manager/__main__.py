import os
import time
import math
import json
import click
import pathlib
import threading
import argparse
import logging
import socket
import collections
import v1 as v1
import manager_operations as manager_operations

LOGGER = logging.getLogger(__name__)

class Manager:
    def __init__(self, host, port):
        LOGGER.info(
            f"Starting Server at host={host} port={port} pwd= {os.getcwd()}"
        )
        self.host = host
        self.port = port
        self.job_queue = collections.deque()
        self.alive = True
        self.job_id = 0
        shutdown_event = threading.Event()

        job_thread = threading.Thread(target=job_handler,
                                            daemon=True,
                                            args=(shutdown_event, self.job_id, self.job_queue))
        job_thread.start()

        self.host_tcp_server()
        shutdown_event.set()

        job_thread.join()
    
        # Member function in charge of running a constant TCP Server
    def host_tcp_server(self):
        """
        Host the Manager TCP Server Socket.

        Runs the TCP server at (self.host, self.port)
        until a shutdown message is received
        """
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            # Bind the socket to the server
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind((self.host, self.port))
            sock.listen()

            # Socket accept() will block for a maximum of 1 second.  If you
            # omit this, it blocks indefinitely, waiting for a connection.
            sock.settimeout(1)
            while True:
                # Wait for a connection for 1s.
                # The socket library avoids consuming
                # CPU while waiting for a connection.
                try:
                    clientsocket, address = sock.accept()
                except socket.timeout:
                    continue
                LOGGER.debug(address)

                clientsocket.settimeout(1)
                LOGGER.debug("")
                # Receive data, one chunk at a time.
                # If recv() times out before we
                # can read a chunk, then go back to the top of the loop and try
                # again.  When the client closes the connection, recv() returns
                # empty data, which breaks out of the loop.
                with clientsocket:
                    message_chunks = []
                    while True:
                        try:
                            LOGGER.debug("")
                            data = clientsocket.recv(4096)
                        except socket.timeout:
                            LOGGER.debug("")
                            continue
                        if not data:
                            LOGGER.debug("")
                            break
                        message_chunks.append(data)
                LOGGER.debug("")
                # Decode list-of-byte-strings to UTF8 and parse JSON data
                message_str = b''.join(message_chunks)
                message_str = message_str.decode("utf-8")
                try:
                    LOGGER.debug("")
                    message_dict = json.loads(message_str)
                except json.JSONDecodeError:
                    continue

                # Send the decoded message_dict as a string to op handler
                manager_operations.manage_operations(message_dict, self.job_queue)

                # Shutdown manager if shutdown received
                try:
                    if message_dict["message_type"] == "shutdown":
                        LOGGER.debug("")
                        self.alive = False
                        return
                except KeyError:
                    LOGGER.debug("")
                    continue
    
def job_handler(shutdown_event, job_id, job_queue):
    LOGGER.info(f"Job Thread Started")
    while not shutdown_event.is_set():
        if len(job_queue) > 0:
            LOGGER.debug(f"{len(job_queue)}")
            job_dict = job_queue.popleft()
            LOGGER.debug(job_dict)
            output_file = pathlib.Path(job_dict["output_directory"])/f"job_{job_id}"
            job_id += 1
            n = int(job_dict["n"])
            if n <= 1:
                logging.error("n must be positive int greater than 1")
                with open(output_file, "w") as f:
                    f.write(f"Invalid Input ({n}): n must be positive int greater than 1")
                return
            
            if v1.is_prime(n):
                LOGGER.debug(f"{n} is prime")
                with open(output_file, "w") as f:
                    f.write(f"{n} is prime")
            else:
                LOGGER.debug(f"{n} is not prime")
                with open(output_file, "w") as f:
                    f.write(f"{n} is not prime")


@click.command()
@click.option("--host", "host", default="localhost")
@click.option("--port", "port", default=6000)
@click.option("--logfile", "logfile", default=None)
@click.option("--loglevel", "loglevel", default="info")
def main(host, port, logfile, loglevel):
    if logfile:
        handler = logging.FileHandler(logfile)
    else:
        handler = logging.StreamHandler()
    formatter = logging.Formatter(
        f"Server:{port} [%(levelname)s] %(message)s"
    )
    handler.setFormatter(formatter)
    root_logger = logging.getLogger()
    root_logger.addHandler(handler)
    root_logger.setLevel(loglevel.upper())

    Manager(host, port)




if __name__ == "__main__":
    main()
import multiprocessing
import grpc
import numpy as np
import socket
import time

from PyQt5.QtWidgets import QApplication

from . import slm_pb2
from . import slm_pb2_grpc

from .slm_server import SLMDisplay


def is_port_in_use(port):
    """Check if the given port is in use by trying to bind to it
    Returns boolean
    """
    host = ''
    in_use = False
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind((host, port))
        except:
            in_use = True
    return in_use


def run_slm(port):
    """Run an SLM server on a given port
    """
    app = QApplication([])
    display = SLMDisplay(f"SLM-{port}", app, port)
    app.exec()


class SLMController:
    """An SLM Controller which runs a server in a separate process and can send
    commands to it on that port.
    The server halts when the parent process is killed.
    """

    def __init__(self, port):
        self.port = port

    def start_server(self):
        try:
            self.slm_server.terminate()
        except:
            pass

        if is_port_in_use(self.port):
            print("Port already in use. Choose another port.")
        else:
            self.slm_server = multiprocessing.Process(
                target=run_slm, args=(self.port,))
            self.slm_server.daemon = True
            self.slm_server.start()
        time.sleep(0.1)

    def stop_server(self):
        self.slm_server.terminate()

    def set_image(self, image: np.ndarray):
        """Put the given uint8 numpy array onto the slm screen
        """
        with grpc.insecure_channel(f"localhost:{self.port}") as channel:
            stub = slm_pb2_grpc.SLMStub(channel)
            stub.SetImage(slm_pb2.Image(image_bytes=image.tobytes(),
                                        width=image.shape[0], height=image.shape[1]))

    def set_screen(self, screen: int):
        """Put the slm on the given screen
        """
        with grpc.insecure_channel(f"localhost:{self.port}") as channel:
            stub = slm_pb2_grpc.SLMStub(channel)
            stub.SetScreen(slm_pb2.Screen(screen=screen))

import multiprocessing
from PyQt5.QtWidgets import QApplication

from slm_server import SLMDisplay


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
    display = SLMDisplay(f"SLM-{port}", app.screens()[0], port)
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

        self.slm_server = multiprocessing.Process(
            target=run_slm, args=(self.port,))
        self.slm_server.daemon = True
        self.slm_server.start()

    def stop_server(self):
        self.slm_server.terminate()

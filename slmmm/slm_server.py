import asyncio

import PyQt5.QtWidgets as qw
import PyQt5.QtCore as qc
import PyQt5.QtGui as qg
import numpy as np

import grpc
from grpc import aio

from slmmm import slm_pb2
from slmmm import slm_pb2_grpc


async def serve(worker, port) -> None:
    """Start a grpc server on the given port
    """
    server = grpc.aio.server()
    slm_pb2_grpc.add_SLMServicer_to_server(SLM(worker), server)
    listen_addr = f'[::]:{port}'
    server.add_insecure_port(listen_addr)
    await server.start()
    try:
        await server.wait_for_termination()
    except KeyboardInterrupt:
        # Shuts down the server with 0 seconds of grace period. During the
        # grace period, the server won't accept new connections and allow
        # existing RPCs to continue within the grace period.
        await server.stop(0)


class SLM(slm_pb2_grpc.SLMServicer):
    def __init__(self, worker):
        self.worker = worker

    async def SetImage(self, request, context):
        try:
            new_image = np.frombuffer(request.image_bytes, dtype=np.uint8).reshape(
                (request.height, request.width))
            self.worker.set_image.emit(new_image)
            return slm_pb2.Response(completed=True)
        except ValueError:
            return slm_pb2.Response(completed=False, error="Couldn't set the image")

    async def SetImageColour(self, request_iterator, context):
        try:
            image_bytes = []
            for request in request_iterator:
                image_bytes.append(np.frombuffer(request.image_bytes, dtype=np.uint8).reshape(
                    request.height, request.width))
            assert len(image_bytes) == 3, "Image should have 3 channels"

            self.worker.set_image_colour.emit(np.array(image_bytes))
        except ValueError:
            return slm_pb2.Response(completed=False, error="Couldn't set the image")
        except AssertionError:
            return slm_pb2.Response(completed=False, error="Image should have 3 channels")

    async def SetScreen(self, request, context):
        self.worker.set_screen.emit(request.screen)
        return slm_pb2.Response(completed=True)

    async def SetPosition(self, request, context):
        self.worker.set_position.emit(request.x, request.y)
        return slm_pb2.Response(completed=True)


class SLMWorker(qc.QObject):
    """A worker to interact with the grpc server.
    This gets placed in a different thread to the main thread and communicates
    with the display through qsignals.
    """
    start = qc.pyqtSignal()
    set_image = qc.pyqtSignal(np.ndarray)
    set_image_colour = qc.pyqtSignal(np.ndarray)
    set_screen = qc.pyqtSignal(int)
    set_position = qc.pyqtSignal(int, int)

    def __init__(self, port, *args, **kwargs):
        super().__init__()
        self.start.connect(self.run)
        self.port = port

    @qc.pyqtSlot()
    def run(self):
        asyncio.run(serve(self, self.port))


class SLMDisplay(qc.QObject):
    """Class to display an SLM pattern fullscreen onto a monitor
    """

    def __init__(self,
                 window_title,
                 application,
                 port,
                 slm_display_size=None,
                 slm_position=(0, 0)):
        super().__init__()

        self.app = application

        self.thread = qc.QThread()
        self.thread.start()

        self.worker = SLMWorker(port)
        self.worker.set_image.connect(self.set_image)
        self.worker.set_image_colour.connect(self.set_image_colour)
        self.worker.set_position.connect(self.set_position)
        self.worker.set_screen.connect(self.set_screen)

        self.worker.moveToThread(self.thread)
        self.worker.start.emit()

        self.image_ref = None

        self.scene = qw.QGraphicsScene()

        self.screen = None

        # this turns off any annoying border the window might have
        self.set_screen(0)

    @qc.pyqtSlot(int, int)
    def set_position(self, x, y):
        pass

    @qc.pyqtSlot(int)
    def set_screen(self, screen_index):
        """Set the screen the plot is to be displayed on
        destroys the current window, and creates a new one with the same values
        """
        screens = self.app.screens()
        if len(screens) <= screen_index:
            print("No screen at that index, setting to last screen")
            new_screen = screens[-1]
        else:
            new_screen = screens[screen_index]
        shape = (new_screen.geometry().width(),
                 new_screen.geometry().height())
        if self.screen is not None:
            self.screen.close()
        self.screen = qw.QGraphicsView()
        self.scene.setSceneRect(0, 0, *shape)
        self.screen.setStyleSheet("border: 0px")
        self.screen.setScene(self.scene)
        self.screen.setHorizontalScrollBarPolicy(qc.Qt.ScrollBarAlwaysOff)
        self.screen.setVerticalScrollBarPolicy(qc.Qt.ScrollBarAlwaysOff)
        self.screen.show()
        self.screen.windowHandle().setScreen(new_screen)
        self.screen.showFullScreen()
        self.screen.setWindowTitle("SLM")

    @qc.pyqtSlot(np.ndarray)
    def set_image(self, image):
        '''Set the image which is being displayed on the fullscreen plot
        '''
        if self.image_ref is not None:
            self.scene.removeItem(self.image_ref)
        qimage = qg.QImage(image, *image.shape, qg.QImage.Format_Grayscale8)
        pixmap = qg.QPixmap(qimage)
        self.image_ref = self.scene.addPixmap(pixmap)

    @qc.pyqtSlot(np.ndarray)
    def set_image_colour(self, image):
        '''Set the image which is being displayed on the fullscreen plot
        '''
        if self.image_ref is not None:
            self.scene.removeItem(self.image_ref)
        qimage = qg.QImage(image, image.shape[1], image.shape[2], qg.QImage.Format_RGB888)
        pixmap = qg.QPixmap(qimage)
        self.image_ref = self.scene.addPixmap(pixmap)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Run an SLM server')
    parser.add_argument('port', type=int,
                        help='an integer for the accumulator')

    args = parser.parse_args()
    app = qw.QApplication([])
    screen = SLMDisplay("hi", app, args.port)
    app.exec()

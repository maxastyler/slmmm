import asyncio
import logging

import PyQt5.QtWidgets as qw
import PyQt5.QtCore as qc
import PyQt5.QtGui as qg
import pyqtgraph as pg
import socket

import numpy as np

import grpc
from grpc import aio

import slm_pb2
import slm_pb2_grpc

import multiprocessing


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
                (request.width, request.height))
            self.worker.set_image.emit(new_image)
            return slm_pb2.Response(completed=True)
        except ValueError:
            return slm_pb2.Response(completed=False, error="Couldn't set the image")

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
        self.worker.set_position.connect(self.set_position)
        self.worker.set_screen.connect(self.set_screen)

        self.worker.moveToThread(self.thread)
        self.worker.start.emit()

        self.image_ref = None

        self.scene = qg.QGraphicsScene()
        self.screen = qw.QGraphicsView()
        # this turns off any annoying border the window might have
        self.screen.setStyleSheet("border: 0px")
        self.screen.setScene(self.scene)

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
        self.scene.setSceneRect(0, 0, *shape)
        self.screen.show()
        self.screen.windowHandle().setScreen(new_screen)
        self.screen.showFullScreen()

    @qc.pyqtSlot(np.ndarray)
    def set_image(self, image):
        '''Set the image which is being displayed on the fullscreen plot
        '''
        if self.image_ref is not None:
            self.scene.removeItem(self.image_ref)
        qimage = qg.QImage(image, *image.shape, qg.QImage.Format_Grayscale8)
        pixmap = qg.QPixmap(qimage)
        self.image_ref = self.scene.addPixmap(pixmap)


class FullScreenPlot(pg.PlotWidget):
    """Class to display a numpy array as a fullscreen plot
    """

    def __init__(self,
                 screen_size,
                 slm_display_size=None,
                 slm_position=(0, 0)):
        '''Take in the screen size which to plot to, the slm display size if
        it differs from the screen size and the slm position if it needs to
        be placed at a specific point on the plot

        The slm position is taken from the top-left corner of the image
        '''
        super().__init__()

        self.screen_size = None
        self.slm_display_size = None
        self.slm_position = None
        self.image = None

        # update the size parameters
        if slm_display_size is None:
            slm_display_size = screen_size
        self.screen_size = screen_size
        self.slm_display_size = slm_display_size
        self.slm_position = slm_position
        self.image = np.zeros(self.slm_display_size)
        self.LUT = None

        self.set_limits()
        self.hideAxis('left')
        self.hideAxis('bottom')

        # set a placeholder image
        self.image_display = pg.ImageItem(self.image)
        self.addItem(self.image_display)

    def set_limits(self):
        '''Set the limits of the display
        '''
        self.setLimits(xMin=0 - self.slm_position[0],
                       xMax=self.screen_size[0] - self.slm_position[0],
                       yMin=self.slm_display_size[1] - self.screen_size[1] +
                       self.slm_position[1],
                       yMax=self.slm_display_size[1] + self.slm_position[1],
                       minXRange=self.screen_size[0],
                       maxXRange=self.screen_size[0],
                       minYRange=self.screen_size[1],
                       maxYRange=self.screen_size[1])

    @qc.pyqtSlot(np.ndarray)
    def set_and_update_image(self, new_image, **kwargs):
        '''Take a numpy array and set it as the new image,
        then update the display
        '''
        self.image = new_image
        self.image_display.setImage(self.image, **kwargs)

    @qc.pyqtSlot(np.ndarray)
    def update_LUT(self, LUT):
        '''Update the lookup table for the plot
        '''
        self.image_display.setLookupTable(LUT)
        self.LUT = LUT

    def update_SLM_size(self, size):
        '''Update the display size of the slm
        '''
        self.slm_display_size = size
        self.set_limits()

    def closeEvent(self, event):
        """Override the close event, so it just hides
        """
        self.hide()


def qt_setup(port):
    import sys
    app = qw.QApplication(sys.argv)
    # w = SLMDisplay("Stinky butts", app.screens()[0])
    # d = SLMDisplay("hi", app.screens()[0], port)
    # d.show()
    size = app.screens()[0].size()
    w, h = (size.width(), size.height())
    im_w, im_h = (w//2, h//2)
    im = qg.QImage(np.random.randint(0, 100, (im_w, im_h), dtype=np.uint8),
                   im_w, im_h, qg.QImage.Format_Grayscale8)
    pm = qg.QPixmap(im)
    scene = qg.QGraphicsScene()
    scene.addPixmap(pm)
    scene.setSceneRect(0, 0, w, h)
    gview = qg.QGraphicsView()
    gview.setScene(scene)
    gview.setHorizontalScrollBarPolicy(qc.Qt.ScrollBarAlwaysOff)
    gview.setVerticalScrollBarPolicy(qc.Qt.ScrollBarAlwaysOff)
    # window = qw.QMainWindow()
    # window.setCentralWidget(gview)
    # window.showFullScreen()
    gview.showFullScreen()
    # gview.setContentsMargins(qc.QMargins())
    gview.setStyleSheet("border: 0px")
    # gview.translate(-10, -10)
    app.exec()


if __name__ == '__main__':
    # p = multiprocessing.Process(target=qt_setup, args=(8080,))
    # p.daemon = True
    # p.start()
    # p_2 = multiprocessing.Process(target = qt_setup, args = (7069,))
    # p_2.start()
    # import slm_client
    # import time
    # print("HI THREE")
    # print(is_port_in_use(7069))
    # asyncio.run(slm_client.run())
    # while True:
    # time.sleep(1)
    # print("OI OIO OI OI ")
    a = qw.QApplication([])
    screen = SLMDisplay("hi", a, 2002)
    im = np.random.randint(0, 255, (100, 100), dtype=np.uint8)
    screen.set_image(im)
    a.exec()
    # time.sleep(2)
    # print(is_port_in_use(8080))
    # p.terminate()
    # print("\n\n\nHI THERE :))))\n\n\n")
    # p.terminate()
    # p_2.terminate()

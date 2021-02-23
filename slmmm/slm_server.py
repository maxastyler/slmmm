import asyncio
import logging

import PyQt5.QtWidgets as qw
import PyQt5.QtCore as qc
import pyqtgraph as pg

import numpy as np

import grpc
from grpc import aio

import slm_pb2
import slm_pb2_grpc


async def serve(worker) -> None:
    server = grpc.aio.server()
    slm_pb2_grpc.add_SLMServicer_to_server(SLM(worker), server)
    listen_addr = '[::]:50051'
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

    async def SetPhaseMask(self, request, context):
        try:
            new_image = np.frombuffer(request.phasemask, dtype=np.complex128).reshape(
                (request.width, request.height))
            self.worker.set_image.emit(new_image)
            return slm_pb2.Response(completed=True)
        except ValueError:
            return slm_pb2.Response(completed=False, error="Got a value error")

    async def SetLUT(self, request, context):
        try:
            new_lut = np.frombuffer(request.lut, dtype=float)
            self.worker.set_lut.emit(new_lut)
            return slm_pb2.Response(completed=True)
        except ValueError:
            return slm_pb2.Response(completed=False, error="Got a value error")


class SLMWorker(qc.QObject):
    start = qc.pyqtSignal()
    set_image = qc.pyqtSignal(np.ndarray)
    set_lut = qc.pyqtSignal(np.ndarray)

    def __init__(self, *args, **kwargs):
        super().__init__()
        self.start.connect(self.run)

    @qc.pyqtSlot()
    def run(self):
        asyncio.run(serve(self))


class SLMDisplay(qc.QObject):
    """Class to display an SLM pattern fullscreen onto a monitor
    """

    def __init__(self,
                 window_title,
                 screen,
                 slm_display_size=None,
                 slm_position=(0, 0)):
        super().__init__()

        self.thread = qc.QThread()
        self.thread.start()

        self.worker = SLMWorker()
        self.worker.set_image.connect(self.set_image)
        self.worker.set_lut.connect(self.set_LUT)

        self.worker.moveToThread(self.thread)
        self.worker.start.emit()

        self.screen = screen

        self.window = None
        self.create_screen(screen, slm_display_size, slm_position,
                           window_title)

    def set_screen(self, screen):
        """Set the screen the plot is to be displayed on
        destroys the current window, and creates a new one with the same values
        """
        slm_display_size = self.window.slm_display_size
        slm_position = self.window.slm_position
        image = self.window.image
        window_title = self.window.windowTitle()
        LUT = self.window.LUT

        self.create_screen(screen, slm_display_size, slm_position,
                           window_title)
        if LUT is not None:
            self.window.update_LUT(LUT)
        self.window.set_and_update_image(image)

    def create_screen(self, screen, slm_display_size, slm_position,
                      window_title):
        """Set up the slm display on the given screen
        """
        self.screen = screen

        if self.window is not None:
            self.window.close()

        self.window = FullScreenPlot(
            (screen.geometry().width(), screen.geometry().height()),
            slm_display_size, slm_position)

        self.window.show()
        self.window.windowHandle().setScreen(screen)
        self.window.showFullScreen()
        self.window.setWindowTitle(window_title)

    @qc.pyqtSlot(np.ndarray)
    def set_image(self, image, **kwargs):
        '''Set the image which is being displayed on the fullscreen plot
        '''
        self.window.set_and_update_image(image, **kwargs)

    @qc.pyqtSlot(np.ndarray)
    def set_LUT(self, lut):
        """Set the lookup table
        """
        self.window.update_LUT(lut)


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


if __name__ == '__main__':
    import sys
    app = qw.QApplication(sys.argv)
    w = SLMDisplay("Stinky butts", app.screens()[0])
    app.exec()

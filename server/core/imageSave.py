from threading import Thread
import queue

from core.timer import Timer


class ImageSave(Thread):
    def __init__(self, queue):
        Thread.__init__(self)

        self.queue = queue
        self.isRunning = True

    def run(self):
        i = 0

        timer = Timer("thread loop")

        while True:

            if not self.isRunning:
                break
            if self.queue.empty():
                pass
            else:

                data = self.queue.get()

                image = data['image']
                camera = data['camera']
                index = data['index']

                image.save(
                    "C:/Users/norby/Pictures/test/kamera"+str(camera)+"/"+str(index)+'.bmp')
                self.queue.task_done()

                i = i+1

        print("stopped")

        return "Stopped"

    def stop(self):

        self.isRunning = False

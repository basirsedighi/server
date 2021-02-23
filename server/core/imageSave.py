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
            if self.queue.empty():
                pass
            else:

                image = self.queue.get()

                image.save(
                    "C:/Users/norby/Pictures/test/kamera1/"+str(i)+'.jpg')
                self.queue.task_done()

                i = i+1

                if not self.isRunning:
                    break

        print("stopped")

        return "Stopped"

    def stop():

        self.isRunning = False

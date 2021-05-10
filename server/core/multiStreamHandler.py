
class MyMultiStreamHandler(cvb.MultiStreamHandler ):

    def __init__(self, streams):
        super().__init__(streams)
        self.rate_counter = cvb.RateCounter()

    # called in the interpreter thread to setup additionla stuff.
    def setup(self, streams):
        super().setup(streams)
        print("setup")

    # called in the interpreter thread to tear down stuff from setup.
    def tear_down(self, streams):
        super().tear_down(streams)
        print("tear_down")

    # called from the aqusition thread
    def handle_async_stream(self, streams):
        super().handle_async_stream(streams)
        print("handle_async_streams")

    # called from the aqusition thread
    def handle_async_wait_result(self, wait_result_list ):
        super().handle_async_wait_result(wait_result_list )
        self.rate_counter.step()
        print(wait_result_list)
        for image,status in wait_result_list:
            
            print("New image: " + image.__class__.__name__ + " " + str(image) + " | Status: " + str(status) + " | Buffer Index: " + str(image.buffer_index))

    # print messurement results
    def eval(self):
        print("Acquired with: " + str(self.rate_counter.rate) + " fps")

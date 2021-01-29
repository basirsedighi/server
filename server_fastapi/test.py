import os
import asyncio
import cvb
import cv2 as cv


rate_counter = None


async def async_acquire(port):

    global rate_counter
    with cvb.DeviceFactory.open(os.path.join(cvb.install_path(), "drivers", "CVMock.vin"), port=port) as device:
        stream = device.stream
        stream.start()

        rate_counter = cvb.RateCounter()

        for i in range(0, 100):
            result = await stream.wait_async()
            image, status = result.value
            cv.
            rate_counter.step()
            if status == cvb.WaitStatus.Ok:
                print("Buffer index: " + str(image.buffer_index) +
                      " from stream: " + str(port))

        stream.abort()


watch = cvb.StopWatch()

loop = asyncio.get_event_loop()
loop.run_until_complete(asyncio.gather(
    async_acquire(port=0)))
loop.close()

duration = watch.time_span

print("Acquired on port 0 with " + str(rate_counter.rate) + " fps")
print("Overall measurement time: " + str(duration / 1000) + " seconds")

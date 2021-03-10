 # CVBpy Example Script
 #
 # 1. Open the CVMock.vin driver.
 # 2. Asynchronously acquire images.
 # 3. Measure the frame rate and print results.
 #
 # Note: can be extended to multible cameras.
 
import os
import asyncio
import cvb 
from core.timer import Timer 

image_number = 1 
rate_counter = None
 
async def async_acquire(port):
    global rate_counter
    global image_number
    with cvb.DeviceFactory.open(os.path.join(cvb.install_path(), "drivers", "GenICam.vin"), port=port) as device:
        stream = device.stream
        stream.start()

        rate_counter = cvb.RateCounter()
 
        for i in range(0, 100):
            
            result = await  stream.wait_async()
            image, status = result.value
            rate_counter.step()
            if status == cvb.WaitStatus.Ok:
                image.save("C:/Users/tor_9/Documents/test_jpg/async/"+ str(image_number)+".jpg")
                image_number += 1
                print("Buffer index: " + str(image.buffer_index) + " from stream: " + str(port))
                
 
        stream.abort()
     
 
 
 
watch = cvb.StopWatch()
 
loop = asyncio.get_event_loop()
loop.run_until_complete(asyncio.gather(
    async_acquire(port=0))) 
 
loop.close()

duration = watch.time_span
 
print("Acquired on port 0 with " + str(rate_counter.rate) + " fps")
print("Overall measurement time: " +str(duration / 1000) + " seconds")
import urllib.request
import json
import random
from threading import Thread
import time
import sys
from phue import Bridge

#webbrowser.open_new('https://discovery.meethue.com/')
with urllib.request.urlopen("https://discovery.meethue.com/") as url:
    data = json.loads(url.read().decode())

ipaddress = (data[0]['internalipaddress'])
userName = 'avzYjdyKIm0k9y10ZHBLH11161PZGz7QqFYNxsUF'


#method to strobe a light on or off, should be added to a thread unless you want the application to lock here

def strobeLight(lightId, frequencyMS=50):
    # TODO fix this bug with internal time state monitoring
    # the maximum strobe is at 50 for right now because the rest api sometimes takes a second to respond leavingadad
    # one light in one frozen state
    if frequencyMS < 50:
        frequencyMS = 50
    lightsState = True
    while True:
        if lightsState:
            onOrOff = 255
        else:
            onOrOff = 0

        b.set_light(lightId, 'bri', onOrOff, 0)
        time.sleep(frequencyMS / 1000.0)
        lightsState = not lightsState



#abstract method to change a property by a certain value after its been given an initial value
def changeLightHueAsync(lightId, changeValue, minValue, maxValue, property, numberOfChanges=1,
                        transTimeMs=300, varyChangeValue=False):
    if isinstance(lightId, list):
        propertyValue = b.get_light(lightId[0], property)
    else:
        propertyValue = b.get_light(lightId, property)
    counter = 0
    currentTime = lastTime = int(round(time.time() * 1000))
    while True:
        if varyChangeValue:
            changeAmount = random.randint(-random.randint(0, changeValue), random.randint(0, changeValue))
        else:
            changeAmount = random.randint(-changeValue, changeValue)
        propertyValue += changeAmount

        #instead of clamping just know if we should have went up or down
        if propertyValue < minValue or propertyValue > maxValue:
            propertyValue -= (2*changeAmount)

        # allow both lights to change at the same time
        b.set_light(lightId, property, propertyValue)
        if counter > numberOfChanges:
            break
        counter += 1
        '''
        if property == 'hue':
            currentTime = int(round(time.time()*1000))
            print(currentTime-lastTime)
            lastTime = currentTime
        '''
        time.sleep(transTimeMs/1000.0)
print(sys.executable)
b = Bridge(ipaddress, userName)
b.connect()
b.set_light([1, 2], 'on', True)

brightness = 50

#Spawn threads to change the hues on the two lights so they dont ping pong changing and have them execute in parallel
thread1Hue = Thread(target=changeLightHueAsync, args=(1, 5000, 0, 64000, 'hue', 1000000, 50, ))
thread1Sat = Thread(target=changeLightHueAsync, args=(1, 25, 0, 255, 'sat', 1000000, 200, ))
thread1Bright = Thread(target=changeLightHueAsync, args=(1, 20, 20, brightness, 'bri', 1000000, 50, ))

thread2Hue = Thread(target=changeLightHueAsync, args=(2, 5000, 0, 64000, 'hue', 1000000, 50, ))
thread2Sat = Thread(target=changeLightHueAsync, args=(2, 25, 0, 255, 'sat', 1000000, 200, ))
thread2Bright = Thread(target=changeLightHueAsync, args=(2, 20, 20, brightness, 'bri', 1000000, 50, ))

threadStrobeLights = Thread(target=strobeLight, args=([1,2], 50))

thread1Hue.start()
thread1Sat.start()
thread1Bright.start()
#threadStrobeLights.start()

thread2Hue.start()
thread2Sat.start()
thread2Bright.start()

thread1Hue.join()
thread1Sat.join()
thread1Bright.join()
#threadStrobeLights.join()

thread2Hue.join()
thread2Sat.join()
thread2Bright.join()

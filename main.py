from machine import Pin
import json
from mqtt_as import MQTTClient, config
import uasyncio as asyncio
from primitives.switch import Switch
from time import ticks_diff, ticks_us
from settings import SERVIDOR, SSID, PASS

config['server'] = SERVIDOR
config['ssid'] = SSID
config['wifi_pw'] = PASS
# config['connect_coro'] = conn_han
# config['wifi_coro'] = wifi_han
config['ssl'] = True

# Set up client
MQTTClient.DEBUG = False  # Optional
client = MQTTClient(config)

tstart = 0.000000000001
delta = 0
contador = 0

# Callback on debounced switch closure
def timeit():
    global tstart, delta, contador
    contador += 1
    delta += ticks_diff(ticks_us(), tstart)
    tstart = ticks_us()

async def main(client):
    await client.connect()
    n = 0
    await asyncio.sleep(2)  # Give broker time
    global delta, contador
    while True:
        if contador > 0:
            # apply scaling
            velocidad=1000000*contador/delta
            delta = 0
            contador = 0
            print(velocidad)  # To test, just print ms
            datos=json.dumps(
                        ('velocidad',velocidad)
                    )
            await client.publish("meteorologica/", datos, qos = 1)
        await asyncio.sleep(5)  # Report once per second

sensor = Pin(22, Pin.IN)  # Hardware: assumes switch to gnd
sw = Switch(sensor)
sw.close_func(timeit)  # Associate callback with switch contact closure

try:
    asyncio.run(main(client))
finally:
    client.close()
    asyncio.new_event_loop()

from machine import Pin, Timer
from time import ticks_us, ticks_diff
import uasyncio as asyncio
import json
from mqtt_as import MQTTClient, config
from settings import SERVIDOR, SSID, WIFI_PASS, MQTT_USR, MQTT_USR_PASS

config['server'] = SERVIDOR
config['ssid'] = SSID
config['wifi_pw'] = WIFI_PASS
# config['connect_coro'] = conn_han
# config['wifi_coro'] = wifi_han
config['ssl'] = True
config['user'] = MQTT_USR
config['password'] = MQTT_USR_PASS

# Set up client
MQTTClient.DEBUG = False  # Optional
client = MQTTClient(config)

class AsyncPin:
    contador = 0
    tstart = ticks_us()
    delta = 0

    def __init__(self, pin, trigger):
        self.pin = pin
        self.flag = asyncio.ThreadSafeFlag()
        self.pin.irq(handler=lambda pin: self.flag.set(), trigger=trigger)

    async def wait_edge(self):
        await self.flag.wait()
        diferencia = ticks_diff(ticks_us(), self.tstart)
        if diferencia > 100 or self.contador == 0:
            # print('Got edge.')
            self.delta += diferencia
            self.tstart = ticks_us()
            self.contador += 1

pin_in = Pin(22, Pin.IN, Pin.PULL_DOWN)
async_pin = AsyncPin(pin_in, Pin.IRQ_RISING)

async def foo():
    while True:
        await async_pin.wait_edge()

async def main(client):
    await client.connect()
    n = 0
    await asyncio.sleep(2)  # Give broker time
    asyncio.create_task(foo())
    while True:
        await asyncio.sleep(2)
        if async_pin.contador > 1:
            velocidad = round(1000000*(async_pin.contador)/async_pin.delta,1)
        else:
            velocidad = None
        print(velocidad)
        datos=json.dumps(
                    ('velocidad',velocidad)
                )
        await client.publish("meteorologica/", datos, qos = 1)
        async_pin.delta = 0
        async_pin.contador = 0

try:
    asyncio.run(main(client))
finally:
    client.close()
    asyncio.new_event_loop()
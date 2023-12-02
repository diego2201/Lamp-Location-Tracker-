import aioble
import bluetooth
import machine
import uasyncio as asyncio

_REMOTE_UUID = bluetooth.UUID(0x1848)
_GENERIC = bluetooth.UUID(0x1800)
_REMOTE_CHARACTERISTICS_UUID = bluetooth.UUID(0x2A6E)

led = machine.Pin("LED", machine.Pin.OUT)
connected = False
alive = False

async def find_remote():
    async with aioble.scan(5000, interval_us=30000, window_us=30000, active=True) as scanner:
        async for result in scanner:
            if result.name() == "BasePi2":
                print("Found BasePi2")
                for item in result.services():
                    print(item)
                if _GENERIC in result.services():
                    print("Found Robot Remote Service")
                    return result.device
    return None

async def blink_task():
    """ Blink the LED on and off every second """
    print('blink task started')
    toggle = True
    while True and alive:
        blink = 250
        led.value(toggle)
        toggle = not toggle
        if connected:
            blink = 1000
        else:
            blink = 250
        await asyncio.sleep_ms(blink)
    print('blink task stopped')

async def peripheral_task():
    print ("peripheral task started")
    global connected, alive 
    connected = False
    device = await find_remote()
    if not device:
        print("No remote found")
        return
    try:
        print("connecting to", device)
        connection = await device.connect()
    
    except asyncio.TimeoutError:
        print("Timeout during connection")
        return

    async with connection:
        print("connected")
        alive = True
        connected = True

        robot_service = await connection.service(_REMOTE_UUID)
        control_characteristic = await robot_service.characteristic(_REMOTE_CHARACTERISTICS_UUID)

        while True:
            try:
                if robot_service == None:
                    print("remote disconnected")
                    alive = False
                    break
            
            except asyncio.TimeoutError:
                print("Timeout during discovery / service / characteristic")
                alive = False
                break

            if control_characteristic == None:
                print("no control")
                alive = False
                break
                 
            try:
                data = await control_characteristic.read(timeout_ms=1000)

                await control_characteristic.subscribe(notify=True)
                while True:
                    command = await control_characteristic.notified()

            except Exception as e:
                print(f"something went wrong: {e}")
                connected = False
                alive = False
                break
            
        await connection.disconnected()
        print("disconnected")
        alive = False

async def main():
    tasks = []
    tasks = [
        asyncio.create_task(blink_task()),
        asyncio.create_task(peripheral_task()),
    ]
    await asyncio.gather(*tasks)

while True:
    asyncio.run(main())
                
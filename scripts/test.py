import serial
import sys
import time
arduino = serial.Serial(port='/dev/serial/by-id/usb-Arduino__www.arduino.cc__0043_7583033343935150A092-if00', 
                        baudrate=115200,
                        timeout=0,
                        )
print(arduino.name)
i = 0
while i < 10:
    time.sleep(2.0)
    arduino.write('hello'.encode('utf-8'))
    i += 1
arduino.close()
# def write_read(x):
#     arduino.write(bytes(x, 'utf-8'))
#     time.sleep(0.5)
#     data = arduino.readline()
#     return data
# # x, y = -1, 2
# # print(f'{x}')
# # print(arduino.write(bytes(f'{x}', 'utf-8')))
# # data = arduino.readline()
# # print(data)
# i = 0
# while True:
#     # arduino.flush()

#     d = write_read(f'{i}')
#     print(d)
#     i += 1
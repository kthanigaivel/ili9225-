from display import *
from machine import Pin, SPI
MSPI=SPI(0,baudrate=46000000,firstbit=SPI.MSB,bits=8,sck=Pin(2),mosi=Pin(3),miso=Pin(4))

dis=Display(cs=Pin(5,Pin.OUT),rst=Pin(6,Pin.OUT),rs=Pin(7,Pin.OUT),  spi=MSPI)
dis.begin()
  

dis.set_window()
fbuf=dis.framebuffer()
fbuf.fill(0xff00)
fbuf.text('Thanigaivel is Awesome!', 10, 10, 0x00f0)
fbuf.fill_rect(10,30,50,90,0x2f30)
fbuf.hline(0, 90, 96, 0xffff)
dis.data(fbuf)
time.sleep(2)
dis.reset_window()
dis.photo('peacock.pbm',0,0)




    


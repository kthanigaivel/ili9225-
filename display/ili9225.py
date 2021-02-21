import time,framebuf
from micropython import const
from machine import SPI,Pin

_TFTWIDTH                = const(176)
_TFTHEIGHT               = const(220)
_DRIVER_OUTPUT_CTRL      = const(0x01)
_LCD_AC_DRIVING_CTRL     = const(0x02)
_ENTRY_MODE              = const(0x03)
_DISP_CTRL1              = const(0x07)
_BLANK_PERIOD_CTRL1      = const(0x08)
_FRAME_CYCLE_CTRL        = const(0x0B)
_INTERFACE_CTRL          = const(0x0C)
_OSC_CTRL                = const(0x0F)
_POWER_CTRL1             = const(0x10)
_POWER_CTRL2             = const(0x11)
_POWER_CTRL3             = const(0x12)
_POWER_CTRL4             = const(0x13)
_POWER_CTRL5             = const(0x14)
_VCI_RECYCLING           = const(0x15)
_RAM_ADDR_SET1           = const(0x20)
_RAM_ADDR_SET2           = const(0x21)
_GRAM_DATA_REG           = const(0x22)
_GATE_SCAN_CTRL          = const(0x30)
_VERTICAL_SCROLL_CTRL1   = const(0x31)
_VERTICAL_SCROLL_CTRL2   = const(0x32)
_VERTICAL_SCROLL_CTRL3   = const(0x33)
_PARTIAL_DRIVING_POS1    = const(0x34)
_PARTIAL_DRIVING_POS2    = const(0x35)
_HORIZONTAL_WINDOW_ADDR1 = const(0x36)
_HORIZONTAL_WINDOW_ADDR2 = const(0x37)
_VERTICAL_WINDOW_ADDR1   = const(0x38)
_VERTICAL_WINDOW_ADDR2   = const(0x39)
_GAMMA_CTRL1             = const(0x50)
_GAMMA_CTRL2             = const(0x51)
_GAMMA_CTRL3             = const(0x52)
_GAMMA_CTRL4             = const(0x53)
_GAMMA_CTRL5             = const(0x54)
_GAMMA_CTRL6             = const(0x55)
_GAMMA_CTRL7             = const(0x56)
_GAMMA_CTRL8             = const(0x57)
_GAMMA_CTRL9             = const(0x58)
_GAMMA_CTRL10            = const(0x59)
C_INVOFF                 = const(0x20)
C_INVON                  = const(0x21)

def color565(r, g, b):
    return ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)

class Display(object):

    def __init__(self,  cs, rs, rst, spi, width=_TFTWIDTH, height=_TFTHEIGHT):
        self._cs= cs
        self._rs = rs
        self._rst = rst
        self._spi = spi
        self.width = width
        self.height = height
        self._cs(0)
    
        self.fbuf=framebuf.FrameBuffer(bytearray(self.width * self.height * 2), self.width, self.height, framebuf.RGB565)
        
    def send(self, data, is_data=True, chunk_size=4096):
        self._rs(is_data)
        if isinstance(data, int):
            data = [data & 0xFF]
        if isinstance(data,framebuf.FrameBuffer):
            self._spi.write(data)
        if isinstance(data,list):
            for start in range(0, len(data), chunk_size):
                end = min(start+chunk_size, len(data))
                self._spi.write(bytes(data[start:end]))
        return self

    def command(self, data):
        return self.send(data, False)

    def data(self, data):
        return self.send(data, True)

    def reset(self):
        if self._rst is not None:
            self._rst(1) #self._gpio.set_high(self._rst)
            time.sleep(0.005)
            self._rst(0) #self._gpio.set_low(self._rst)
            time.sleep(0.02)
            self._rst(1) #self._gpio.set_high(self._rst)
            time.sleep(0.150)

    def _init(self):
        self.command(_POWER_CTRL1).data([0x00, 0x00]); # set SAP,DSTB,STB
        self.command(_POWER_CTRL2).data([0x00, 0x00]); # set APON,PON,AON,VCI1EN,VC
        self.command(_POWER_CTRL3).data([0x00, 0x00]); # set BT,DC1,DC2,DC3
        self.command(_POWER_CTRL4).data([0x00, 0x00]); # set GVDD
        self.command(_POWER_CTRL5).data([0x00, 0x00]); # set VCOMH/VCOML voltage
        time.sleep(0.04);
        self.command(_POWER_CTRL2).data([0x00, 0x18]); # set APON, PON, AON, VCI1EN, VC
        self.command(_POWER_CTRL3).data([0x61, 0x21]); # set BT, DC1, DC2, DC3
        self.command(_POWER_CTRL4).data([0x00, 0x6F]); # set GVDD   /*007F 0088 */
        self.command(_POWER_CTRL5).data([0x49, 0x5F]); # set VCOMH/VCOML voltage
        self.command(_POWER_CTRL1).data([0x08, 0x00]); # set SAP, DSTB, STB
        time.sleep(0.01);
        self.command(_POWER_CTRL2).data([0x10, 0x3B]); # set APON, PON, AON, VCI1EN, VC
        time.sleep(0.05);
        self.command(_DRIVER_OUTPUT_CTRL).data([0x01, 0x1C]);  # set the display line number and display direction
        self.command(_LCD_AC_DRIVING_CTRL).data([0x01, 0x00]); # set 1 line inversion
        self.command(_ENTRY_MODE).data([0x10, 0x30]);          # set GRAM write direction and BGR=1.
        self.command(_DISP_CTRL1).data([0x00, 0x00]);          # Display off
        self.command(_BLANK_PERIOD_CTRL1).data([0x08, 0x08]); # set the back porch and front porch
        self.command(_FRAME_CYCLE_CTRL).data([0x11, 0x00]);    # set the clocks number per line
        self.command(_INTERFACE_CTRL).data([0x00, 0x00]);      # CPU interface
        self.command(_OSC_CTRL).data([0x0D, 0x01]);            # set Osc  /*0e01*/
        self.command(_VCI_RECYCLING).data([0x00, 0x20]);       # set VCI recycling
        self.command(_RAM_ADDR_SET1).data([0x00, 0x00]);       # RAM Address
        self.command(_RAM_ADDR_SET2).data([0x00, 0x00]);       # RAM Address
        self.command(_GATE_SCAN_CTRL).data([0x00, 0x00]);
        self.command(_VERTICAL_SCROLL_CTRL1).data([0x00, 0xDB]);
        self.command(_VERTICAL_SCROLL_CTRL2).data([0x00, 0x00]);
        self.command(_VERTICAL_SCROLL_CTRL3).data([0x00, 0x00]);
        self.command(_PARTIAL_DRIVING_POS1).data([0x00, 0xDB]);
        self.command(_PARTIAL_DRIVING_POS2).data([0x00, 0x00]);
        self.command(_HORIZONTAL_WINDOW_ADDR1).data([0x00, 0xAF]);
        self.command(_HORIZONTAL_WINDOW_ADDR2).data([0x00, 0x00]);
        self.command(_VERTICAL_WINDOW_ADDR1).data([0x00, 0xDB]);
        self.command(_VERTICAL_WINDOW_ADDR2).data([0x00, 0x00]);
        self.command(_GAMMA_CTRL1).data([0x00, 0x00]);
        self.command(_GAMMA_CTRL2).data([0x08, 0x08]);
        self.command(_GAMMA_CTRL3).data([0x08, 0x0A]);
        self.command(_GAMMA_CTRL4).data([0x00, 0x0A]);
        self.command(_GAMMA_CTRL5).data([0x0A, 0x08]);
        self.command(_GAMMA_CTRL6).data([0x08, 0x08]);
        self.command(_GAMMA_CTRL7).data([0x00, 0x00]);
        self.command(_GAMMA_CTRL8).data([0x0A, 0x00]);
        self.command(_GAMMA_CTRL9).data([0x07, 0x10]);
        self.command(_GAMMA_CTRL10).data([0x07, 0x10]);
        self.command(_DISP_CTRL1).data([0x00, 0x12]);
        time.sleep(0.05);
        self.command(_DISP_CTRL1).data([0x10, 0x17]);

    def begin(self):
        self.reset()
        self._init()
        self.set_window();
        self.clear();
        self.reset_window(); 

    def set_window(self, x0=0, y0=0, x1=None, y1=None):
        if x1 is None:
            x1 = self.width-1
        if y1 is None:
            y1 = self.height-1
        self.command(_HORIZONTAL_WINDOW_ADDR1).data(x1);
        self.command(_HORIZONTAL_WINDOW_ADDR2).data(x0);
        self.command(_VERTICAL_WINDOW_ADDR1).data(y1);
        self.command(_VERTICAL_WINDOW_ADDR2).data(y0);
        self.command(_RAM_ADDR_SET1).data(x0);
        self.command(_RAM_ADDR_SET2).data(y0);
        self.command([0x00,0x22]);
        
    def reset_window(self):
        self.command(_HORIZONTAL_WINDOW_ADDR1).data([0x00,0xaf]);
        self.command(_HORIZONTAL_WINDOW_ADDR2).data([0x00,0x00]);
        self.command(_VERTICAL_WINDOW_ADDR1).data([0x00,0xdb]);
        self.command(_VERTICAL_WINDOW_ADDR2).data([0x00,0x00]);
    def framebuffer(self):     
        return framebuf.FrameBuffer(bytearray(self.width * self.height * 2), self.width, self.height, framebuf.RGB565)
 
    def clear(self): 
        #color565(blue red green ( 0 - 255))
        color= color565(0,255,0)
        self.fbuf.fill(color)
        self.data(self.fbuf)
        
    def photo(self,file,x,y):
        self.x=x
        self.y=y
        self.set_window()
        with open(file, 'rb') as f:
            f.readline() # Magic number
            f.readline() # Creator comment
            x=str(f.readline(),'utf-8') # Dimensions
            li=list(x.split(" "))
            self.fbuf.fill(0xffff)
            self.data(self.fbuf)    
            fbuf1 = framebuf.FrameBuffer(bytearray(f.read()), int(li[0]), int(li[1]), framebuf.MONO_HLSB)
            self.fbuf.blit(fbuf1,self.x,self.y,0)
            self.data(self.fbuf)
        self.reset_window()
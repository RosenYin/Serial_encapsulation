#!/usr/bin/env python3
# codeing =utf-8

# 需要serial , binascii包
# pip3 install pyserial

import binascii
import serial
import serial.tools.list_ports
import threading

from bs4 import UnicodeDammit

class C_SerialEncapsulation():
    # 构造函数
    def __init__(self) -> None:
        self.serial_port = serial.Serial()
        self.lock = threading.Lock()  # 初始化线程锁
    # 串口数据配置
    def PortParamConfig(self, port_name=None, json_data:dict={}):
        '''
        在使用 serial.Serial() 创建串口实例时，可以传入的参数很多，常用的参数如下（默认值放在开头：后面第一个）：

        port - 串口设备名或 None。
        baudrate - 波特率，可以是9600，50, 75, 110, 134, 150, 200, 300, 600, 1200, 1800, 2400, 4800, 9600, 19200, 38400, 57600, 115200, 230400, 460800, 500000, 576000, 921600, 1000000, 1152000, 1500000, 2000000, 2500000, 3000000, 3500000, 4000000。
        bytesize - 数据位，可取值为：EIGHTBITS，FIVEBITS, SIXBITS, SEVENBITS, EIGHTBITS。
        parity - 校验位，可取值为：PARITY_NONE, PARITY_EVEN, PARITY_ODD, PARITY_MARK, PARITY_SPACE。
        stopbits - 停止位，可取值为：STOPBITS_ONE, STOPBITS_ONE_POINT_FIVE, STOPBITS_TOW。
        xonxoff - 软件流控，可取值为： False，True。
        rtscts - 硬件（RTS/CTS）流控，可取值为： False，True。
        dsr/dtr - 硬件（DSR/DTR）流控，可取值为：False，True。
        timeout - 读超时时间，可取值为： None, 0 或者其他具体数值（支持小数）。当设置为 None 时，表示阻塞式读取，一直读到期望的所有数据才返回；当设置为 0 时，表示非阻塞式读取，无论读取到多少数据都立即返回；当设置为其他数值时，表示设置具体的超时时间（以秒为单位），如果在该时间内没有读取到所有数据，则直接返回。
        write_timeout - 写超时时间，可取值为： None, 0 或者其他具体数值（支持小数）。参数值起到的效果参考 timeout 参数。
        '''
        with self.lock:  # 加锁
            # 串口名，默认'/dev/ttyUSB0'
            if(port_name is None):
                if('portName' in json_data.keys()):
                    self.serial_port.port=f'{json_data["portName"]}'
                else: self.serial_port.port = '/dev/ttyUSB0'
            else: self.serial_port.port = port_name
            if((port_name[:8] != '/dev/tty')):
                raise("串口名不正确，应为'/dev/tty*'!!")
            # 波特率，默认9600
            if('baudRate' in json_data.keys()):
                self.serial_port.baudrate=json_data["baudRate"]
            else: self.serial_port.baudrate = 9600
            # 数据位长度，默认8
            if('bytesize' in json_data.keys()):
                self.serial_port.bytesize=json_data["bytesize"]
            else: self.serial_port.bytesize = 8
            # 停止位，默认1
            if('stopbits' in json_data.keys()):
                self.serial_port.stopbits=json_data["stopbits"]
            else: self.serial_port.stopbits = 1
            # 奇偶校验位，默认 "N"
            if('parity' in json_data.keys()):
                self.serial_port.parity=json_data["parity"]
            else: self.serial_port.parity = "N"#奇偶校验位
            # 超时设置，默认 0.05 ，在调用readall、read_line等函数时需要,否则会卡死
            if('timeout' in json_data.keys()):
                self.serial_port.timeout=json_data["timeout"]
            else: self.serial_port.timeout = 0.05
            # 返回串口类型
            return self.serial_port
        
    # 打开端口
    def PortOpen(self):
        '''
        打开端口
        '''
        with self.lock:  # 加锁
            if not self.serial_port.is_open:
                self.serial_port.open()
            if(self.serial_port.isOpen()):
                # print("串口打开成功！")
                return True
            else:
                # print("串口打开失败！")
                return False
    # 关闭端口
    def PortClose(self):
        '''
        关闭端口
        '''
        with self.lock:  # 加锁
            if self.serial_port.is_open:
                self.serial_port.close()  # 关闭串口
            if(self.serial_port.isOpen()):
                # print("串口关闭失败！")
                return False
            else:
                # print("串口关闭成功！")
                return True
    def ByteConvertToInt(self, byte_:bytes):
        temp = binascii.b2a_hex(byte_)
        temp = temp.decode(encoding='utf-8')
        return int(temp, 16)
    # 以下为串口读取数据
    # 关于 read() 方法，需要了解如下几点：
    # ① read() 方法默认一次读取一个字节，可以通过传入参数指定每次读取的字节数。
    # ② read() 方法会将读取的内容作为返回值，类型为 bytes。
    # ③ 在打开串口时，可以为 read() 方法配置超时时间。
    def PortReadContinuousData(self, auto_open:bool=True, data_len:int=None):
        '''
        从串口按字节连续读取数据，并返回数据列表，列表中的元素类型为int
        使用于每个接收数据是UTF-8编码
        '''
        with self.lock:  # 加锁
            if(auto_open):
                self.PortParamConfig()
                self.PortOpen()
            # print(serial_port.is_open)
            rxdata = []
            if(data_len is None):
                while True:
                    try:
                        if(self.serial_port.isOpen()):
                            # 按字节读取数据，必须UTF-8编码，b'\x口口'
                            rxbuff = self.serial_port.read()
                            # 将接收到的二进制字节数据转化为十六进制表示形式
                            rxbuff = binascii.b2a_hex(rxbuff)
                            # 将字节 解码为 字符串，因为int函数只允许字符串类型
                            rxbuff= rxbuff.decode(encoding='utf-8')
                            # print('%#x'%rxbuff)
                            if(rxbuff):
                                if(rxbuff is not None):
                                    # 字符串转化为int数据
                                    rxbuff = int(rxbuff, 16)
                                    # print(rxbuff)
                                    # print('int:%#x'%rxbuff)
                                rxdata.append(rxbuff)
                                # print(rxbuff)
                                continue
                            else:
                                # print("接收数据完毕！")
                                break
                        else:
                            # print("串口未打开，无法读取")
                            break
                    except Exception as e:
                        # print("异常报错：", e)
                        pass
            else:
                while data_len>0:
                    try:
                        if(self.serial_port.isOpen()):
                            # 按字节读取数据，必须UTF-8编码，b'\x口口'
                            rxbuff = self.serial_port.read()
                            # 将接收到的二进制字节数据转化为十六进制表示形式
                            rxbuff = binascii.b2a_hex(rxbuff)
                            # 将字节 解码为 字符串，因为int函数只允许字符串类型
                            rxbuff= rxbuff.decode(encoding='utf-8')
                            data_len = data_len - 1
                            # print('%#x'%rxbuff)
                            if(rxbuff):
                                if(rxbuff is not None):
                                    # 字符串转化为int数据
                                    rxbuff = int(rxbuff, 16)
                                    # print(rxbuff)
                                    # print('int:%#x'%rxbuff)
                                rxdata.append(rxbuff)
                                # print(rxbuff)
                                continue
                            else:
                                # print("接收数据完毕！")
                                break
                        else:
                            # print("串口未打开，无法读取")
                            break
                    except Exception as e:
                        # print("异常报错：", e)
                        pass
            return rxdata
        
    # 调用readall方法一次性读取所有数据,默认超时时间0.05s(自设定的)
    def PortReadAllData(self, auto_open:bool=True):
        '''
        调用readall方法一次性读取所有数据,默认超时时间0.05s(自设定的)
        '''
        with self.lock:  # 加锁
            if(auto_open):
                self.PortParamConfig()
                self.PortOpen()
            if(self.serial_port.is_open):
                try:
                    rxdata = self.serial_port.readall()
                    # print(rxdata)
                    # print('读取到数据')
                    return rxdata
                except:
                    pass
            else:
                # print("串口未打开，无法读取")
                pass
    # 调用read方法，读取指定长度数据，默认长度为1，默认超时时间0.05s(自设定的)
    def PortReadSizeData(self, data_size:int=1, auto_open:bool=True):
        '''
        调用read方法，读取指定长度数据，默认长度为1，默认超时时间0.05s(自设定的)
        '''
        with self.lock:  # 加锁
            if(auto_open):
                self.PortParamConfig()
                self.PortOpen()
            if(self.serial_port.is_open):
                try:
                    rxdata = self.serial_port.read(size=data_size)
                except:
                    print("读取指定大小数据失败")
                    pass
                else:
                    return rxdata
            else:
                # print("串口未打开，无法读取")
                pass
    # 以下为向串口发送消息
    # write() 方法只能发送 bytes 类型的数据，所以需要对字符串进行 encode 编码。
    # write() 方法执行完成后，会将发送的字节数作为返回值。
    def PortSendListData(self, tx_data:list, auto_open:bool=True):
        '''
        端口发送列表类型消息，仅测试了int类型16进制数据作为元素
        '''
        with self.lock:  # 加锁
            if(auto_open):
                self.PortParamConfig()
                self.PortOpen()
            # print(data_bytes)
            if(self.serial_port.isOpen()):
                try:
                    self.serial_port.write(tx_data)
                    # print("发送完成")
                except:
                    # print("发送失败")
                    pass
            else:
                # print("发送失败，串口未打开")
                pass
    # 端口发送字符串类型数据
    def PortSendStrData(self, tx_data:str, format_type:str, auto_open:bool=True):
        '''
        端口发送字符串类型数据
        '''
        with self.lock:  # 加锁
            if(auto_open):
                self.PortParamConfig()
                self.PortOpen()
            # 将字符串转换为字节
            data_bytes = tx_data.encode()

            # 将数据转换为16进制发送
            if(format_type == "hex"):
                data_bytes = bytearray.fromhex(tx_data)
            # print(data_bytes)
            if(self.serial_port.isOpen()):
                try:
                    self.serial_port.write(data_bytes)
                except:
                    # print("发送失败")
                    pass
            else:
                # print("发送失败，串口未打开")
                pass
    # 端口发送Json文件中的数据
    def PortSendJsonData(self, json_data:dict, auto_open:bool=True):
        '''
        端口发送Json文件中的数据
        '''
        with self.lock:  # 加锁
            if(auto_open):
                self.PortParamConfig()
                self.PortOpen()
            # 读取json中字典消息
            if('timeout' in json_data.keys()):
                controlData=json_data["controlData"]
            else: controlData = 'error,"controlData"Key no data'
            if('timeout' in json_data.keys()):
                data_format=json_data["dataFormat"]
            else: data_format = "hex"
            
            # 将字符串转换为字节
            data_bytes = controlData.encode()

            # 将数据转换为16进制发送
            if(data_format == "hex"):
                data_bytes = bytearray.fromhex(controlData)
            # print(data_bytes)
            if(self.serial_port.isOpen()):
                try:
                    self.serial_port.write(data_bytes)
                except:
                    # print("发送失败")
                    pass
            else:
                # print("发送失败，串口未打开")
                pass

    # 打印可用串口列表
    @staticmethod
    def Print_Used_Com():
        """
        打印可用串口列表
        """
        # 串口列表串口号
        port_list_number = []
        # 串口列表名称
        port_list_name = []
        port_list_name.clear()
        port_list_number.clear()

        port_list = list(serial.tools.list_ports.comports())

        if len(port_list) <= 0:
            # print("The Serial port can't find!")
            pass
        else:
            for each_port in port_list:
                port_list_number.append(each_port[0])
                port_list_name.append(each_port[1])

        # print(port_list_number)
        # print(port_list_name)
        return port_list_number

    def find_new_device_port(self):
        # 获取所有可用的串口设备
        available_ports = serial.tools.list_ports.comports()
        # 存储之前已知的设备列表，可用于比较新设备
        previous_devices = set()
        # 迭代所有已知的串口设备
        for port in available_ports:
            previous_devices.add(port.device)
        while True:
            # 重新获取可用的串口设备
            available_ports = serial.tools.list_ports.comports()
            # 存储当前已知的设备列表
            current_devices = set()
            # 比较当前设备与之前的设备列表，找出新插入的设备
            for port in available_ports:
                current_devices.add(port.device)
                if port.device not in previous_devices:
                    # print("New device port:", port.device)
                    return port.device
            # 更新之前已知的设备列表
            previous_devices = current_devices

def Main():
    IO = C_SerialEncapsulation()
    data = {"portName":"/dev/ttyUSB0", "baudRate":9600, "controlData":"", "dataFormat":"hex"}
    IO.PortParamConfig(data)
    # IO.PortOpen()
    IO.PortSendListData([0x03,0x03,0x00,0x00,0x00,0x03,0x04,0x29])
    IO.PortReadContinuousData(data)

    data = "\x0a"
    # print('1',type(data))
    # print(data)
    data = data.encode("utf8")
    print('2',type(data))
    print(data)
    data = binascii.b2a_hex(data)
    print('3',type(data))
    print(data)

    datas = data.decode(encoding='utf-8')
    print('5',type(datas))
    print(datas)
    a = int(datas, 16)
    print('6',type(a))
    print('%#x'%a)
    print(a)
    datas = bytearray.fromhex(datas)
    print('7',type(datas))
    print(datas)

    datas = datas.decode()
    print('8',type(datas))
    print(datas)
    
    datas = datas.encode()
    print('9',type(datas))
    print(datas)

def Test():
    s = b'\xe4\xbd\xa0\xe5\xa5\xbd\xe4\xb8\x96\xe7\x95\x8c'
    # s = s.encode('unicode_escape')
    dammit = UnicodeDammit(s)
    print(dammit.unicode_markup)
    print(dammit.detector.chardet_encoding)
    print(s)
    data = '离离原上草，一岁一枯荣'.encode('utf-8')
    print(data)
    dammit = UnicodeDammit(data)
    print(dammit.unicode_markup)
    print(dammit.detector.chardet_encoding)

if __name__ == '__main__':
    IO = C_SerialEncapsulation()
    IO.Print_Used_Com()

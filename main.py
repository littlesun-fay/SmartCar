import socket                                                           #导入socket通信库
import machine
from machine import Pin
import network


g4 = Pin(1,Pin.OUT)
g5 = Pin(2,Pin.OUT)
g12 = Pin(3,Pin.OUT)
g13 = Pin(4,Pin.OUT)

 """小车控制部分"""
def Go():                                                               #控制前进函数
    g4.value(1)
    g5.value(0)
    g12.value(1)
    g13.value(0)

def Back():                                                             #后退函数
    g4.value(0)
    g5.value(1)
    g12.value(0)
    g13.value(1)


def Left():                                                             #左转函数
    g4.value(1)
    g5.value(0)
    g12.value(0)
    g13.value(0)

def Right():                                                            #右转函数
    g4.value(0)
    g5.value(0)
    g12.value(1)
    g13.value(0)

def Stop():                                                             #停车函数
    g4.value(0)
    g5.value(0)
    g12.value(0)
    g13.value(0)

"""网络连接部分"""
sta_if = network.WLAN(network.STA_IF)
p2 = Pin(2, Pin.OUT)
sta_if.active(False)
if not sta_if.isconnected():
        p2.value(0)
        print('connecting to network...')                               #开始连接
        sta_if.active(True)
        sta_if.connect('小太阳', '15527290613')                         #连接到手机WiFi
        while not sta_if.isconnected(): 
                pass
if sta_if.isconnected():
        print('connect success')                                        #如连接成功提示
        p2.value(1)
        print('network config:', sta_if.ifconfig())                     #打印IP地址数组

"""socket通信部分"""
addr = sta_if.ifconfig()[0]                                             #使用网络连接的IP数组中第一个IP
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)   
s.bind((sta_if.ifconfig()[0], 80))                                      #绑定IP地址，端口号为80
s.listen(5)                                                             #设置允许连接的客户端数量
print('listening on:', addr)
while True:
    cl, addr = s.accept()                                               #接受客户端的连接请求，cl为此链接创建的一个新的scoket对象，addr客户端地址
    print('client connected from:', addr)
    cl_file = cl.makefile('rwb', 0)                                     #返回与socket对象关联的文件对象。rwb:支持二进制模式的读写操作 0:默认值，不支持缓存
    req = b''
    while True: 
        line = cl_file.readline()                                       #读取发送过来的数据，直到\r\n换行结束
        if not line or line == b'\r\n':
            break
        req += line
    print("Request:")
    req=req.decode('utf-8').split('\r\n')                               #解码
    req_data=req[0].lstrip().rstrip().replace(' ','').lower()
    print(req_data)
    if req_data.find('favicon.ico')>-1:
        cl.close()
        continue
    else:
        req_data=req_data.replace('get/?','').replace('http/1.1','')
        index = req_data.find('key=')                                   #查找key标签
        value = req_data[index+4:index+6].lstrip().rstrip()
        print('key:',value)
        if value == 'go':
            Go()
        elif value == 'ba':
            Back()
        elif value == 'le':
            Left()
        elif value == 'ri':
            Right()
        else:
            Stop()
    with open("control.html", 'r') as f:
        for line in f:
            cl.send(line)
                                                                        #返回html网页的数据
    cl.close()                                                          #关闭socket

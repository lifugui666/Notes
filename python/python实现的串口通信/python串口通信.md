# python实现串口通信





使python实现串口通信

## 1

安装serial包

```shell
pip install serial
pip install pyserial ##这是使用serial.tools所必须安装的
```



## 2

查看当前设备下有多少串口

```python
import serial
import serial.tools.list_ports

'''
使用该脚本测试是否能获取到串口
'''

ports = serial.tools.list_ports.comports()
for port in ports:
    print(port.hwid)
```



 

## 3设置参数 收发数据

```python 
import serial
 
# 打开串口
ser = serial.Serial('COM46', 9600, timeout=1)  # 'COM1'是你的串口号，9600是波特率，timeout是超时时间（单位为秒）
# 向串口发送数据
ser.write(b's')
# 从串口接收数据
received_data = ser.readline()
print("Received data: ", received_data)
# 关闭串口
ser.close()
```


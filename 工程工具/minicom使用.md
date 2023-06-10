## 安装minicom

```


# 首先安装minicom
sudo apt-get install minicom

# 第一次使用minicom需要进行一些配置
sudo minicom -s


            +------[设置]---------+
            | 文件名和路径            |
            | 文件传输协定            |
            | 串口设置              |
            | 调制解调器和拨接          |
            | 屏幕和键盘             |
            | 保存设置为 dfl         |
            | 另存设置为…            |
            | 离开本画面             |
            | 离开 Minicom        |
            +-------------------+

# 选择串口设置

    +-----------------------------------------------------------------------+
    | A - 串行设备               : /dev/modem                                   |
    | B - 锁文件位置              : /var/lock                                    |
    | C - 拨入程序               :                                              |
    | D - 拨出程序               :                                              |
    | E - Bps/Par/Bits       : 115200 8N1                                   |
    | F - 硬件流控制              : 是                                            |
    | G - 软件流控制              : 否                                            |
    | H -     RS485 Enable      : No                                        |
    | I -   RS485 Rts On Send   : No                                        |
    | J -  RS485 Rts After Send : No                                        |
    | K -  RS485 Rx During Tx   : No                                        |
    | L -  RS485 Terminate Bus  : No                                        |
    | M - RS485 Delay Rts Before: 0                                         |
    | N - RS485 Delay Rts After : 0                                         |
    |                                                                       |
    |    变更设置？                                                              |
    +-----------------------------------------------------------------------+

# 输入A就可以修改串口

```



## 查找usb转串口设备

在修改串口之前必须要知道串口设备的路径....

1. 使用lsusb查看是否有串口设备：

   ```shell
   lee@lee-ThinkPad-A485:~/Documents/Notes$ lsusb
   Bus 005 Device 001: ID 1d6b:0003 Linux Foundation 3.0 root hub
   Bus 004 Device 006: ID 04f2:b604 Chicony Electronics Co., Ltd Integrated Camera (1280x720@30)
   Bus 004 Device 007: ID 0bda:b023 Realtek Semiconductor Corp. RTL8822BE Bluetooth 4.2 Adapter
   Bus 004 Device 003: ID 05e3:0610 Genesys Logic, Inc. Hub
   Bus 004 Device 004: ID 06cb:009a Synaptics, Inc. Metallica MIS Touch Fingerprint Reader
   Bus 004 Device 002: ID 05e3:0610 Genesys Logic, Inc. Hub
   Bus 004 Device 001: ID 1d6b:0002 Linux Foundation 2.0 root hub
   Bus 003 Device 001: ID 1d6b:0003 Linux Foundation 3.0 root hub
   Bus 002 Device 002: ID 24ae:1813 Shenzhen Rapoo Technology Co., Ltd. E9260 Wireless Multi-mode Keyboard
   ***Bus 002 Device 008: ID 1a86:7523 QinHeng Electronics CH340 serial converter
   Bus 002 Device 001: ID 1d6b:0002 Linux Foundation 2.0 root hub
   Bus 001 Device 001: ID 1d6b:0002 Linux Foundation 2.0 root hub
   ### 很明显，在我标注***的地方显示，当前有一个设备是serial converter
   ### 这最起码意味着我的电脑上确实有一个usb转串口的设备
   ### 如果这里都没有，那说明你或许应该去安装一下驱动了....
   ```

2. 查看系统日志，一般USB转串口设备会以ttyUSBx命名

   ```shell
   lee@lee-ThinkPad-A485:~/Documents/Notes$ sudo dmesg |grep ttyUSB
   [65241.135832] usb 2-2: ch341-uart converter now attached to ttyUSB0
   [65241.685881] ch341-uart ttyUSB0: ch341-uart converter now disconnected from ttyUSB0
   ```

   从系统日志可以看到，ttyUSB0不晓得由于什么原因连接上之后又断开了，可谓是狗屎

   ....继续分析一下，从系统日志可以看出这个usb转串口是ch341芯片，在系统日志里查找一下ch341相关的信息

   ```shell
   [65241.122676] usbcore: registered new interface driver ch341
   [65241.122698] usbserial: USB Serial support registered for ch341-uart
   [65241.122735] ch341 2-2:1.0: ch341-uart converter detected
   [65241.135832] usb 2-2: ch341-uart converter now attached to ttyUSB0
   [65241.682650] usb 2-2: usbfs: interface 0 claimed by ch341 while 'brltty' sets config #1
   ### 有一个叫做brltty的玩意和ch341冲突了
   [65241.685881] ch341-uart ttyUSB0: ch341-uart converter now disconnected from ttyUSB0
   [65241.685931] ch341 2-2:1.0: device disconnected
   ```

   很明显有一个叫做brltty的家伙和ch341冲突了

   ```shell
   lee@lee-ThinkPad-A485:~/Documents/Notes$ sudo apt-get remove brltty
   ```

   执行之后重新插拔设备，查看dmesg，就会发现已经ok了

   

## 配置minnicom

```
sudo minicom -s
# 然后选择串口设置->设置串口设备
# 我这里的串口设备就是/dev/ttyUSB0
```


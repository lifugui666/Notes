# linux的图形界面



# 基础关系

众所周知linux其实是不带界面的，大佬们可以用命令行征服这个系统，但是我不是大佬，所以我还是需要图形界面的；

说实话我接触linux长达四五年的时间里，X11 GTK QT GNOME KDE XFACE这些词汇时常出现，但是我却不理解他们到底是什么；这次就尽量对这些东西构建一个大局上的认识；

## linux的图形界面

linux的图形界面并不是linux系统的一部分，图形界面只是一款运行在linux下的普通软件，这一点和windows不同，对于windows来说，界面就是系统的一部分；

unix的图形界面一直以来都是以MIT的X window system为标准的，



## X协议，X11，X11R6

X协议是一个协议，这个协议使用了C\S架构，即Xserver和Xclinet；

X11是X协议的第11个版本，而X11R6的是X11的第六个发行版...

需要注意的是不同版本的X协议是无法相互通信的，就像ipv4不能和ipv6通信一样；



## X server和X client

X server的任务是接受来自键盘，鼠标等设备的输入，将输入传递给X client供X client使用；

X client也可以将自己的需求发送给X server ，X server将会负责图形界面的绘制和显示；最上层的X client提供了一个完整的GUI负责与用户交互；

X协议负责两者之间的通信；



## Xorg，Xfree86

X协议只是协议，协议只是一种规定，而协议如果没有实现只是一纸空文；

Xorg和Xfree是对X协议的实现；现在的linux一般都用Xorg了；

Xorg是一个Xserver；



## Xlib，QT，GTK +和 GNOME KDE

xlib是对x协议的封装，xlib是一个库；从原理上说单独使用xlib就可以开发出xclient；

QT是以xlib为基础的一套工具，你可以理解为QT对xlib又进行了一次封装，相当于直接使用xlib，使用QT可以大幅减轻开发难度，KDE就是基于QT开发的一套桌面环境；

GTK+包含两部分：GTK和GDK；GDK是对Xlib的封装，而GTK则提供了一些控件和对象模型；GNOME是GTK+开发的一套桌面环境；

QT并不是GPL协议，因此有一部分开源用户开发了GTK+；


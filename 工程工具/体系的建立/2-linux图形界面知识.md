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



## Xlib，xcb，QT，GTK +和 GNOME KDE

xlib是对x协议的封装，xlib是一个库；从原理上说单独使用xlib就可以开发出xclient；

xcb也是对X协议的封装，它是xlib的替代品，相对于xlib，xcb的使用难度更低一点；

QT是以xlib为基础的一套工具，你可以理解为QT对xlib又进行了一次封装，相当于直接使用xlib，使用QT可以大幅减轻开发难度，KDE就是基于QT开发的一套桌面环境；

GTK+包含两部分：GTK和GDK；GDK是对Xlib的封装，而GTK则提供了一些控件和对象模型；GNOME是GTK+开发的一套桌面环境；

QT并不是GPL协议，因此有一部分开源用户开发了GTK+；



## QT与GTK之间的战争

在unix界，图形界面的标准一直都是MIT的X window system；但是在商业应用上，早年间有两个派别：一个是当年的巨头sun公司（openlook），一个是现在仍是巨头的IBM公司（motif）；这两者最后胜出的试试IBM的motif，成为了最为普遍的图形界面库；后来sun和IBM又相互妥协，推出了CDE作为一个标准图形界面；当年motif的授权价格非常贵，微软的windows发展也如日中天，linux也在寻找一个不要钱的图形界面标准；

96年，有一个德国人发起了KDE项目；这个项目针对的是CDE的；KDE本身使用GPL协议，但是KDE的底层是QT，QT在当时已经在unix下自由发布了，但是QT并不是GPL协议；因此有一部分人认为KDE并不能算作自由软件；于是这部分人兵分两路，其中一部分决定重写一个库代替QT（harmonny计划），另一部分决定干脆重写一个GNOME（GNU network object environment ）代替KDE；

当年的redhat公司是linux界的老大，它对KDE/QT的版权问题感到担心，因此红帽非常支持GNOME的发展；为了GNOME的发展红帽是出钱出力；

于是KDE和GNOME之间的战争又打响了；KDE由于QT的版权问题被一部分人诟病，并且KDE/QT使用C++，明显开发难度高于使用C语言的GNOME/GTK；但是KDE毕竟是先行者，先发优势很大，KDE的稳定性很高；而GNOME虽然当年的稳定性很差，但是吸引了很多自由软件开发者，GNOME大有赶上KDE的趋势；

在2000年左右，这场战争进入白热化阶段；一批Apple出身的工程师成立了自己的公司为GNOME设计界面；KDE2.0也发布了，这个版本的KDE继承了Koffice，Kdevelop等大量的软件，甚至集成了一个当时足以与微软的IE浏览器相抗衡的网络浏览器Kounqueror；另一边Sun，RedHat等一票公司成立了GNOME基金会，Sun宣布将自己的Star office集成到GNOME里；目前为止GNOME已经从当年稳定性奇差的项目进化到可以与KDE一战的项目了；最终，同年10月，QT的公司Trolltech将QT的自由版本发布为GPL宣言，KDE/QT的版权问题最终得到了解决，同时还发布了嵌入式QT，时至今日（2023年）嵌入式QT仍旧是嵌入式开发中的重要工具；

这场战争在2023的今天仍在继续..不过说实话激烈程度已经没有那么高了；GNOME由于根正苗红的自由软件，谁用都免费，也不存在被收费的可能，因此大公司们为了规避可能存在的风险会倾向于选择GNOME；而KDE的质量和开发效率都比GNOME高，并且在嵌入式领域有绝对的优势，不过QT毕竟只有free edition是GPL协议，如果你在windows或者unix上使用Qt仍旧需要购买；

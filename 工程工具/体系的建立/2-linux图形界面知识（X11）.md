# linux的图形界面



# 常见名词的解释

众所周知linux其实是不带界面的，大佬们可以用命令行征服这个系统，但是我不是大佬，所以我还是需要图形界面的；

说实话我接触linux长达四五年的时间里，X11 GTK QT GNOME KDE XFACE这些词汇时常出现，但是我却不理解他们到底是什么；这次就尽量对这些东西构建一个大局上的认识；

## linux的图形界面

linux的图形界面并不是linux系统的一部分，图形界面只是一款运行在linux下的普通软件，这一点和windows不同，对于windows来说，界面就是系统的一部分；

unix的图形界面一直以来都是以MIT的X window system为标准的，



## X协议，X11，X11R6

X协议是一个协议，这个协议使用了C\S架构，即Xserver和Xclinet；

X11是X协议的第11个版本，而X11R6的是X11的第六个发行版...

需要注意的是不同版本的X协议是无法相互通信的；



## X server和X client

X server的任务是接受来自键盘，鼠标等设备的输入，将输入传递给X client供X client使用；

X client也可以将自己的需求发送给X server ，X server将会负责图形界面的绘制和显示；

最上层的X client提供了一个完整的GUI负责与用户交互；

X协议负责两者之间的通信；



## Xorg，Xfree86

X协议只是协议，协议只是一种规定，而协议如果没有实现只是一纸空文；

Xorg和Xfree是对X协议的实现；现在的linux一般都用Xorg了；

Xorg是一个Xserver；



## Xlib，xcb，QT，GTK +和 GNOME KDE

xlib是对x协议的封装，xlib是一个库；从原理上说单独使用xlib就可以开发出xclient；

xcb也是对X协议的封装，它是xlib的替代品，相对于xlib，xcb的使用难度更低一点；

QT是以xlib为基础的一套工具，你可以理解为QT对xlib又进行了一次封装，相比于直接使用xlib，使用QT可以大幅减轻开发难度，KDE就是基于QT开发的一套桌面环境；

GTK+包含两部分：GTK和GDK；GDK也是对Xlib的封装（GDK的定位与Qt相同），而GTK则提供了一些控件和对象模型；GNOME是GTK+开发的一套桌面环境；

QT并不是GPL协议，这也是kde和gnome大战的起因；



## QT与GTK之间的战争

在unix界，图形界面的标准一直都是MIT的X window system；但是在商业应用上，早年间有两个派别：一个是当年的巨头sun公司（openlook），一个是现在仍是巨头的IBM公司（motif）；这两者最后胜出的是IBM的motif；后来sun和IBM又相互妥协，推出了CDE作为一个标准图形界面；当年motif的授权价格非常贵，微软的windows发展也如日中天，linux也在寻找一个不要钱的图形界面标准；

96年，有一个德国人发起了KDE项目；这个项目针对的是CDE的；KDE本身使用GPL协议，但是KDE的底层是QT，QT在当时已经在unix下自由发布了，但是QT并不是GPL协议；因此有一部分人认为KDE并不能算作自由软件；于是这部分人兵分两路，其中一部分决定重写一个库代替QT（harmonny计划），另一部分决定干脆重写一个GNOME（GNU network object environment ）代替KDE；

当年的redhat公司是linux界的老大，它对KDE/QT的版权问题感到担心，因此红帽非常支持GNOME的发展；为了GNOME的发展红帽出钱出力；

于是KDE和GNOME之间的战争又打响了；KDE由于QT的版权问题被一部分人诟病，并且KDE/QT使用C++，明显开发难度高于使用C语言的GNOME/GTK；但是KDE毕竟是先行者，先发优势很大，KDE的稳定性很高；而GNOME虽然当年的稳定性很差，但是吸引了很多自由软件开发者，GNOME大有赶上KDE的趋势；

在2000年左右，这场战争进入白热化阶段；一批Apple出身的工程师成立了自己的公司为GNOME设计界面；KDE2.0也发布了，这个版本的KDE继承了Koffice，Kdevelop等大量的软件，甚至集成了一个当时足以与微软的IE浏览器相抗衡的网络浏览器Kounqueror；另一边Sun，RedHat等一票公司成立了GNOME基金会，Sun宣布将自己的Star office集成到GNOME里；目前为止GNOME已经从当年稳定性奇差的项目进化到可以与KDE一战的项目了；最终，同年10月，QT的公司Trolltech将QT的自由版本发布为GPL宣言，KDE/QT的版权问题最终得到了解决，同时还发布了嵌入式QT，时至今日（2023年）嵌入式QT仍旧是嵌入式开发中的重要工具；

这场战争在2023的今天仍在继续..不过说实话激烈程度已经没有那么高了；GNOME由于根正苗红的自由软件，谁用都免费，也不存在被收费的可能，因此大公司们为了规避可能存在的风险会倾向于选择GNOME；而KDE的质量和开发效率都比GNOME高，并且在嵌入式领域有绝对的优势，不过QT毕竟只有free edition是GPL协议，如果你在windows或者unix上使用Qt仍旧需要购买；

# X11 programming manual

https://tronche.com/gui/x/xlib/

这里只做简单的翻译的学习

### 第一章：介绍xlib

X windows system是由MIT设计的network-transparent window system；X display server可以运行在一个单色/彩色显示硬件上；server可以将用户的输入分配给位于同一台机器或者网络上其他地方点的各种client，并且接受这些client的输出请求；client和server可以在同一台机器上，也可以在不同的机器上，这点可能会引起我们的困惑，但是这不是重点；

#### 1.1 x window system介绍

本书中的一些词条是X所独有的，其他的通用的词条在其他window system中可能与X中有不同的含义，关于这点请参考词汇表；

X window system支持一个或多个包含重叠的windows或者subwindows的screen；screen是一个物理意义上的监视器，他可以是彩色的，也可以是单色的，灰阶的；每个display或者workstation可以拥有多个screen；一个X server可以为多个screen提供服务；**由一个键盘，一个鼠标，一个或多个screen组成的集合我们称之为"display"；**

在X server中，所有的windows都被安排在严格层级结构中；每个层级结构的顶端是是一个root window，root window可以覆盖一个display中全部的screens；每个root windows都部分地或者完整地被 child window所覆盖；除开root window之外的全部window都有parents；通常情况下每个应用软件都至少有一个window；child window也可以有自己的child window；按照这种方式，一个应用软件可以在任何一个screen上创建任意深度的树形结构；X则为windows提供图形，文字，像素操作；

child window的尺寸是可以比parent大的；也就是说child的一部分或者整个child是可以超过其parents的边界的，但是其输出却由其parent进行裁剪；如果一个window的几个child有相互重叠的部分，其中一个被认为是高（top/raised）于其他的child，那么这个高的child会遮盖其他的child；如果输出到了被其他窗口遮盖的地方，那么这个窗口会被window system所抑制，除非这个窗口本身有backing store；如果窗口被第二个窗口所遮盖，那么第二个窗口仅遮挡第一个窗口和第二个窗口共同的祖先；

一个window可以没有边框，也可以有多个像素宽的边框，这个边框也可以是你喜欢的颜色或者样式；window通常（但不是一定）是有背景的，当window未被覆盖时，这个背景就会被绘制；child会遮盖他们的parents，parent中的图形操作也时常被child所裁切；

每个window和pixmap都有独立的坐标系统；这个坐标系统的原点位于屏幕的左上角，有xy两个轴；坐标是以像素为单位的整数，并且是与像素中心重合的；对于window而言，原点位于左上角内侧的边界内；

X并不保证能够保存windows中的内容；如果一个windows的一部分或者整个windows被隐藏，并且被带回到screen时，windows的内容是可能会丢失的；然后，server会向client发送一个Expose事件以提醒这个窗口一部分或者整个要被重绘；程序必须按照要求准备好window的内容；

X也提供了一个off-screen存储图像对象的方法，叫做pixmap，深度为1的pximap有时候也会被叫做bitmaps；pixmap在多数图形函数中都可以被与window交替使用，并且用于各种图形操作以定义图案或者标题；windows和pixmap被合称为drawables（可绘制对象）；

Xlib中的大多数函数只是向输出buffer中添加请求；这些请求随后会在X server上异步执行；返回 存储在server中的值的 函数 在没有收到明确的答复或者发生错误之前，是不会返回的（阻塞的）；你可以提供一个错误处理handle，当错误发生的时候以供调用；

如果一个client不希望异步执行请求，那么它可以在请求后面调用一下XSync()，这个函数会阻塞，直到所有先前被缓存的异步事件被发送和处理；这有一个比较重要的应用，xlib的输出buffer总是通过调用从服务器返回值挥着等待输入的任何函数来刷新；

xlib中的许多函数会返回一个整数的资源ID，这个ID允许你调用存储在server中的对象；这些对象可以是windw，font，pixmap，colormap，cursor，GContext，这些家伙被定义在<X11/x.h>中；这些资源都是被请求创建的，并且当链接被关闭的时候会被请求所释放（销毁）；这些资源中大多数资源是可以在不同的应用之间被共享的，实际上，windows是被window manager显示的管理的；fonts和cursor天生就被多个screens所分享；font被按照需求所加载或者卸载，同时被数个client分享；font经常被缓存在server中；xlib没有提供应用之间的图像上下文分享功能；

client程序是被事件驱动的；事件可能是请求的副产物（例如：重新生成windows的Expose事件）；也可以是完全异步的（例如通过键盘）；client被要求悉知事件，因为其他的应用也可以给你的程序发送事件，所以程序必须准备处理所有类型的事件；

输入事件（例如：鼠标移动或者一个键被按下）从服务器异步到达，并在队列中等待，知道他们被显示的调用（例如XNextEvent()或者XWindowEvent()）；此外，一些库函数（例如XRaiseWindow()）生成Expose和ConfigureRequest事件，这些事件也会异步到达，但是client或许会希望 在调用一个 可以让服务器生成事件的函数之后 通过调用XSync() 显式的等待他们；

#### 1.2 Error

有一些函数返回**Status**，它是一个整数，用来指示错误；如果函数返回一个零状态，则表示返回参数尚未被更新；由于C语言不支持返回多个值，因此很多要通过将结果写入client-passed存储来返回结果；默认情况下，错误不是通过标准库处理就是通过你提供的方法处理；返回字符串指针的函数，如果字符串不存在，就会返回NULL指针；

X server在检测到协议错误的时候会报告这些错误；如果一个请求会产生多个错误，那么server会报告这些错误中的任何一个；

由于Xlib通常不会立即将请求送入server（通常会缓存它们），错误的报告或许会比错误的发生会延迟很多；处于debug的考虑，xlib提供了强制同步机制；当同步机制被打开的时候，错误就能被及时的汇报；

*（11.8.1 enabling or disable synchronization：在进行调试时，让xlib同步运行会方便很多，这样在错误出现的时候会及时报告错误；使用`XSynchronize()`函数启用或禁用同步；但是需要注意的是当你启用同步的时候，图像的绘制速度将会减慢至少30倍甚至更多；在posix标准系统下，有一个全局变量_Xdebug，如果在debugger下运行程序前将这个变量设为非零，将会强制同步库行为；完成这些工作后，所有生成协议请求的函数会调用所谓的after function，`XSetAfterFunction()`设置会被调用的函数）*

当xlib检测到错误的时候，他会调用你的程序提供的错误处理句柄；如果你没有提供错误处理，这个错误会被打印，并且你的程序会被终止；

#### 1.3 标准头文件

以下是Xlib的标准库

- `X11/Xlib.h`

  这是Xlib最主要的头文件，所有主要的xlib符号被声明在这个文件里；这个文件中还包含了一个预处理器符号`XlibSpecificationRelease` 

  

- `X11/X.h`

  这个文件中声明了应用软件所需要的X 协议的类型和常量；它是被X11/Xlib.h所包含的，因此不应该直接引用这个头文件

  

- `X11/Xcms.h`

  这个文件中包含了“颜色管理函数（https://tronche.com/gui/x/xlib/color/）”中描述的许多颜色管理功能的符号；前缀为'Xcms'的所有函数，类型，符号，加上颜色转换上下文宏，都被定义在这个文件里；在引用这个文件之前必须引用Xlib.h 

  

- `X11/Xutil.h`

  这个文件中定义了很多用于inter-client(网络client)交互和应用软件实用的函数，详情参照 "[Inter-Client Communication Functions](https://tronche.com/gui/x/xlib/ICC/)" 和 "[Application Utility Functions](https://tronche.com/gui/x/xlib/utilities/)". 在包含这个头文件前必须先包含`X11/Xlib.h`

  

- `X11/Xresource.h`

  这个文件定义了用于资源管理器设施的全部函数，类型和符号；详情参见"[Resource Manager Functions](https://tronche.com/gui/x/xlib/resource-manager/)". 引用前必须引用`X11/Xlib.h`

  

- `X11/Xatom.h`

  这个文件声明了全部的预定义atom，这些atom前缀为'XA_' 

  

- `X11/cursorfont.h`

  这个文件声明了标准光标字体的光标符号，这些符号被列出在[X Font Cursors](https://tronche.com/gui/x/xlib/appendix/b/). 所有这些符号的前缀都为"XC_".

  

- `X11/keysymdef.h`

  这个文件声明了全部的标准KeySym值，这些值是以"XK_"为前缀的符号，这些KeySyms被按组排列，并且有一个预处理器符号控制每个组的内容；在文件中，预处理器符号必须先于这些内容被声明，以让预处理器符号获取这些值 . 这些预处理器符号是XK_MISCELLANY, XK_LATIN1, XK_LATIN2, XK_LATIN3, XK_LATIN4, XK_KATAKANA, XK_ARABIC, XK_CYRILLIC, XK_GREEK, XK_TECHNICAL, XK_SPECIAL, XK_PUBLISHING, XK_APL, XK_HEBREW, XK_THAI, and XK_KOREAN.

  

- `X11/keysym.h`

  这个文件定义了预处理器符号XK_MISCELLANY, XK_LATIN1, XK_LATIN2, XK_LATIN3, XK_LATIN4, 和 XK_GREEK，也包含了`X11/keysymdef.h`.

  

- `X11/Xlibint.h`

  这个文件中定义了扩展所用到的全部函数，类型和符号，关于扩展，详情参照 [Extensions](https://tronche.com/gui/x/xlib/appendix/c/). 这个文件自动的被包含在`X11/Xlib.h`

  

- `X11/Xproto.h`

  这个文件定义了基础X协议的类型和符号，用于实现扩展；这个文件被自动的包含在`X11/Xlibint.h`里，因此应用程序和扩展程序里不应当直接使用这个文件；

  

- `X11/Xprotostr.h`

  This file declares types and symbols for the basic X protocol, for use in implementing extensions. It is included automatically from **`X11/Xproto.h`**, so application and extension code should never need to reference this file directly.同上

  

- **`X11/X10.h`**

  这个文件里定义了X10所兼容的功能所用到的全部函数，类型，符号；[Compatibility Functions](https://tronche.com/gui/x/xlib/appendix/d/).

#### 1.4 Generic Values and Types

下面这些符号有Xlib所定义，并且在这个手册中贯穿始终；

1. xlib定义了**Bool**和布尔类型的值 **True** **False**
2. **None**是资源ID和atom通用的NULL
3. 类型**XID**用作通用资源ID
4. 类型XPointer被定义为char *，用作指向数据的不透明指针

#### 1.5 名称和参数的约定

Xlib follows a number of conventions for the naming and syntax of the functions. Given that you remember what information the function requires, these conventions are intended to make the syntax of the functions more predictable.

The major naming conventions are:

- 

- To differentiate the X symbols from the other symbols, the library uses mixed case for external symbols. It leaves lowercase for variables and all uppercase for user macros, as per existing convention.

  

- All Xlib functions begin with a capital X.

  

- The beginnings of all function names and symbols are capitalized.

  

- All user-visible data structures begin with a capital X. More generally, anything that a user might dereference begins with a capital X.

  

- Macros and other symbols do not begin with a capital X. To distinguish them from all user symbols, each word in the macro is capitalized.

  

- All elements of or variables in a data structure are in lowercase. Compound words, where needed, are constructed with underscores (_).

  

- The display argument, where used, is always first in the argument list.

  

- All resource objects, where used, occur at the beginning of the argument list immediately after the display argument.

  

- When a graphics context is present together with another type of resource (most commonly, a drawable), the graphics context occurs in the argument list after the other resource. Drawables outrank all other resources.

  

- Source arguments always precede the destination arguments in the argument list.

  

- The x argument always precedes the y argument in the argument list.

  

- The width argument always precedes the height argument in the argument list.

  

- Where the x, y, width, and height arguments are used together, the x and y arguments always precede the width and height arguments.

  

- Where a mask is accompanied with a structure, the mask always precedes the pointer to the structure in the argument list.

#### 1.6 编程注意事项

主要的编程注意事项如下：

1. 在X中坐标和尺寸实际上是一个16位的量；这么做是为了在满足给定性能的情况下尽可能减少带宽（X是cs架构，带宽会影响性能）；接口中坐标经常被声明为int型；超过16位的值将被截断；长和宽被声明为无符号量；
2. 来自不同制造商的键盘可能是最大的变数；如果你想要你的程序有较高的可移植性，那么你应该在针对键盘的处理上多加小心
3. 用户应该对他们的显示屏拥有控制权，所以当你编写程序的时候尽量去控制window而不是去控制整个screen；你在顶级窗口中最好只控制你自己的应用；更多信息请参照"[Inter-Client Communication Functions](https://tronche.com/gui/x/xlib/ICC/)和 [*Inter-Client Communication Conventions Manual*](https://tronche.com/gui/x/icccm/).



#### 1.8 格式约定

这章是介绍接口文档的格式的，不翻译了；



### 第二章：Display函数

在你的程序可以使用一个display之前，你必须同Xserver建立链接；一旦你建立了链接，你就可以使用本章中讨论的xlib的宏和函数去返回关于display的信息；

#### 2.1 打开（链接）display

打开一个控制着display的Xserver，使用**XOpenDisplay()**

##### Syntax

```
Display *XOpenDisplay(display_name)
      char *display_name;
```

##### Arguments

| **display_name** | 指定一个display名称，这个名称将用于确定哪个display和通信域会被使用；在POSIX标准的系统下，这个值是NULL，因为这个值默认的和DISPLAY系统变量一样 |
| ---------------- | ------------------------------------------------------------ |

##### Description

display名称的编码和解释依赖于实现； Host Portable Character Encoding中的字符串是可以的；对于其他字符的支持则取决于实现；对于POSIX标准的系统，dispaly名称或者DISPLAY环境变量可以是以下这个格式：

```
	hostname:number.screen_number
```



| **hostname**      | 指定display物理链接的主机的名称，后面可以跟一个:或者两个::   |
| ----------------- | ------------------------------------------------------------ |
| **number**        | 指明主机所拥有的display server的编号，你可以在这一项后面随意的添加一个句点(.)；一个cpu可以拥有多个display，如果有多个，那么第一个display的编号是0； |
| **screen_number** | 指明会被用到的screen编号，一个Xserver可以控制多个screen；screen_number是一个内部变量，C语言可以使用 **[DefaultScreen()](https://tronche.com/gui/x/xlib/display/display-macros.html#DefaultScreen)** 访问，其他的语言可以使用 **[XDefaultScreen()](https://tronche.com/gui/x/xlib/display/display-macros.html#DefaultScreen)** 访问，参照 "[Display Macros](https://tronche.com/gui/x/xlib/display/information.html#display)"). |



例如：下面这个例子表明要使用一叫dual-headed的机器的第0个display的第一个screen

> dual-headed:0.1

**XOpenDisplay()** 函数返回一个 [Display](https://tronche.com/gui/x/xlib/display/opening.html#Display) 结构体，这个结构体用作和Xserver的链接，并且包含了这个Xserver的全部信息； **XOpenDisplay()** 使用TCP或DEC网路协议链接你的应用和Xserver，也可能用一些本地网络进程协议链接Xserver和应用； 如果hostname和display编号之间使用一个分号隔离，那么就会使用TCP协议；如果没有分隔，那么xlib会使用它认为最快速的协议；如果使用两个分号分隔，那么将会使用DECnet；一个Xserver能够同时支持任何一种传输机制或者全部的机制；特殊的Xlib实现可以支持更多种传输机制；

如果顺利的话， **XOpenDisplay()** 将会返回一个指向**Display**结构体的指针；这个结构体被定义在**X11/Xlib.h**. 如果**XOpenDisplay()** 执行的不顺利，那么它就会返回一个NULL，如果XOpenDisplay()** 被成功调用，那么这个dispaly下面的全部screen都可以被这个client使用；指定的screen的编号可以使用**[DefaultScreen()](https://tronche.com/gui/x/xlib/display/display-macros.html#DefaultScreen)**返回 （或者使用 **[XDefaultScreen()](https://tronche.com/gui/x/xlib/display/display-macros.html#DefaultScreen)** 函数). 你可以使用information宏指令或者函数去访问Display或者 [Screen](https://tronche.com/gui/x/xlib/display/display-macros.html) 结构体的内容.更多关于使用宏指令和函数获取Dispaly结构体信息的知识请参照 [Display Macros](https://tronche.com/gui/x/xlib/display/information.html#display).

Xserver或许实现了多种不同的接入机制(see "[Controlling Host Access](https://tronche.com/gui/x/xlib/window-and-session-manager/controlling-host-access/)").



#### 2.2 获取关于display，image format，screen的信息

xlib提供了诸多实用的宏和对应的函数来从Display结构体中返回信息，宏是给C语言用的，对应的函数则是给其他函数用的；

##### 2.2.1 Display Macros

应用软件不应该直接修改Display或者Screen结构体中的内容，这些成员应该是只读的，尽管他们可能会因为一些操作被改变；

下述的被列出的C语言宏，以及对应的其他语言的函数是等价的，他们都可以返回数据

###### AllPlanes

```c
AllPlanes

unsigned long XAllPlanes() 
```

Both return a value with all bits set to 1 suitable for use in a plane argument to a procedure.

###### BlackPixel, WhitePixel

Both **BlackPixel()** and **WhitePixel()** can be used in implementing a monochrome application. These pixel values are for permanently allocated entries in the default colormap. The actual RGB (red, green, and blue) values are settable on some screens and, in any case, may not actually be black or white. The names are intended to convey the expected relative intensity of the colors.

```c
BlackPixel(display, screen_number)

unsigned long XBlackPixel(display, screen_number)
      Display *display;
      int screen_number;
```

| **display**       | Specifies the connection to the X server.                   |
| ----------------- | ----------------------------------------------------------- |
| **screen_number** | Specifies the appropriate screen number on the host server. |

Both return the black pixel value for the specified screen.

```c
WhitePixel(display, screen_number)

unsigned long XWhitePixel(display, screen_number)
      Display *display;
      int screen_number;
```

| **display**       | Specifies the connection to the X server.                   |
| ----------------- | ----------------------------------------------------------- |
| **screen_number** | Specifies the appropriate screen number on the host server. |

Both return the white pixel value for the specified screen.

###### ConnectionNumber

```c
ConnectionNumber(display) 
int XConnectionNumber(display)
    Display *display; 
```

| **display** | Specifies the connection to the X server. |
| ----------- | ----------------------------------------- |
|             |                                           |

Both return a connection number for the specified display. On a POSIX-conformant system, this is the file descriptor of the connection.DefaultColormap```DefaultColormap(**display**, **screen_number**) Colormap XDefaultColormap(**display**, **screen_number**)      Display ***display**;      int **screen_number**; `

| **display**       | Specifies the connection to the X server.                   |
| ----------------- | ----------------------------------------------------------- |
| **screen_number** | Specifies the appropriate screen number on the host server. |

Both return the default colormap ID for allocation on the specified screen. Most routine allocations of color should be made out of this colormap.

###### DefaultDepth

```c
DefaultDepth(display, screen_number) 
int XDefaultDepth(display, screen_number)      
    Display *display;      
	int screen_number; 
```

| **display**       | Specifies the connection to the X server.                   |
| ----------------- | ----------------------------------------------------------- |
| **screen_number** | Specifies the appropriate screen number on the host server. |

Both return the depth (number of planes) of the default root window for the specified screen. Other depths may also be supported on this screen (see .PN XMatchVisualInfo ).

###### XListDepths

To determine the number of depths that are available on a given screen, use **XListDepths()**.

```c
int *XListDepths(display, screen_number, count_return)      
    Display *display;      
	int screen_number;      
	int *count_return; 
```



| **display**       | Specifies the connection to the X server.                   |
| ----------------- | ----------------------------------------------------------- |
| **screen_number** | Specifies the appropriate screen number on the host server. |
| **count_return**  | Returns the number of depths                                |

The **XListDepths()** function returns the array of depths that are available on the specified screen. If the specified **screen_number** is valid and sufficient memory for the array can be allocated, **XListDepths()** sets **count_return** to the number of available depths. Otherwise, it does not set count_return and returns NULL. To release the memory allocated for the array of depths, use **[XFree()](https://tronche.com/gui/x/xlib/display/XFree.html)**.

###### DefaultGC

```c
DefaultGC(display, screen_number) 
GC XDefaultGC(display, screen_number)      
    Display *display;      
	int screen_number; 
```

| **display**       | Specifies the connection to the X server.                   |
| ----------------- | ----------------------------------------------------------- |
| **screen_number** | Specifies the appropriate screen number on the host server. |

Both return the default graphics context for the root window of the specified screen. This GC is created for the convenience of simple applications and contains the default GC components with the foreground and background pixel values initialized to the black and white pixels for the screen, respectively. You can modify its contents freely because it is not used in any Xlib function. This GC should never be freed.

###### DefaultRootWindow

```c
DefaultRootWindow(display) 
Window XDefaultRootWindow(display)      
    Display *display; 
```

| **display** | Specifies the connection to the X server. |
| ----------- | ----------------------------------------- |
|             |                                           |

Both return the root window for the default screen.



## DefaultScreenOfDisplay

```
DefaultScreenOfDisplay(**display**) Screen *XDefaultScreenOfDisplay(**display**)      Display ***display**; 
```

| **display** | Specifies the connection to the X server. |
| ----------- | ----------------------------------------- |
|             |                                           |

Both return a pointer to the default screen.



## ScreensOfDisplay

```
ScreenOfDisplay(**display**, **screen_number**) Screen *XScreenOfDisplay(**display**, **screen_number**)      Display ***display**;      int **screen_number**; 
```

| **display**       | Specifies the connection to the X server.                   |
| ----------------- | ----------------------------------------------------------- |
| **screen_number** | Specifies the appropriate screen number on the host server. |

Both return a pointer to the indicated screen.



## DefaultScreen

```
DefaultScreen(**display**) int XDefaultScreen(**display**)      Display ***display**; 
```

| **display** | Specifies the connection to the X server. |
| ----------- | ----------------------------------------- |
|             |                                           |

Both return the default screen number referenced by the **[XOpenDisplay()](https://tronche.com/gui/x/xlib/display/opening.html)** function. This macro or function should be used to retrieve the screen number in applications that will use only a single screen.



## DefaultVisual

```
DefaultVisual(**display**, **screen_number**) Visual *XDefaultVisual(**display**, **screen_number**)      Display ***display**;      int **screen_number**; 
```

| **display**       | Specifies the connection to the X server.                   |
| ----------------- | ----------------------------------------------------------- |
| **screen_number** | Specifies the appropriate screen number on the host server. |

Both return the default visual type for the specified screen. For further information about visual types, see section 3.1.



## DisplayCells

```
DisplayCells(**display**, **screen_number**) int XDisplayCells(**display**, **screen_number**)      Display ***display**;      int **screen_number**; 
```

| **display**       | Specifies the connection to the X server.                   |
| ----------------- | ----------------------------------------------------------- |
| **screen_number** | Specifies the appropriate screen number on the host server. |

Both return the number of entries in the default colormap.



## DisplayPlanes

```
DisplayPlanes(**display**, **screen_number**) int XDisplayPlanes(**display**, **screen_number**)      Display ***display**;      int **screen_number**; 
```

| **display**       | Specifies the connection to the X server.                   |
| ----------------- | ----------------------------------------------------------- |
| **screen_number** | Specifies the appropriate screen number on the host server. |

Both return the depth of the root window of the specified screen. For an explanation of depth, see the [glossary](https://tronche.com/gui/x/xlib/glossary/).



## DisplayString

```
DisplayString(**display**) char *XDisplayString(**display**)      Display ***display**; 
```

| **display** | Specifies the connection to the X server. |
| ----------- | ----------------------------------------- |
|             |                                           |

Both return the string that was passed to **[XOpenDisplay()](https://tronche.com/gui/x/xlib/display/opening.html)** when the current display was opened. On POSIX-conformant systems, if the passed string was NULL, these return the value of the DISPLAY environment variable when the current display was opened. These are useful to applications that invoke the **fork** system call and want to open a new connection to the same display from the child process as well as for printing error messages.



## XExtendedMaxRequestSize

```
long XExtendedMaxRequestSize(**display**) Display ***display**; 
```

| **display** | Specifies the connection to the X server. |
| ----------- | ----------------------------------------- |
|             |                                           |

The **XExtendedMaxRequestSize()** function returns zero if the specified display does not support an extended-length protocol encoding; otherwise, it returns the maximum request size (in 4-byte units) supported by the server using the extended-length encoding. The Xlib functions **[XDrawLines()](https://tronche.com/gui/x/xlib/graphics/drawing/XDrawLines.html)**, **[XDrawArcs()](https://tronche.com/gui/x/xlib/graphics/drawing/XDrawArcs.html)**, **[XFillPolygon()](https://tronche.com/gui/x/xlib/graphics/filling-areas/XFillPolygon.html)**, **[XChangeProperty()](https://tronche.com/gui/x/xlib/window-information/XChangeProperty.html)**, **[XSetClipRectangles()](https://tronche.com/gui/x/xlib/GC/convenience-functions/XSetClipRectangles.html)**, and **[XSetRegion()](https://tronche.com/gui/x/xlib/utilities/regions/XSetRegion.html)** will use the extended-length encoding as necessary, if supported by the server. Use of the extended-length encoding in other Xlib functions (for example, **[XDrawPoints()](https://tronche.com/gui/x/xlib/graphics/drawing/XDrawPoints.html)**, **[XDrawRectangles()](https://tronche.com/gui/x/xlib/graphics/drawing/XDrawRectangles.html)**, **[XDrawSegments()](https://tronche.com/gui/x/xlib/graphics/drawing/XDrawSegments.html)**, **[XFillArcs()](https://tronche.com/gui/x/xlib/graphics/filling-areas/XFillArcs.html)**, **[XFillRectangles()](https://tronche.com/gui/x/xlib/graphics/filling-areas/XFillRectangles.html)**, **[XPutImage()](https://tronche.com/gui/x/xlib/graphics/XPutImage.html)**) is permitted but not required; an Xlib implementation may choose to split the data across multiple smaller requests instead.

###### XMaxRequestSize

```c
long XMaxRequestSize(display) 
    Display *display; 
```

| **display** | Specifies the connection to the X server. |
| ----------- | ----------------------------------------- |
|             |                                           |

The **XMaxRequestSize()** function returns the maximum request size (in 4-byte units) supported by the server without using an extended-length protocol encoding. Single protocol requests to the server can be no larger than this size unless an extended-length protocol encoding is supported by the server. The protocol guarantees the size to be no smaller than 4096 units (16384 bytes). Xlib automatically breaks data up into multiple protocol requests as necessary for the following functions: **[XDrawPoints()](https://tronche.com/gui/x/xlib/graphics/drawing/XDrawPoints.html)**, **[XDrawRectangles()](https://tronche.com/gui/x/xlib/graphics/drawing/XDrawRectangles.html)**, **[XDrawSegments()](https://tronche.com/gui/x/xlib/graphics/drawing/XDrawSegments.html)**, **[XFillArcs()](https://tronche.com/gui/x/xlib/graphics/filling-areas/XFillArcs.html)**, **[XFillRectangles()](https://tronche.com/gui/x/xlib/graphics/filling-areas/XFillRectangles.html)**, and **[XPutImage()](https://tronche.com/gui/x/xlib/graphics/XPutImage.html)**.

###### LastKnownRequestProcessed

```c
LastKnownRequestProcessed(display) 
unsigned long XLastKnownRequestProcessed(display)     
    Display *display; 
```

| **display** | Specifies the connection to the X server. |
| ----------- | ----------------------------------------- |
|             |                                           |

Both extract the full serial number of the last request known by Xlib to have been processed by the X server. Xlib automatically sets this number when replies, events, and errors are received.

###### NextRequest

```c
NextRequest(display) 
unsigned long XNextRequest(display)     
    Display *display; 
```

| **display** | Specifies the connection to the X server. |
| ----------- | ----------------------------------------- |
|             |                                           |

Both extract the full serial number that is to be used for the next request. Serial numbers are maintained separately for each display connection.

###### ProtocolVersion

```c
ProtocolVersion(display) 
int XProtocolVersion(display)      
    Display *display; 
```

| **display** | Specifies the connection to the X server. |
| ----------- | ----------------------------------------- |
|             |                                           |

Both return the major version number (11) of the X protocol associated with the connected display.

###### ProtocolRevision

```c
ProtocolRevision(display) 
int XProtocolRevision(display)      
    Display *display; 
```

| **display** | Specifies the connection to the X server. |
| ----------- | ----------------------------------------- |
|             |                                           |

Both return the minor protocol revision number of the X server.

###### QLength

```c
QLength(display) 
int XQLength(display)      
    Display *display; 
```

| **display** | Specifies the connection to the X server. |
| ----------- | ----------------------------------------- |
|             |                                           |

Both return the length of the event queue for the connected display. Note that there may be more events that have not been read into the queue yet (see **[XEventsQueued()](https://tronche.com/gui/x/xlib/event-handling/XEventsQueued.html)**).



## RootWindow

```
RootWindow(**display**, **screen_number**) Window XRootWindow(**display**, **screen_number**)      Display ***display**;      int **screen_number**; 
```

| **display**       | Specifies the connection to the X server.                   |
| ----------------- | ----------------------------------------------------------- |
| **screen_number** | Specifies the appropriate screen number on the host server. |

Both return the root window. These are useful with functions that need a drawable of a particular screen and for creating top-level windows.



## ScreenCount

```
ScreenCount(**display**) int XScreenCount(**display**)      Display ***display**; 
```

| **display** | Specifies the connection to the X server. |
| ----------- | ----------------------------------------- |
|             |                                           |

Both return the number of available screens.



## ServerVendor

```
ServerVendor(**display**) char *XServerVendor(**display**)      Display ***display**; 
```

| **display** | Specifies the connection to the X server. |
| ----------- | ----------------------------------------- |
|             |                                           |

Both return a pointer to a null-terminated string that provides some identification of the owner of the X server implementation. If the data returned by the server is in the Latin Portable Character Encoding, then the string is in the Host Portable Character Encoding. Otherwise, the contents of the string are implementation dependent.



## VendorRelease

```
VendorRelease(**display**) int XVendorRelease(**display**)      Display ***display**; 
```

| **display** | Specifies the connection to the X server. |
| ----------- | ----------------------------------------- |
|             |                                           |

Both return a number related to a vendor's release of the X server.






























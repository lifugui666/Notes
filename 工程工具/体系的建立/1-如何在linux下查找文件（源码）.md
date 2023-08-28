# 在linux下如何查找文件（源码）？

## 找文件

有好几种方法....

### 1. find

```shell
# 格式
# find [路径] [表达式]

--------------------------------------
# 常见用法:在当前目录下查找"myfile","myfile"为文件名称，也可使用正则表达式
find -name "myfile"
--------------------------------------
# 指定目录查找:从根目录（也就是/）开始查找"myfile"文件
find / -name "myfile"
--------------------------------------

```

总结：find在不加任何参数时，默认搜索路径是当前目录以及子目录，并且是暴力查找，因此小范围用用还行；在30G的磁盘下查找大概需要3s，这个速度着实不能算快；

### 2. locate

这个软件需要安装

```shell
sudo apt-get install plocate
```

```shell
# locate的语法简单
updatedb # 在使用locate之前应当使用updatedb命令，否则可能查找不到
locate myfine
```

总结：locate默认的查找范围是全部本地文件；但是locate的速度比find要快的多；locate本质上是在/var/lib/locatedb中查找，locatedb中记录了全部本地文件的信息，但是这个db的更新周期是由cron来决定的（即linux会周期性的更新这个locatedb）；因此在使用locate的时候要注意时效性，最好在使用前手动使用updatedb命令更新一下数据库；

### 3. whereis

whereis并**不是用来找文件的位置**的，whereis**是用来查找“命令”的位置的**

```shell
# 例如：我想知道ls命令到底在哪里？
whereis ls
# 结果如下
ls: /usr/bin/ls /usr/share/man/man1/ls.1.gz

# 这个结果的含义是
# ls命令的二进制文件位于 /usr/bin/ls 
# ls命令的手册文件位于 /usr/share/man/manl/ls.1.gz
# ls命令的源文件没找到

# 当然，也可以只查找其中一项
whereis -s ls # 查找ls的源代码
whereis -b ls # 查找ls的二进制文件
whereis -m ls # 查找ls的手册文件
```

### 4. which

which是用来查找命令的位置的，其结果和whereis -b的结果是一样的；

**which只会去系统变量路径下面查找**

```shell
# 所谓系统变量 可以用echo去查看
lee@lee-ThinkPad-A485:/$ echo $PATH
/home/lee/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games:/snap/bin:/snap/bin

lee@lee-ThinkPad-A485:/$ which ls
/usr/bin/ls
lee@lee-ThinkPad-A485:/$ whereis -b ls
ls: /usr/bin/ls
```

总结：可以很明确的看到，which的结果和whereis -b的结果是一样的；也就是说which实际上查找的是命令的二进制文件的位置；

同时我们应该注意到which只能查找系统变量路径下的内容；如果PATH出了问题，很可能使用which查找不到想要的结果；

### 5. type

type最大的作用其实是分辨一个命令是系统自带的还是后来安装的

```shell
lee@lee-ThinkPad-A485:/$ which ssh
/usr/bin/ssh
lee@lee-ThinkPad-A485:/$ type ssh
ssh 是 /usr/bin/ssh
lee@lee-ThinkPad-A485:/$ which ls
/usr/bin/ls
lee@lee-ThinkPad-A485:/$ type ls
ls 是 "ls --color=auto" 的别名
```

总结：从这里可以看出，如果对后来安装的命令使用type，会显示这个软件的二进制文件位置；否则就可以判断这个命令是原带的；



## 如何查找一个字段？

作为高贵的linux用户，我希望能直接在terminal上实现 搜索这个路径下指定的字段 的功能；

```shell
# 可以用
grep -r "目标字段" * . # 其中 *表示所有文件， .表示当前目录

# 使用-rn可以简化这个命令
grep -rn "目标字段"

# -rn会在所有的文件里搜索，实际使用中我们是不希望在二进制文件中查找字段的...所以有第三中方法
grep -Irn "目标字段"
```



## 如何找到源码(dpkg -S)？

当我们在代码中看到某个函数，想要了解一下这个函数时，如何找到这个文件？在研究X11的一些内容时，我遇到了一些函数，这些函数明显是X11的API；现在我想要知道这个API的源码，应该怎么找？

```c
//xsel.c

/*
 * xsel -- manipulate the X selection
 * Copyright (C) 2001 Conrad Parker <conrad@vergenet.net>
 *
 * Permission to use, copy, modify, distribute, and sell this software and
 * its documentation for any purpose is hereby granted without fee, provided
 * that the above copyright notice appear in all copies and that both that
 * copyright notice and this permission notice appear in supporting
 * documentation.  No representations are made about the suitability of this
 * software for any purpose.  It is provided "as is" without express or
 * implied warranty.
 */
//...略
#include <X11/Xlib.h> 
#include <X11/Xatom.h>
//...略

/* Find the "CLIPBOARD" selection if required */
if (want_clipboard) 
{
	selection = XInternAtom (display, "CLIPBOARD", False); //我想找到XInternAtom函数的具体定义
}

```

从这个函数的名字不难看出这个函数不是Xlib.h的就是Xatom.h的；

在linux中，尤其是C语言相关的内容，找头文件是很容易的，使用上面介绍的locate命令或者find命令都能找到；但是想要找对应的实现(.c文件)或者源码就很困难了，因为一般情况下我们使用deb包（debian系下）安装的软件，都是二进制文件安装，不附带源码的；因此我们的查找思路如下：

1. 使用`dpgk -S 头文件`的方式查找头文件所属的安装包；
2. 通过安装包找源码；

```shell
# 使用dpkg -S
lee@lee-ThinkPad-A485:/$ dpkg -S X11/Xlib.h
libx11-dev:amd64: /usr/include/X11/Xlib.h
# 可以看到，这个文件所属的安装包是libx11-dev
# 但是只有头文件是不够的，有头文件那么必定有.so文件，一般情况下这个.so文件应该和头文件或者跟安装包文件名称相同
# 如果我们的系统里查找不到这个.so文件，那么问题也不大，实际上按照这个安装包的名称去查找对应的源码已经足够了；不过这里我们还是查找一下动态链接库
lee@lee-ThinkPad-A485:~$ locate -i xlib.so
/snap/gnome-3-38-2004/140/usr/lib/x86_64-linux-gnu/graphviz/libgvplugin_xlib.so.6
/snap/gnome-3-38-2004/140/usr/lib/x86_64-linux-gnu/graphviz/libgvplugin_xlib.so.6.0.0
/snap/gnome-3-38-2004/143/usr/lib/x86_64-linux-gnu/graphviz/libgvplugin_xlib.so.6
/snap/gnome-3-38-2004/143/usr/lib/x86_64-linux-gnu/graphviz/libgvplugin_xlib.so.6.0.0
/snap/gnome-42-2204/120/usr/lib/x86_64-linux-gnu/graphviz/libgvplugin_xlib.so
/snap/gnome-42-2204/120/usr/lib/x86_64-linux-gnu/graphviz/libgvplugin_xlib.so.6
/snap/gnome-42-2204/120/usr/lib/x86_64-linux-gnu/graphviz/libgvplugin_xlib.so.6.0.0
/snap/gnome-42-2204/126/usr/lib/x86_64-linux-gnu/graphviz/libgvplugin_xlib.so
/snap/gnome-42-2204/126/usr/lib/x86_64-linux-gnu/graphviz/libgvplugin_xlib.so.6
/snap/gnome-42-2204/126/usr/lib/x86_64-linux-gnu/graphviz/libgvplugin_xlib.so.6.0.0
# 虽然有输出但是动态库是不会放在这里的，动态库一般的位置是/usr/lib/
# 换个名字再试一次
lee@lee-ThinkPad-A485:~$ locate -i libx11.so
# 这里省略了一部分输出...
/usr/lib/i386-linux-gnu/libX11.so.6
/usr/lib/i386-linux-gnu/libX11.so.6.4.0
/usr/lib/x86_64-linux-gnu/libX11.so### ！！！！！！应该是这个
/usr/lib/x86_64-linux-gnu/libX11.so.6
/usr/lib/x86_64-linux-gnu/libX11.so.6.4.0
# 这里我用了两个可能的名称去查找这个动态库；注意一下动态库一般的路径是/usr/lib/；
# 至此我们能确定，X11\lib.h这个头文件是libx11-dev包里的；并且我们找到的.so文件也可以让我们确定；

# 接下来我们就需要去找这个头文件的实现了
lee@lee-ThinkPad-A485:~$ cd /tmp/ # 因为要下载一些东西所以我们进入tmp目录工作
lee@lee-ThinkPad-A485:/tmp$ sudo apt-get source libx11-dev
lee@lee-ThinkPad-A485:/tmp$ ls |grep libx11
libx11-1.7.5
libx11_1.7.5-1ubuntu0.2.diff.gz
libx11_1.7.5-1ubuntu0.2.dsc
libx11_1.7.5.orig.tar.gz
libx11_1.7.5.orig.tar.gz.asc
ee@lee-ThinkPad-A485:/tmp$ cd libx11-1.7.5/
lee@lee-ThinkPad-A485:/tmp/libx11-1.7.5$ ls
aclocal.m4  compile       configure.ac  depcomp     install-sh   Makefile.in  NEWS       src
AUTHORS     config.guess  COPYING       docbook.am  ltmain.sh    man          nls        test-driver
autogen.sh  config.sub    cpprules.in   include     m4           missing      README.md  x11.pc.in
ChangeLog   configure     debian        INSTALL     Makefile.am  modules      specs      x11-xcb.pc.in
lee@lee-ThinkPad-A485:/tmp/libx11-1.7.5$ cd src/
# 现在我们可以看到libx11-dev包下面的源码基本上都在这里了，接下来我们可以尝试使用grep -iIrn XInternAtom尝试一下是否能找到这个函数的定义
ee@lee-ThinkPad-A485:/tmp/libx11-1.7.5/src$ grep -Irn XInternAtom
Iconify.c:72:    prop = XInternAtom (dpy, "WM_CHANGE_STATE", False);
GetWMProto.c:68:    prop =  XInternAtom(dpy, "WM_PROTOCOLS", False);
GetWMCMapW.c:68:    prop =  XInternAtom(dpy, "WM_COLORMAP_WINDOWS", False);
SetWMProto.c:68:    prop = XInternAtom (dpy, "WM_PROTOCOLS", False);
xcms/LRGB.c:467:    Atom  CorrectAtom = XInternAtom (dpy, XDCCC_CORRECT_ATOM_NAME, True);
xcms/LRGB.c:468:    Atom  MatrixAtom  = XInternAtom (dpy, XDCCC_MATRIX_ATOM_NAME, True);
xkb/XKB.c:35:XkbInternAtomFunc       _XkbInternAtomFunc  = XInternAtom;
xkb/XKB.c:772:    _XkbInternAtomFunc = (getAtom ? getAtom : XInternAtom);
xkb/XKBUse.c:693:                        xkbi->composeLED = XInternAtom(dpy, str, False);
xkb/XKBUse.c:705:            xkbi->composeLED = XInternAtom(dpy, "Compose", False);
IntAtom.c:58:Atom _XInternAtom(
IntAtom.c:163:XInternAtom ( ### ！！！！！！！！在这里
IntAtom.c:176:    if ((atom = _XInternAtom(dpy, name, onlyIfExists, &sig, &idx, &n))) {
IntAtom.c:243:XInternAtoms (
IntAtom.c:268:	if (!(atoms_return[i] = _XInternAtom(dpy, names[i], onlyIfExists,
xlibi18n/lcPrTxt.c:143:    else if (encoding == XInternAtom(dpy, "UTF8_STRING", False))
xlibi18n/lcPrTxt.c:145:    else if (encoding == XInternAtom(dpy, "COMPOUND_TEXT", False))
xlibi18n/lcPrTxt.c:147:    else if (encoding == XInternAtom(dpy, XLC_PUBLIC(lcd, encoding_name), False))
xlibi18n/lcTxtPr.c:102:	    encoding = XInternAtom(dpy, "UTF8_STRING", False);
xlibi18n/lcTxtPr.c:106:	    encoding = XInternAtom(dpy, "COMPOUND_TEXT", False);
xlibi18n/lcTxtPr.c:110:	    encoding = XInternAtom(dpy, XLC_PUBLIC(lcd, encoding_name), False);
xlibi18n/lcTxtPr.c:176:	    encoding = XInternAtom(dpy, "COMPOUND_TEXT", False);
WMProps.c:143:        XChangeProperty (dpy, w, XInternAtom(dpy, "WM_LOCALE_NAME", False),
SetWMCMapW.c:68:    prop = XInternAtom (dpy, "WM_COLORMAP_WINDOWS", False);
ScrResStr.c:42:    prop_name = XInternAtom(screen->display, "SCREEN_RESOURCES", True);
# 至此，我们找到了函数的定义

```

（我原本以为XInternAtom这个函数会在X11/Xatom.h里，但是经过两轮查找我发现它居然在X11/Xlib.h里....）

总的来说这个方法通用性其实不是特别高...但总不失为一种思路




















































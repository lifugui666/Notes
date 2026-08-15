# linux的包管理工具

## 历史

### 远古时代如何安装软件？

上古时代，在那个linux和windows还不存在的时代，人们想要安装一个软件的难度是很高的，如果想要安装软件，就要找到源代码包，自己解压，自己配置编译的选项，然后进行编译获得二进制文件，然后还需要手动将这个可执行文件和另一些配置文件复制到指定的位置，然后还要进行文件的权限设置；我相信在坐的诸位如果在那个年代，应该大部分人都难以完成软件的安装；卸载软件稍微轻松一点，卸载就是将安装倒过来再进行一遍；

在这个时期，软件除了安装困难之外还有两个大问题：

1. 文件权限过于复杂
2. 软件的升级过于困难

后来软件的发行慢慢开始使用二进制包发行，这为用户省去了编译的过程，但是仍旧没有解决上述的两个痛点；

### 软件安装的进化

为了解决上述两个问题，人们做出了不少努力，有两个派别：

1. 让软件自己解决：这个方案是微软的...在windows XP之前，微软的操作系统不包含软件管理功能，人们安装，卸载软件要么像远古时期那么手动安装，要么就使用软件自带的安装脚本，软件开发者为了自己软件的易用性确实也会乐于编写这个安装脚本；否则自己写的软件别人装不上，怎么能盈利？实际上在今天的windows上仍旧能看到这个方案的影子，windows用户应该都使用过软件自带的installer来安装软件；

2. 系统级的解决方案：逐渐出现了一些系统级别的工具来帮助人们安装；这些工具又分为两个派别：

   1. ports派：ports是unix的一个工具集，prots用户仍旧需要获取源码包，然后配置，编译，安装；但是ports可将这些步骤中的大部分自动化；ports的缺陷是无法查看已经安装的软件包含那些文件，也无法升级软件；

   2. system V unix：这个工具完全不管你怎么安装，你该编译还是要自己编译，该安装还是自己安装；但是这个工具会帮你记住这些软件都安装了什么文件，这些文件都放在什么地方；

      如果使用system v**发布**软件，需要先编译，然后准备一个文件列表，这个文件中应当记录安装这个软件所有需要的所有文件的位置，权限等信息，然后运行一系列命令来查找和检查这个列表中的文件，并且最终将列表所述的内容打包成一个压缩包；

      这个压缩包可以在任何安装了system v的机器上使用system v的命令进行软件的安装；system v将把列表中的文件放到合适的地方，并且会维护一个数据库记录各个软件的文件的位置；

      system v的问题在于编译配置很不方便，因为其实一般用户拿到的都是压缩包，不能自己编译；



### linux的选择

linux的选择集合了unix的ports和system v的优势；最先推出包管理工具的是红帽：RPM-redhat package manager；当然现在有很多其他的发行版也在用rpm；rpm包分为rpm和srpm，其中rpm包只包含二进制文件，而srpm包含源码，用户可以自己编译；



目前linux界在包管理工具上分为两派：

1. rpm：redhat，fedora，centos，openSUSE等
2. deb：debian，ubuntu等

红帽系的包管理工具，底层是rpm，上层是yum；

debian系的包管理工具，底层是dpkg，上层是apt-get；



**我相信大家都用过手机上的应用商城...实际上yum和apt-get就是linux的应用商城罢了**

## deb/dsc/apt-get

出于个人的使用习惯，这里优先学习一下debian的处理方案；

在debian系的linux中，软件的安装包格式是.deb；我们使用dpkg命令安装.deb包；

deb包分为两种类型：

1. **deb**包，包含可执行文件，库文件，配置文件，info，版权，其他文档；
2. **dsc**包，包含源代码，版本修改声明，构建指令，编译工具等；



### deb包的结构

deb由三个部分组成：

1. 数据包：包含实际上安装的程序数据，一般为"data.tar.xxx"
2. 安装信息&控制：包含deb包的安装说明，标识，脚本等，一般为"control.tar.gz"
3. 二进制数据：文件头等信息，需要用软件查看；

```shell
# deb包中包含了DEBIAN 和 软件具体的安装目录
soft-name
    |--DEBIAN
    |       |--control # 描述性文件
    |       |--postinst# 在安装后会被调用
    |       |--postrm  # 卸载后会被调用
    |       |--preinst # 在安装前会被调用
    |       |--prerm   # 卸载前会被调用
    |       |--copyright
    |
    |--opt
    |   |--files
    |--etc
    |   |--files
    ...
```

#### control文件

| 字段         | 用途                                   | 注                                                           |
| ------------ | -------------------------------------- | ------------------------------------------------------------ |
| Package      | 程序名                                 | 不能有空格                                                   |
| Version      | 版本号                                 |                                                              |
| Description  | 说明                                   |                                                              |
| Sections     | 软件的类型                             | utils，net，mall，X11等                                      |
| Priority     | 程序对系统的重要度                     | required，standard，optional，extra等                        |
| Essential    | 是否为系统的基本软件包？               | yes，no；若为yes则不允许卸载（当然linux上你可以用root权限卸载任何文件...） |
| Architecture | 支持的架构平台                         | i386，amd64等                                                |
| Source       | 源代码的名称                           |                                                              |
| depends      | 软件所依赖的其他软件包和库的名字       |                                                              |
| Pre-Depends  | 在安装本软件之前就应该安装好的软件和库 |                                                              |
| Recommend    | 推荐安装的其他软件包和库               |                                                              |
| Suggest      | 建议安装的其他软件包和库               |                                                              |



### apt

首先声明一点，你可以认为apt是apt-get的友好版本；apt拥有apt-get的几乎所有功能，并且apt默认开启了进度条，对用户更加友好；

apt这个东西大致相当于linux的应用商店；

#### 源

应用商店肯定是需要服务器提供服务的...在apt中，我们称呼这些提供服务的服务器为源；

配置文件`/etc/apt/source.list`中记录了软件源的镜像站点的地址；但是这些镜像站点上到底有什么软件目前还不清楚，此时我们可以使用`apt-get update`命令来探查这些站点；`apt-get update`会扫描每一个软件源服务器，并建立一个软件索引文件放在本地的`/var/lib/apt/lists/`中;

在ubuntu下面源的配置文件如下：

```shell
# deb cdrom:[Ubuntu 22.04 LTS _Jammy Jellyfish_ - Release amd64 (20220419)]/ jammy main restricted

# See http://help.ubuntu.com/community/UpgradeNotes for how to upgrade to
# newer versions of the distribution.
deb http://cn.archive.ubuntu.com/ubuntu/ jammy main restricted
# deb-src http://cn.archive.ubuntu.com/ubuntu/ jammy main restricted

# 后略...
```

服务器地址总是这样以`deb`和`deb-src`一对的形式出现，其中默认情况下，deb-src是被注释掉的；如果想要使用`apt-get source xxx`来获取dsc包，那么就应当将deb-src放出来；



### 如何获取源代码？

使用：apt-get source xxx

```shell
# 例如：获取xsel的源码
lee@lee-ThinkPad-A485:~/Documents/babylon/xsel-src$ sudo apt-get source xsel
lee@lee-ThinkPad-A485:~/Documents/babylon/xsel-src$ ls
xsel-1.2.0+git9bfc13d.20180109
xsel_1.2.0+git9bfc13d.20180109-3.debian.tar.xz
xsel_1.2.0+git9bfc13d.20180109-3.dsc
xsel_1.2.0+git9bfc13d.20180109.orig.tar.gz

```


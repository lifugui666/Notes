# 在linux下如何查找文件？

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


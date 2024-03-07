如果需要编译一段C代码，很不幸的是这段C代码又引用了很多非标准库的头文件，难道需要把这些头文件挨个编译一下吗...这样每次编译简直太累了；makefile解决了这个问题；

## 例子

如果main.c 应用了头文件a.h和b.h，按照手动编译链接的方法，过程如下

```bash
gcc -c main.c
gcc -c a.c
gcc -c b.c
gcc main.o a.o b.o
```

使用makefile的方法：

在该路径下建立一个叫做makefile或者Makefile的文件，

```bash
vim makefile
main : main.o a.o b.o
		gcc -o main main.o a.o b.o
main.o : main.c
		gcc -c main.c
a.o : a.c
		gcc -c a.c
b.o : b.c
		gcc -c b.c
```

然后在路径下执行make命令即可

## makefile的格式

```bash
结果文件 : 生成结果文件需要的文件
		生成结果文件需要执行的命令
```



## makefile的隐式规则

在看xv6系统的makefile时，发现了一种写法

```shell
OBJS = \
  $K/entry.o \
  $K/start.o \
  # ...
  $K/virtio_disk.o \
  
  # ...
  $K/kernel: $(OBJS) $K/kernel.ld $U/initcode
        $(LD) $(LDFLAGS) -T $K/kernel.ld -o $K/kernel $(OBJS)
        $(OBJDUMP) -S $K/kernel > $K/kernel.asm
        $(OBJDUMP) -t $K/kernel | sed '1,/SYMBOL TABLE/d; s/ .* / /; /^$$/d' > $K/kernel.sym
```

可见，$(OBJS)是一个依赖，但神奇的是这个makefile种并没有关于诸如`entry.o`的生成规则；但是从`make --debug=b`来看，这些`xx.o`文件确实被生成了；

实际上这里的`entry.o`是由makefile的隐式规则生成的；

如果makefile发现一个依赖不存在，而且也没有能生成依赖的规则；那么makefile就会尝试去"猜测"；
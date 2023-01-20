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
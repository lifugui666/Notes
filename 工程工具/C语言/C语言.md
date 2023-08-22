

# GCC怎么用？

## 基础应用：编译链接

```shell
# 只有一个文件
gcc test.c -o test #test就是目标文件

# 有多个文件
# 1.使用-c进行汇编
gcc -c file1.c -o file1.o
gcc -c file2.c -o file2.o
gcc -c main.c -o main.o
gcc -o main main.o file1.o file2.o
```



# 头文件怎么用？

## 头文件一般用来写如下内容：

1. 宏定义
2. 变量；**全局变量与全局函数不要定义在头文件中，这点下面会说明**（可以**声明**，但是不要定义！）
3. 结构体
4. 函数声明

## 如何防止反复定义？

```c
//test.h

#ifndef _TEST_H_
#define _TEST_H_

	//头文件的实际内容...

#endif
```

这里涉及到一个问题：可以在头文件中声明，但是**切勿在头中定义**！

例如：下面这个错误的例子

```c
//test.h
#ifndef _TEST_H_
#define _TEST_H_
char c1 = '1';
char c2 = '2';
#endif
```

```c
//test1.c
#include "test.h"
extern char c1;
void test1()
{
    printf("%c",c1);
}
```

```c
//test2.c
#include "test.h"
extern char c2;
void test2()
{
    printf("%c",c2);
}
```

```c
//main.c
#include "stdio.h"
#include "test.h"

void main()
{
    test1();
    test2();
}
```

原因在于进行在汇编阶段时，test1.c和test2.c中均包含了test.h，而此时汇编器会针对这两份test.h均做处理，由于test.h中的c1和c2已经被赋值，因此在汇编阶段这两个家伙会被保存在data段，并且会有两份；这就会导致连接器在进行链接的时候发现c1和c2在符号表中存在两份，此时有的连接器会给出warning，而有的链接器将会直接报错；




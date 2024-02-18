## exercise 1 Boot xv6 

安装工具链

```shell
lifugui@lifugui_thinkpa:~$ sudo apt-get install git build-essential gdb-multiarch qemu-system-misc gcc-riscv64-linux-gnu binutils-riscv64-linux-gnu
# 这里建议使用20.00版本后的ubuntu，从网上的资料老看有一些较老版本的ubuntu的源里缺少软件包；
# 如果出现了找不到包的情况，可以先sudo apt-get update一下
# 安装完成之后检测一下
lifugui@lifugui_thinkpa:~$ qemu-system-riscv64 --version
QEMU emulator version 6.2.0 (Debian 1:6.2+dfsg-2ubuntu6.16)
Copyright (c) 2003-2021 Fabrice Bellard and the QEMU Project developers

lifugui@lifugui_thinkpa:~$ riscv64-unknown-elf-gcc --version
riscv64-unknown-elf-gcc () 10.2.0
Copyright (C) 2020 Free Software Foundation, Inc.
This is free software; see the source for copying conditions.  There is NO
warranty; not even for MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.

# 顺带一提..我这里的 riscv64-unknown-elf-gcc 是后来用apt install装上的..不知为何按照官网上的脚本执行之后没有这个 riscv64-unknown-elf-gcc=，不过倒是有riscv64的linux编译工具...很怪
```

拉代码，这个步骤对身处国内的我而言是很困难的...

```shell
git clone git://g.csail.mit.edu/xv6-labs-2020
```

编译即可

```shell
# 进入xv6-labs-2020，执行make qemu
lifugui@lifugui_thinkpa:/mnt/d/6s081/xv6-labs-2020$ make qemu
qemu-system-riscv64 -machine virt -bios none -kernel kernel/kernel -m 128M -smp 3 -nographic -drive file=fs.img,if=none,format=raw,id=x0 -device virtio-blk-device,drive=x0,bus=virtio-mmio-bus.0
# 如果你想退出这个系统，可以按ctrl+a，然后按x
```

我的卡在了在这，可以退出qemu，但是不退出的话就会一直卡在这里，貌似很多人用ubuntu22.04都会遇到这个问题，只要重新编译安装一下qemu就行了：

```shell
sudo mkdir -p /opt/qemu-5.1.0
sudo apt-get install libglib2.0-dev libpixman-1-dev

wget https://download.qemu.org/qemu-5.1.0.tar.xz
cd qemu-5.1.0/
./configure --target-list=riscv64-softmmu
make
sudo make install
```





## exercise 2 sleep

提示：

1. Before you start coding, read Chapter 1 of the [xv6 book](https://pdos.csail.mit.edu/6.828/2020/xv6/book-riscv-rev1.pdf).
2. Look at some of the other programs in `user/` (e.g., `user/echo.c`, `user/grep.c`, and `user/rm.c`) to see how you can obtain the command-line arguments passed to a program.
3. If the user forgets to pass an argument, sleep should print an error message.
4. The command-line argument is passed as a string; you can convert it to an integer using `atoi` (see user/ulib.c).
5. Use the system call `sleep`.
6. See `kernel/sysproc.c` for the xv6 kernel code that implements the `sleep` system call (look for `sys_sleep`), `user/user.h` for the C definition of `sleep` callable from a user program, and `user/usys.S` for the assembler code that jumps from user code into the kernel for `sleep`.
7. Make sure `main` calls `exit()` in order to exit your program.
8. Add your `sleep` program to `UPROGS` in Makefile; once you've done that, `make qemu` will compile your program and you'll be able to run it from the xv6 shell.
9. Look at Kernighan and Ritchie's book *The C programming language (second edition)* (K&R) to learn about C.

注：这个代码需要从命令行中向软件中传递参数，请参照`user\echo.c`等文件，学习如何传参

代码如下：

```c
//sleep.c
#include "kernel/types.h"
#include "kernel/stat.h"
#include "user/user.h" //包含了 sleep 和 atoi 的声明

int main(int argc, char *argv[])
{
    if (argc < 1)
    {
        printf("please set sleep duration\n");
        exit(1);
    }
    
    int arg_int = atoi(argv[1]);
    sleep(arg_int);
    
    exit(0);
}
```

将这个文件放在`user`目录下面，然后修改`Makefile`文件

```makefile
#...

UPROGS=\
        $U/_cat\
        $U/_echo\
        $U/_forktest\
        $U/_grep\
        $U/_init\
        $U/_kill\
        $U/_ln\
        $U/_ls\
        $U/_mkdir\
        $U/_rm\
        $U/_sh\
        $U/_stressfs\
        $U/_usertests\
        $U/_grind\
        $U/_wc\
        $U/_zombie\
        $U/_sleep\ # 添加这一行
        
#...
```

然后make qemu启动即可；经过测试是可以的；

值得一提的是，xv6-labs-2020提供了评作业功能

```shell
lifugui@lifugui_thinkpa:/mnt/d/6s081/xv6-labs-2020$ ./grade-lab-util sleep
make: 'kernel/kernel' is up to date.
== Test sleep, no arguments == sleep, no arguments: OK (2.5s)
== Test sleep, returns == sleep, returns: OK (1.6s)
== Test sleep, makes syscall == sleep, makes syscall: OK (1.7s)
```



## exercise 3 pingpong ([easy](https://pdos.csail.mit.edu/6.828/2020/labs/guidance.html))

- Use `pipe` to create a pipe.
- Use `fork` to create a child.
- Use `read` to read from the pipe, and `write` to write to the pipe.
- Use `getpid` to find the process ID of the calling process.
- Add the program to `UPROGS` in Makefile.
- User programs on xv6 have a limited set of library functions available to them. You can see the list in `user/user.h`; the source (other than for system calls) is in `user/ulib.c`, `user/printf.c`, and `user/umalloc.c`.

这个练习是一个关于pipe的练习，下面是xv6book对pipe的描写

pipe是属于kernel的一块buffer，以一对文件描述符的形式出现，一个用来写入，一个用来读出；从pipe一端写入的数据可以从pipe的另一端读出；pipe提供了进程间通信的功能；下示例代码使用连接到管道读取端的标准输入运行程序wc

```c
// 备注：
// 在unix中，0，1，2这三个文件描述符分别代表标准输入，标准输出，错误输出；这是一个约定
int p[2];
char * argv[2];

argv[0] = "wc";
argv[1] = 0;

pipe(p);
if( fork() == 0 )//关于fork，执行之后会在这里产生一个子进程，子进程也会从这里开始执行，因此这里对父进程和子进程而言是存在分岔的；子进程会进入if分支，而父进程会进入else分支
{
    close(0);		// 子进程关闭默认的标准输入
    dup(p[0]);		// 将这个进程的标准输入定向到p[0]
    close(p[0]);	// 关闭管道的写入端
    close(p[1]);	// 关闭管道的输出端
    exec("/bin/wc"，argv);// 执行wc
}
else
{
    close(p[0]); // 关闭管道的写入端
    write(p[1],"hello world\n", 12); // 向管道的输出端写入hello world
    close(p[1]); // 关闭管道的输出端
}
```

这个程序调用了`pipe`，创建了一个新的pipe并且将写入文件描述符和读出文件描述符存在数组p中；在调用了fork之后，父进程和子进程都拥有一个和pipe相关的文件描述符；

子进程调用`close`和`dup`让文件描述符0与pipe的读取端相关联，关闭p中的文件描述符，以及调用`exec`以运行`wc`；当`wc`从其标准输入读取时，它从管道读取；

然后主进程关闭读取端，向pipe中写入hello world，然后关闭写入端；

如果没有可用的数据，那么pipe的read就会一直等待，直到有数据写入，或者关闭引用写入端的所有文件描述符；在后一种情况下，read将会返回0，就像读取文件到达eof一样；

实际上，read会一直阻塞，直到不可能再有新的数据到达；这也是子进程在执行wc之前就关闭写入端的一个重要原因，如果wc的一个文件描述符与pipe的写入端相关联，那么wc就永远看不到eof

也许pipe在功能上不比临时文件强到什么地方去，但是管道至少有四个优势：

1. 管道会自动回收，如果使用临时文件，那么你就要在用完了之后手动删除；
2. 管道可以传递任意长度的数据，如果使用临时文件，就要确保有足够的磁盘空间；
3. 管道允许并行执行，临时文件则不可以，如果使用临时文件，必须在下一个进程使用文件之前关闭当前文件；
4. 如果你要实现进程间通信，那么pipe的阻塞式读写比临时文件的非阻塞式读写要更高效；

```c
// 这是网上抄到的答案
# include "kernel/types.h"
# include "kernel/stat.h"
# include "user/user.h"

int main()
{
        int p1[2];
        int p2[2];
        char buf[1];
        int childpid, parentpid;
        int pid;

        pipe(p1);
        pipe(p2);

        pid = fork();
        if( pid == 0 )//子进程分支
        {
                close(p1[1]);//关闭pipe1的输出
                close(p2[0]);//关闭pipe2的输入

                childpid = getpid();
                read(p1[0], buf, 1);
                close(p2[0]);
                fprintf(1, "%d: received ping\n", childpid);

                write(p2[1], "x", 1);
                close(p2[1]);
        }
        else
        {
                close(p1[0]);
                close(p2[1]);

                parentpid = getpid();
                write(p1[1],"x",1);
                close(p1[1]);

                read(p2[0], buf, 1);
                close(p2[0]);
                fprintf(1,"%d: received pong\n", parentpid);
        }
        exit(0);
}
```

整理一下pipe的思路...

1. 匿名管道应用场景：匿名pipe时常用在有亲属关系的进程中；
2. 使用`pipe(p)`创建的管道，p[0]是read end，p[1]是write end；
3. pipe是半双工工作的（即：pipe可以向两个方向传递数据，但是不能同时传输）
4. **如果没有任何进程引用pipe的write end，但是仍旧有进程尝试从pipe中read，那么read将会返回0，就像文件到达尾端一样；**
5. 如果pipe的write end有被引用，但是持有write end的进程却没有向pipe中写入datas，那么，当pipe中没有东西却还要调用read时，read会进入阻塞状态；
6. 如果一直向管道里写，管道满了还尝试调用write，那么会阻塞，直到pipe中有空闲可以被继续写入为止；

```c
// 按照我的理解写一个pingpong
# include "kernel/types.h"
# include "kernel/stat.h"
# include "user/user.h"

int main()
{
    int p[2];
    char buffer[1];
    pipe(p);
    
    if ( fork() == 0 )	//child
    {
        close(p[1]);//关闭 write end
        read(p[0], buffer, 1);
        printf("%d: received ping\n",getpid());
    }
    else				//parent
    {
        close(p[0]);//关闭 read end
        write(p[1], "x", 1);
        printf("%d: received pong\n", getpid());
    }
    
    exit(0);
}
```

有问题，输出如下

```shell
$ pingpong
3: received pong
4: re$ ceived ping
```

输出是乱序的...这是因为没有使用wait(0)

```c
// 按照我的理解写一个pingpong
# include "kernel/types.h"
# include "kernel/stat.h"
# include "user/user.h"

int main()
{
    int p[2];
    char buffer[1];

    pipe(p);

    if ( fork() == 0 )  //child
    {
        //close(p[1]);//关闭 write end
        read(p[0], buffer, 1);
        printf("%d: received ping\n",getpid());
        close(p[0]);
        write(p[1],"x",1);
        exit(0);
    }
    else                                //parent
    {
        //close(p[0]);//关闭 read end
        write(p[1], "x", 1);
        wait(0);// 这里使用了wait，只有当子进程结束之后，主进程才会继续向下执行
        read(p[0],buffer,1);
        printf("%d: received pong\n", getpid());
    }
    exit(0);
}
```



## exercise 4 primes

Write a concurrent version of prime sieve using pipes. This idea is due to Doug McIlroy, inventor of Unix pipes. The picture halfway down [this page](http://swtch.com/~rsc/thread/) and the surrounding text explain how to do it. Your solution should be in the file `user/primes.c`.

这个题目要求输出2到35的素数，但是要用素数筛的方式实现；素数筛的意思是如下：

例如要求2-35之间的素数，遍历2-35，遍历到2的时候，就删除2-35之内所有2的倍数，遍历到3的时候就删除2-35之间所有3的倍数；https://swtch.com/~rsc/thread/这个页面解释了这个算法的流程；这是一种filter-and-pipeline的方法；

除此之外，我们还需要用到递归的思想，即第一个进程执行完成之后，等待它的子进程返回；同样，子进程也要等到子进程的子进程返回，直到有一个进程没有子进程了，整个程序才开始真正的返回；

这里有一个关于fork的问题：

```c
int main()
{
    for(int i = 0; i < 3; i++)
    {
        fork();
    }
}
// 这段代码会创建2^3个进程，而非创建3个
```

因此，我们不能在main的循环里fork，循环只能负责给进程喂数；

代码如下：

```c
# include "kernel/types.h"
# include "kernel/stat.h"
# include "user/user.h"

# define READ 0
# define WRITE 1

void filter(int * pipe_left)// 这个函数需要从pipe_left中读取内容
{
        close(pipe_left[WRITE]);//进入filter就关闭left pipe的write end，否则接下来的read有可能会被阻塞
        int prime;
        if( read(pipe_left[READ], &prime, sizeof(prime) ) == 0 )
        {
                exit(0);
        }
        printf("prime %d\n", prime);

        int pipe_right[2];
        pipe(pipe_right);

        if( fork() == 0 )       // 子进程
        {
                filter(pipe_right);
                exit(0);
        }
        else                    //父进程
        {
                close(pipe_right[READ]);//对于right pipe，无需使用read end
                // 删除prime的倍数，如果不是倍数，那么就传递到pipe中
                int tmp;
                while( read(pipe_left[READ], &tmp, sizeof(tmp)) )
                {
                        if ( tmp % prime != 0 )
                        {
                                //printf("%d write %d\n", getpid(), tmp);
                                write(pipe_right[WRITE], &tmp, sizeof(tmp));

                        }
                }
                close(pipe_right[WRITE]);//一旦完成write任务，write end的引用需要关闭
                close(pipe_left[READ]);//用完left的读取端就关掉
                wait(0);
                exit(0);
        }



}

int main()
{
        //创建第一个fork

        int pipe_right[2];
        pipe(pipe_right);

        if ( fork () == 0 )//子进程
        {
                filter(pipe_right);// filter内部也会产生别的pipe
            	/*
            	note: 在子进程里，要认真处理文件描述符
            	*/
                exit(0);//如果子进程返回，那么要正确的退出
        }
        else// 父进程
        {
                close(pipe_right[READ]);//父进程无需使用read end
                for ( int i = 2; i <= 35; i++)
                        write(pipe_right[WRITE], &i, sizeof(i));
                close(pipe_right[WRITE]);//写完之后要放弃对write end的引用
                            //如果这里不放弃对write end的引用
                            //那么子进程的read函数会进入阻塞状态，无法返回
                wait(0);//父进程在此等待子进程的返回
                exit(0);
        }
}
```



## exercise 5 find ([moderate](https://pdos.csail.mit.edu/6.828/2020/labs/guidance.html))

写一个简单的unix版本的find程序，找出路径下所有的同名文件

可以参考`user\ls.c`实现

这里要注意，字符串比较，不能使用`==`，而要用strcmp

在这个练习中同样用到了递归的思想，不过这里也暴露了递归的一个小问题：如果时候递归，那么你应当小心资源问题，我在编写这个程序的时候，由于没有在递归中及时关闭文件描述符，导致过多的文件描述符被打开；

```c

#include "kernel/types.h"
#include "kernel/stat.h"
#include "user/user.h"
#include "kernel/fs.h"

/*
执行功能
这里也需要递归
题目没有要求按什么方式递归，我们选择按深度优先
*/
void find(char * path, char *target)
{
    char buf[512], *p;
    int fd;
    struct dirent de;
    struct stat st;

    if( (fd = open(path, 0)) < 0 )
    {
        fprintf(2, "find: cannot open %s\n", path);
        return;      
    }

    if ( (fstat(fd, &st)) < 0 )
    {
        fprintf(2, "find: cannot stat %s\n",path);
        close(fd);
        return;
    }

    switch (st.type)
    {

        case T_FILE:
            for( p = path + strlen(path); p >= path && *p != '/'; p-- )
            {
                //这里是为了循环，找到最后一个文件的名称的index
                //for example: /a/b/c
                //在经过这个循环处理之后，p会停在/上
            }
            p++;
            if(strcmp(p, target) == 0)
                printf("%s\n", path);
            close(fd);
            break;

        case T_DIR:
            // 当前目录是点的时候

            strcpy(buf, path);
            p = buf + strlen(buf);
            *p++ = '/';
            while( read(fd, &de, sizeof(de)) == sizeof(de) )
            {
                if(strcmp(de.name,"..") == 0 || strcmp(de.name, ".") == 0) continue;
                if(de.inum == 0) continue;
                memmove(p, de.name, DIRSIZ);
                p[DIRSIZ] = 0;

                find(buf, target);
            }

            break;
        default:
            close(fd);
            break;

            
    }

}

/*
需要两个参数：
参数1 指定查询路径
参数2 指定参数目标
*/
int main(int argc, char *argv[])
{
    /*参数检查*/
    if( argc < 2 )
    {
        printf("err: need 2 parameters\n");
        exit(1);
    }

    find(argv[1], argv[2]);

    exit(0);
}

```






























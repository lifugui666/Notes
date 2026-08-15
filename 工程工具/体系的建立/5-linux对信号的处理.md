# signal.h linux下处理

注：windows支持一小部分signal.h机制

## 前言：linux中的程序是如何发送/捕获信号的？

### 信号的产生

#### 1. 按键产生的信号

linux下，信号是异步的；

案例：使用ctrl+C终止程序就是一个信号的应用；键盘输入产生了一个硬件中断，这个中断会被内核捕获，内核将其解释为一个二类信号，内核将这个信号发送给前台进程，引起前台进程的退出；



#### 2. 调用系统函数向进程发送信号

例如kill指令：发送给任意进程，任意的信号

```c
#include <sys/types.h>
#include <signal.h>

int kill(pid_t pid, int sig);//pid是目标进程的进程号，sig是要发送的信息号
```

例如raise函数：发送给当前进程任意的信号

```c
#include <signal.h>

int raise(int sig);//此函数会向当前进程发送指定的信号
```

例如abort函数：发送给

```c
#include <stdlib.h>
void abort(void);//向当前进程发送信号6：SIGABRT；效果和执行exit一样
```

#### 3. 由软件条件产生信号

例如：alarm和SIGALRM

```c
#inlcude <unistd.h>

unsigned int alarm(unsigned int seconds);
//seconds 表示闹钟的秒数
//这个函数的返回值是：上一次设定的闹钟还余下的秒数，如果上次一闹钟没收到干扰，正确执行完毕，那么本次返回值就是0
//这个函数会在计时完成之后向当前进程发送14信号SIGALRM，该信号的默认处理方式是结束当前进程

//使用案例
int main()
{
    alarm(1);
    int count = 0;
    while (ture)
    {
        printf("程序在运行");
    }
    return 0;
}
//这个案例中，程序会持续输出"程序在运行"，在持续输出1s后alarm clock触发；程序结束；
```

#### 4. 由硬件异常产生的信号

例如：0作为除数，就会出发一个硬件错误（寄存器错误）；内核会将该错误解释为SIGFPE；代码演示如下：

```c
#include <iostream>
#include <cstdlib>
#include <signal.h>
#include <unistd.h>

void handler(int sig)
{
    std::cout << "我是收到 " << sig <<"信号才崩溃了"<< std::endl;
}

int main()
{
    signal(SIGFPE, handler);//替换SIGFPE的处理方法
    int a = 10;
    a /= 0;//这里会产生一个硬件错误，这个硬件错误将会被解释为SIGFPE
    std::cout << a << std::endl;
 
    return 0;
}
//这个程序将一直输出：我是收到8信号才崩溃了
```

因为我们替换了SIGFPE的处理方法，因此实际上程序并没有崩溃退出；硬件错误会将状态寄存器中的一些位改变，原本的SIGFPE处理方法会将状态寄存器重置，但是在我们修改了SIGFPE的处理方法后，状态寄存器一直没有得到重置，就会一直触发handler；

### 信号发送的本质

在linux下，进程被一个叫做PCB的结构体描述：PCB process ctrl block；

PCB包含：

1. pid
2. 进程状态：ready（准备好运行了，但是cpu没给时间片），running（正在运行），blocked（阻塞，等待某个事件发生而无法执行）
3. 程序计数器：用于记录下一步要执行的指令
4. 上下文数据：用于切换进程
5. 内存指针：指向操作系统的虚拟地址空间
6. 记账信息：用与记录CPU开支，内存开支等信息
7. IO信息：保存进程打开的文件信息；每一个进程都会默认的打开三个文件：1. 标准输入；2.标准输出；3.标准错误；
8. 父进程pid
9. 子进程列表
10. 信号处理器：信号处理器，本质上是一个bitmap，有64个标志位，对应了64中信号；使用`kill -l `命令就可以查看各个信号的内容；

### 信号的处理

实际上处理信号的动作我们称之为 送达 delivery；

从信号产生到信号送达之间的状态称之为 未决 pending；

进程还可以主动的选择 阻塞 某个信号 block；（阻塞某个信号之后，在没有解除阻塞之前，信号不会被处理）

信号一般情况下不是被立刻处理的，(当然也是可以被立刻处理的，但是大多数时候进程都有优先级更高的任务，信号的处理优先级就被放低了很多；)

一旦进程进入内核态，就会进行一次信号的检查，进入内核态的情况有两种：

1. 使用了系统调用函数
2. 发生了时间片的切换（实际上时间片切换也是一种系统调用；这个涉及到进程调度，不展开，总之目前linux下面，进程切换还是很频繁的，在linux下，时间片长度默认在5-800ms之间，windows的时间片在20ms，可见时间片是在ms级别上的，也不用担心这个时间太短，如果cpu频率是2Ghz，那么1ms的时间仍能保证cpu运行2M次）

总之信号的处理是在内核态中发生的过程；

当进程要从内核态切换回用户态的时候，会进行一次信号检测；检测当前进程的pending表和block表，如果pending表中对应的bit为1，block中的相对的bit为0，则表示收到了信号，会按照handler表中记录的方法进行执行（执行的方式有三种：SIG_DFL默认，SIG_IGN忽略，自定义方法，前两个都是系统调用，不用切换，自定义方法是用户定义的，需要切换到用户态执行；）

完整流程如下：

1. 运行在用户态的代码调用了系统函数，或者时间片到达  --> 切换到内核态
2. 内核态完成系统调用之后会进行一次信号检查，也就是上文所述的pending表和block表那些，如果是默认处理或者忽略处理，直接在内核态中完成处理；
3. 但是如果是用户自定义的处理，就需要切回用户态处理；用户态处理完之后再调用`sigreturn()`返回到内核态；（这里的过程是 内核 -> 用户 -> 内核，虽然处理是在用户态，但是这里的用户态其实没有拿到进程的上下文，单单只是处理这一个信号，因此无法在用户态向下执行）
4. 回到内核态还需要继续检查有没有别的信号，最后调用`sys_sigreturn`返回用户态；







## signal.h中的两个函数

### signal(int sig, void *func())函数

signal.h中只定义了两个函数：

```c
void (*signal(int sig, void (*func)(int)))(int);
//说明一下这个函数

// 中间的部分
signal(int sig, void (*func)(int))//表示函数signal有两个参数，一个是int型的sig；第二个参数是一个没有返回值的函数，并且这个函数要有一个int型的参数

// 外围部分
void (*signal(xxx)) (int)//signal的返回值是一个函数指针，这个函数没有返回值，有一个int型的参数；
```

demo：

```c
#include <iostream>
#include <cstdlib>
#include <signal.h>
#include <unistd.h>

void handler(int sig)
{
    std::cout << "我是收到 " << sig <<"信号才崩溃了"<< std::endl;
}

int main()
{
    signal(SIGFPE, handler);//替换SIGFPE的处理方法
    int a = 10;
    a /= 0;//这里会产生一个硬件错误，这个硬件错误将会被解释为SIGFPE
    std::cout << a << std::endl;
 
    return 0;
}
//这个程序将一直输出：我是收到8信号才崩溃了
```





### int raise(int sig)函数

```c
int raise(int sig);
//向程序发送sig信号
```





## sigsetjmp 和 siglongjmp 函数

### setjmp()和longjmp()

setjmp和longjmp可以被视为加强版的goto，尽管市面上大量的教材告诉你不要使用goto，但是实际上goto可以让代码变的很灵活；

goto只能在函数内使用，我们无法在一个函数内goto到另一个函数内；但是setjmp和longjmp可以完成函数间的转跳；

```c
#incldue <stdio.h>
#include <setjmp.h>

jmp_buf env;// 这个env应当为全局变量

void process()
{
    int result = 1;
    longjmp(env, 1);
}

void main()
{
    char c;
    //while(true)
    {
        switch(setjmp(env))
        {
            case 0:
                printf("初始化转跳点");
                break;
            case 1:
                printf("完成转跳");
                break;
        }
        process();
    }
}

//////--------------------------------------------------
//这段代码我注释掉了循环，但是实际执行的时候还是不断输出“完成转跳”
//1. 第一次执行setjmp的时候，setjmp会返回0，此时输出“初始化转跳点”（setjmp初始化的时候会输出0）
//2. 程序继续执行，进入到了process()函数，这个函数内完成了一次转跳，这次转跳回到了seitch(setjmp(env))这句代码；但是这一次这个setjmp函数会返回1（此时返回值也就是我们longjmp的第二个参数）
//3. 循环往复...
```

这两个函数可以提供一个try catch的异常处理机制：

```c
/* FPRESET.C: This program uses signal to set up a
* routine for handling floating-point errors.
*/

＃include <stdio.h>
＃include <signal.h>
＃include <setjmp.h>
＃include <stdlib.h>
＃include <float.h>
＃include <math.h>
＃include <string.h>

jmp_buf mark; /* Address for long jump to jump to */
int fperr; /* Global error number */

void __cdecl fphandler( int sig, int num ); /* Prototypes */
void fpcheck( void );

void main( void )
{
	double n1, n2, r;
    int jmpret;
    /* 取消所有对浮点型异常的遮罩. */
    _control87( 0, _MCW_EM );
    /* Set up floating-point error handler. The compiler
    * will generate a warning because it expects
    * signal-handling functions to take only one argument.
    */
    if( signal( SIGFPE, fphandler ) == SIG_ERR )
    {
        fprintf( stderr, "Couldn't set SIGFPE/n" );
        abort(); 
    }

    /* Save stack environment for return in case of error. First
    * time through, jmpret is 0, so true conditional is executed.
    * If an error occurs, jmpret will be set to -1 and false
    * conditional will be executed.
    */

    // 注意，下面这条语句的作用是，保存程序当前运行的状态
    jmpret = setjmp( mark );
    if( jmpret == 0 )//作用就是try，第一次执行的时候jmpret一定是0，会尝试的执行if中的代码，如果没有发生异常就会正常执行下去
    {
        printf( "Test for invalid operation - " );
        printf( "enter two numbers: " );
        scanf( "%lf %lf", &n1, &n2 );

        // 注意，下面这条语句可能出现异常，
        // 如果从终端输入的第2个变量是0值的话
        r = n1 / n2;
        // 如果上一句代码出现err，那么就无法到达printf函数
        printf( "/n/n%4.3g / %4.3g = %4.3g/n", n1, n2, r );

        r = n1 * n2;
        //同上
        printf( "/n/n%4.3g * %4.3g = %4.3g/n", n1, n2, r );
    }
    else//如果if中的代码出现了异常，那么就会进入到else分支，执行fpcheck，相当于check
        fpcheck();
}
/* fphandler handles SIGFPE (floating-point error) interrupt. Note
* that this prototype accepts two arguments and that the
* prototype for signal in the run-time library expects a signal
* handler to have only one argument.
*
* The second argument in this signal handler allows processing of
* _FPE_INVALID, _FPE_OVERFLOW, _FPE_UNDERFLOW, and
* _FPE_ZERODIVIDE, all of which are Microsoft-specific symbols
* that augment the information provided by SIGFPE. The compiler
* will generate a warning, which is harmless and expected.

*/
void fphandler( int sig, int num )
{
    /* Set global for outside check since we don't want
    * to do I/O in the handler.
    */
    fperr = num;
    /* Initialize floating-point package. */
    _fpreset();
    /* Restore calling environment and jump back to setjmp. Return
    * -1 so that setjmp will return false for conditional test.
    */
    // 注意，下面这条语句的作用是，恢复先前setjmp所保存的程序状态
    longjmp( mark, -1 );
}

void fpcheck( void )
{
    char fpstr[30];
    switch( fperr )
    {
        case _FPE_INVALID:
        strcpy( fpstr, "Invalid number" );
        break;
        case _FPE_OVERFLOW:
        strcpy( fpstr, "Overflow" );

        break;
        case _FPE_UNDERFLOW:
        strcpy( fpstr, "Underflow" );
        break;
        case _FPE_ZERODIVIDE:
        strcpy( fpstr, "Divide by zero" );
        break;
        default:
        strcpy( fpstr, "Other floating point error" );
        break;
    }
    printf( "Error %d: %s/n", fperr, fpstr );
}
```





### longjmp对各种变量的影响

使用longjmp返回setjmp的存档点之后，环境真的和最初存档的时候一模一样吗？

```c
#include<stdio.h>
#include<stdlib.h>
#include<setjmp.h>
 
static void f1(int, int, int, int);
static void f2(void);
static jmp_buf jmpbuffer;
static int globval;
 
int main(void)
{
        int             autoval;
        register int    regival;
        volatile int    volaval;
        static int      statval;
 
        globval = 1; autoval = 2; regival = 3; volaval = 4; statval = 5;
 
        if(setjmp(jmpbuffer)!=0) /*  此处setjmp的返回值0，通过调用longjmp返回值改变为1(通过gdb调试得出的结果)  */
        {
                printf("after longjmp:\n");
                printf("globval=%d,autoval=%d,regival=%d,volaval=%d,statval=%d\n",globval,autoval,regival,volaval,statval);
                exit(0);
        }
        /*
         *Change variables after setjmp,but before longjmp.
         */
        globval = 95; autoval = 96; regival = 97; volaval = 98; statval = 99;
 
        f1(autoval,regival,volaval,statval); /*  never returns  */
        exit(0);
}
 
static void f1(int i,int j,int k, int l)
{
        printf("in f1():\n");
        printf("globval=%d,autoval=%d,regival=%d,volaval=%d,statval=%d\n",globval,i,j,k,l);
        f2();
}
 
static void f2(void)
{
        longjmp(jmpbuffer,1);
}
```

执行结果如下：

```shell
lee@lee-ThinkPad-A485:/tmp$ ./test 
in f1():
globval=95,autoval=96,regival=97,volaval=98,statval=99
after longjmp:
globval=95,autoval=96,regival=3,volaval=98,statval=99

```

大部分变量居然都发生了变化，只有register关键字修饰的变量没有变；这是需要注意的地方；

同时，切忌使用setjmp和longjmp做流程控制，这两者最好只用来做异常捕获，也不要尝试使用这两个函数让已经发生异常的程序继续运行下去，这会造成无法预测的情况；

### sigsetjmp和siglongjmp

sigsetjmp和siglongjmp的作用和setjmp他们几乎一模一样；

但是sig系列的这两个函数可以保留被阻塞的信号；

总之在进信号处理的时候要用这两个函数

```c
#include <stdio.h>
#include <stdlib.h>
#include <stdlib.h>
#include <setjmp.h>
#include <signal.h>
/**
 * 信号处理函数
 */
void sigdel(int signo) {
    //do nothing
}

int main(int argc, char *argv[])
{
    jmp_buf buf;
    sigset_t newmask, oldmask, pendmask;
    sigemptyset(&newmask);
    sigaddset($newmask, SIGQUIT);
    signal(SIGQUIT, sigdel);
    //阻塞SIGQUIT
    sigprocmask(SIG_BLOCK, &newmask, &oldmask);
    if (setjmp(buf) != 0) {  //实际上执行到这里之前，我们发送了一个sigquit信号，但是这个信号被block了
        sigpending(&pendmask);//这里我们尝试送达信号
        if (sigismember(&pendmask, SIGQUIT)) {//如果被block的信号送到了，就会进入if分支
            puts("block signal exist");
        } else {//如果没有送到就会进入slse分支
            puts("block signal not exist");
        }
    }
    sleep(8);//这期间 ctrl+\ 发送SIGQUIT
    longjmp(buf, 1);
    return 0;
}
//由于setjmp 不会保留被阻塞的信号 所以输出
"block signal not exist"
```

使用sigsetjmp和siglongjmp

```c
#include <stdio.h>
#include <stdlib.h>
#include <stdlib.h>
#include <setjmp.h>
#include <signal.h>
/**
 * 信号处理函数
 */
void sigdel(int signo) {
    //do nothing
}

int main(int argc, char *argv[])
{
    jmp_buf buf;
    sigset_t newmask, oldmask, pendmask;
    sigemptyset(&newmask);
    sigaddset($newmask, SIGQUIT);
    signal(SIGQUIT, sigdel);
    //阻塞SIGQUIT
    sigprocmask(SIG_BLOCK, &newmask, &oldmask);
    if (sigsetjmp(buf, 1) != 0) {
        sigpending(&pendmask);
        if (sigismember(&pendmask, SIGQUIT)) {
            puts("block signal exist");
        } else {
            puts("block signal not exist");
        }
    }
    sleep(8);//这期间 ctrl+\ 发送SIGQUIT
    siglongjmp(buf, 1);
    return 0;
}
//由于sigsetjmp当第二个参数大于0的时候会保留被阻塞的信号，等于0功能和setjmp一样。所以以上代码输出
"block signal exist"

//这个代码和上面那个除了使用了不同的set/long之外，都是一样的；但是这个程序中，siglongjmp明显保存了被blokc的sigquit信号；
```




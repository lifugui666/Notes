



# C语言常见问题

需要特别指出的是，C语言在

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

这里几乎不用考虑头文件的问题，大都数情况下，只要头文件include的路径没有问题就不会产生错误

# 头文件怎么用？

## 头文件生效的逻辑/include的规则

编译的过程：预编译-汇编-链接-可执行文件

头文件在预编译的过程中会被整个移入.c文件中；这也是不允许在.h文件中初始化变量和需要防止重复包含的原因；

C语言中有两种include用法

```c
#include <>
//使用<>包含的头文件，编译器会去默认的路径下寻找头文件
//在linux下，默认的路径有： /usr/include/  /usr/local/include

#include ""
//使用""包含的头文件，会优先从当前目录下开始寻找
```



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



# 文件输入输出

```c
// 打开文件
FILE *fopen( const char *filename, const char *mode );
//其中mode有6种
// r 打开一个已有的文件，允许读取
// w 打开一个文件，允许写入文件；如果文件不存在，创建一个新文件；w模式会覆盖已有内容
// a 以追加模式写入文件；如果文件不存在就创建一个新文件；
// r+ 同上，允许读写
// w+ 同上，允许读写
// a+ 同上，允许读写

// 读文件
int fgetc( FILE *fp);//读取第一个字符
char * fgets(char *buf, int n, FILE *fp);//读取n-1个字符，途中遇到回车换行结束，并且会给结果自动加上'\0'
size_t fread( void *buffer, size_t size, size_t count, FILE *cp );//buffer是被读出的数据的缓冲区，size是读取数据的字节的大小，nmemb表示读写的次数，fp是文件指针；返回值是读取的字节数




// 写文件
int fputc(int c ,FILE *fp);
int fputs(const char *s, FILE *fp);
size_t fwrite(const void *ptr, size_t size, size_t nmemb, FILE *fp)；//ptr是写入内容的指针，size是要写的内容的基本单位的大小，nmemb是要写出的基本单元的个数，fp是文件指针；返回值是实际写到文件中的基本单元的个数；


// 关闭文件
int fclose(FILE *fp);


//例子
#include<stdio.h>
#include<string.h>
int main()
{
        char *buf = "Hello Word";             
        char readbuf[1024] = {'\0'};
 
        FILE *ptr = NULL;
 
        ptr = fopen("./bo.txt","w+");    //打开文件bo.txt,可读可写的方式
 
        fwrite(buf,sizeof(char),strlen(buf),ptr);   //将buf的数据写入文件
 
        fseek(ptr,0,SEEK_SET);      //将文件读写指针偏移到文件头
 
        fread(readbuf,sizeof(char),strlen(buf),ptr);  //将文件的内容读取到readbuf
        fclose(ptr);    //关闭文件
 
        puts(readbuf);  //将文件读取的内容打印出来
 
        return 0;
}
```

在linux中，这三个函数可以用open，read，write来替代，但要注意，open等函数实际上是unix标准的函数；而fopen等函数是C语言的标准函数；因此fopen等函数的移植性好；同时要注意open系列函数是没有缓冲的，而fopen有缓冲；

# 字符串长度strlen

这里容易产生错误的地方在于strlen和sizeof的使用；

strlen找'\0'；

sizeof则会明确的返回占用的内存字节数量；

```c
#include <stdio.h>

char arr1[] = "abcdef";
printf("%d", sizeof(arr1));//输出7
printf("%d", strlen(arr1));//输出6
//注意： 字符串实际上是以'\0'结尾的；因此在内存中，arr1是“abcdef'\0'”,占用7字节，使用sizeof会输出7；但是strlen不会将‘\0’算上；

char arr2 * = "abcdef";
printf("%d", sizeof(arr2));//输出4
printf("%d", strlen(arr2));//输出6
//注意： 数组和指针并不完全等价，尤其是在使用sizeof的时候，sizeof数组返回的是数组占用的字节数，但是sizeof指针返回的是指针的长度；

int arr3[] = {1,2,3,4,5,6};
printf("%d", sizeof(arr3));//输出24
printf("%d", strlen(arr3));//报错
//注意： {1，2，3，4，5，6}，其中每个数字都是一个int，一个4 byte，因此总共占用24byte；strlen的参数必须是一个char *，因此会报错；这里要注意一下，int 1和char 1不一样，int的1是4byte，char的1是1byte；

char arr4[] = {'a','b','c','d','e','f'};
printf("%d", sizeof(arr4));//输出24
printf("%d", strlen(arr4));//不确定
//注意： arr4在某种意义上说也是字符串，但是strlen无法处理这个形式的字符串

char arr5[3][] = {'a','b','c','d'};
printf("%d", sizeof(arr4));//输出6，因为是二位数组，虽然只包含四个内容，但是还有两个空的位置；
printf("%d", strlen(arr4));//输出4，因为strlen只找'\0',strlen找到'\0'就会停止执行，返回结果；
```







# cJSON

C语言本身没有json解析功能，我们需要借助一些库；这里我们选择cJSON

https://github.com/DaveGamble/cJSON

这个项目中有cJSON.h和cJSON.c两个文件，只需要将这两个文件加入你的项目即可；

```c
/* The cJSON structure: */
typedef struct cJSON
{
    /* next/prev allow you to walk array/object chains. Alternatively, use GetArraySize/GetArrayItem/GetObjectItem */
    struct cJSON *next;
    struct cJSON *prev;
    /* An array or object item will have a child pointer pointing to a chain of the items in the array/object. */
    struct cJSON *child;

    /* The type of the item, as above. */
    int type;

    /* The item's string, if type==cJSON_String  and type == cJSON_Raw */
    char *valuestring;
    /* writing to valueint is DEPRECATED, use cJSON_SetNumberValue instead */
    int valueint;
    /* The item's number, if type==cJSON_Number */
    double valuedouble;

    /* The item's name string, if this item is the child of, or is in the list of subitems of an object. */
    char *string;
} cJSON;

```

## 例子

```c
#include <stdio.h>
#include "cJSON.h"

char *message = 
"{                              \
    \"name\":\"mculover666\",   \
    \"age\": 22,                \
    \"weight\": 55.5,           \
    \"address\":                \
        {                       \
            \"country\": \"China\",\
            \"zip-code\": 111111\
        },                      \
    \"skill\": [\"c\", \"Java\", \"Python\"],\
    \"student\": false          \
}";

int main(void)
{
    cJSON* cjson_test = NULL;
    cJSON* cjson_name = NULL;
    cJSON* cjson_age = NULL;
    cJSON* cjson_weight = NULL;
    cJSON* cjson_address = NULL;
    cJSON* cjson_address_country = NULL;
    cJSON* cjson_address_zipcode = NULL;
    cJSON* cjson_skill = NULL;
    cJSON* cjson_student = NULL;
    int    skill_array_size = 0, i = 0;
    cJSON* cjson_skill_item = NULL;

    /* 解析整段JSO数据 */
    cjson_test = cJSON_Parse(message);
    if(cjson_test == NULL)
    {
        printf("parse fail.\n");
        return -1;
    }

    /* 依次根据名称提取JSON数据（键值对） */
    cjson_name = cJSON_GetObjectItem(cjson_test, "name");
    cjson_age = cJSON_GetObjectItem(cjson_test, "age");
    cjson_weight = cJSON_GetObjectItem(cjson_test, "weight");

    printf("name: %s\n", cjson_name->valuestring);
    printf("age:%d\n", cjson_age->valueint);
    printf("weight:%.1f\n", cjson_weight->valuedouble);

    /* 解析嵌套json数据 */
    cjson_address = cJSON_GetObjectItem(cjson_test, "address");
    cjson_address_country = cJSON_GetObjectItem(cjson_address, "country");
    cjson_address_zipcode = cJSON_GetObjectItem(cjson_address, "zip-code");
    printf("address-country:%s\naddress-zipcode:%d\n", cjson_address_country->valuestring, cjson_address_zipcode->valueint);

    /* 解析数组 */
    cjson_skill = cJSON_GetObjectItem(cjson_test, "skill");
    skill_array_size = cJSON_GetArraySize(cjson_skill);
    printf("skill:[");
    for(i = 0; i < skill_array_size; i++)
    {
        cjson_skill_item = cJSON_GetArrayItem(cjson_skill, i);
        printf("%s,", cjson_skill_item->valuestring);
    }
    printf("\b]\n");

    /* 解析布尔型数据 */
    cjson_student = cJSON_GetObjectItem(cjson_test, "student");
    if(cjson_student->valueint == 0)
    {
        printf("student: false\n");
    }
    else
    {
        printf("student:error\n");
    }
    
    return 0;
}

```





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





# linux下的C语言计时器

**请注意：linux并不是实时系统，因此想要实时定时器是不可能的...linux下的计时器不是绝对精确的**

```c
#include <sys/time.h>

// 通过对itimerval结构体中的变量来实现对计时器的控制
struct itimerval
  {
    /* Value to put into `it_value' when the timer expires.  */
    // 当计时器到时间的时候，it_interval的值会被放到it_value
    struct timeval it_interval;
    /* Time to the next timer expiration.  */
    // 计时器到期的时间
    struct timeval it_value;
  };

struct timeval
{
  __time_t tv_sec;		/* Seconds.  */ //
  __suseconds_t tv_usec;	/* Microseconds.  */
};

// 计时器到期之后会产生一个SIGALRM信号，我们可以使用处理信号的方式处理计时器；

//使用案例
#include <stdio.h>
#include <time.h>
#include <sys/time.h>
#include <stdlib.h>
#include <signal.h>

static int i;
void signal_handler(int signam)
{
    i++;
    printf("catch signal num is :%d\n",signam);
    printf("i = %d\n",i);
}

void settimer()
{
    struct itimerval timer;
    //设置之后，10s启动计时器；
    timer.it_value.tv_sec = 10;
    timer.it_value.tv_usec = 0;
    //每1s产生一个事件；
    timer.it_interval.tv_sec = 1;
    timer.it_interval.tv_usec = 0;

    setitimer(ITIMER_REAL,&timer,NULL);

    signal(SIGALRM,signal_handler);
}
int main()
{
    settimer();
    while (i < 20)
    {
        ;
    }

    return 0;
}


```






























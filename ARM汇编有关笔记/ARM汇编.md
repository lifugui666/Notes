# ARM汇编如何写hello world

李富贵

qq:1040734443

(随意传播，欢迎讨论)

## 背景&阅前须知

注1：**ARMv8以后的寄存器用法和ARMv7之前的寄存器用法存在差异，但是原理相同，文章内容如果没有特殊说明，都是以ARMv7版本为例**

注2：**涉及到英文材料 我会把英文原文以斜体的方式标注出来，本人英语水平有限，如有错误请多包含**（诸如entry之类的单词有时候我也不晓得要翻译成“入口”还是“条目”，因此如果有翻译错误欢迎指正）

注3：在这篇文章中，汇编语言代码中出现 "/**/"    ''@"    ";"     "//"都是注释符号



正文部分：



## 基础知识

### 区分指令集？架构？内核（微架构）？Soc？

指令集：指令集指的是一种CPU与软件之间的交流规范，本质上是对二进制机器码的格式要求；

架构：架构指的是具体的指令集；例如ARM指令集实际上有很多不一样的版本，例如ARMv7表示第七个版本，ARMv8表示第八个版本...在大多数场合，指令集和架构说的是一个东西（然而要区分 架构 和 微架构）

内核（微架构）：这里的内核指的是CPU中最核心的那一部分；一块CPU中，也不是所有的电路都能被称为内核；内核指的是架构的物理实现的那一部分电路，是CPU的核心；在ARMv8之前，内核的版本通常以ARMxx的方式命名，例如ARM7，ARM9，ARM11；ARMv8之后，ARM的内核被分为了Cortex-A，Cortex-R，Cortex-M系列；

Soc：Soc指的就是看得见摸得着的那块芯片；各个厂家在内核的基础上有增加了一些外围电路，实现不同的功能，最后生产封装，变成一块芯片；



举例：BCM2711这个SOC 是采用了Cortex-A53内核的ARM架构处理器



### ARM处理的模式

无论是x86架构还是arm架构，处理器在处理不同类型的任务时，会使用不同的模式；例如处理器在处理用户程序的时候，会使用"用户模式"，这种模式权限很低，处理器不能调动屏幕一类的硬件外设；如果需要调用外设硬件，需要使用权限更高的模式；针对不同的使用场景，ARM划分出了不同的处理模式；

最常见的说法是ARM处理有7种模式，早期的ARM处理器确实是这样，但随着ARM指令集版本的不同，处理器的工作模式也在发生着变化；根据官方文档`ARM Cortex-A Series Programmer's Guide for ARMv8-A`中的描述，从ARMv7开始，处理器拥有9种工作模式

| Mode            | Function                                                     | 特权等级 |
| --------------- | ------------------------------------------------------------ | -------- |
| User (USR)      | 非特权模式，大多数应用运行于该模式下                         | PL0      |
| FIQ(快速中断）  | FIQ中断异常时进入                                            | PL1      |
| IRQ(一般中断）  | 在IRQ中断异常时进入                                          | PL1      |
| Supervisor(SVC) | 在reset或者调用svc指令的时候进入                             | PL1      |
| Monitor (MON)   | 当调用SMC（Secure Monitor Call）指令或者当进程被配置为安全处理进程的时候进入；<br>这个模式提供了对“安全模式”与“非安全模式”两种状态切换的支持 | PL1      |
| Abort (ABT)     | 当发生存储访问异常时进入                                     | PL1      |
| Undef (UND)     | 当发生了未定义的指令异常时进入                               | PL1      |
| System (SYS)    | 特权模式，与用户模式分享寄存器视角                           | PL1      |
| Hyp (HYP)       | Entered by the Hypervisor Call and Hyp Trap exceptions.（这个模式与虚拟化扩展有关） | PL2      |



### 汇编指令的基本格式

所有的编程语言（包括汇编语言这种低级语言）在被执行前一定要被翻译成机器码，也就是0和1组成的序列；

对于ARM而言，汇编指令最终被执行前会被翻译成32bits的机器码（注：ARM64的机器码也是32bits的）

举个例子：

```assembly
/*假设某指令的机器码遵循以下规则*/
Opcode{cond}{s} 	Rd, 	Rn, 	op2
/*操作数{条件}{状态} 目标寄存器 源寄存器	后续操作*/
```

机器码以32个0或1的排列组成，[31:28]表示的是条件，24-21表示的是操作等等...所以如果你乐意，你甚至可以直接手搓机器码；

（在ARM的文档中我只找到了ARMv7的译码规则）

| 31-28 | 27-25 | 24-21  | 20   | 19-16 | 15-12 | 11-0 |
| ----- | ----- | ------ | ---- | ----- | ----- | ---- |
| cond  | 001   | Opcode | S    | Rn    | Rd    | op2  |

（这个译码规则将说明，为什么对于ARM而言，并不是所有的立即数都是合法的，这个问题我将会在后面学习）

注：并不是每个指令的机器码格式都完全一致，可以参照ARM官网文档 https://developer.arm.com/documentation/ddi0596/2021-12/Base-Instructions/BL--Branch-with-Link-?lang=en 这个文档中列出了ARM-A64架构的基本指令的机器码格式，同样的，也可以在官网文档找找到其他架构的机器码格式（Instruction Set Architecture文档）*这里强烈谴责ARM，文档搞得好乱捏*



### 流水线

执行一条指令，一般而言需要经过：取指，译码和执行三个步骤；

1. 取指：寻找指令的地址，并读取对应的内存中的指令

2. 译码：将指令翻译为机器码

3. 执行：处理器真正的执行代码

ARM采用了”流水线“设计：在一个时间周期内，处理器会同时进行取指，译码和执行；

**三级流水**：同时处理F-D-E（取指->译码->执行）

例：

当处理器正在执行第（n）条指令时；

与此同时，处理器也在对第（n+1）条指令进行译码；

与此同时，处理器还在对第（n+2）条指令进行取指；

如此一来，下一个时间周期可以直接对第（n+1）条指令进行执行；（因为对n+1的译码已经在上一个时间片完成了）

流水线可以实现让每一次操作都在执行指令，并为后续指令的执行做准备；

注：这也是简单指令集的优势所在，像ARM这样的简单指令集，每一个指令执行需要的周期都是一样的，所以可以严丝合缝的使用流水线；复杂指令集由于存在一些复杂指令，这些复杂指令执行起来可能需要不止一个时间片，因此无法简单的使用流水线（当然intel这些大厂也发明了可以将复杂指令拆分成多个简单指令，让复杂指令集也可以使用流水线，不过这就是另一个故事了）

**五级流水线**：

相较于三级，在同一个时钟周期内，处理器又多了两个操作：存取，保存结果到寄存器

*随着技术的发展还有双ALU流水线和超标量流水线...不过总的理念和三级流水线都是相同的，这里不作为重点进行学习*



### 分支预处理

ARM采用了流水线处理方式，这决定了当某条指令被执行时，后续指令必定已经处于被装填的状态；

但是程序往往存在复杂的跳转（例如判断语句，会产生两种不同的后续操作，而没有完成判断时，处理器并不知道要往哪一边走，此时产生了分支）；在不做分支预处理的情况下，可能出现辛辛苦苦 取指-编码的指令被废弃，需要重新 取指-编码；

分支预处理的作用在于列出下一步可能会出现的指令，真的进行到下一步的时候进行选择即可，不用重新计算，大致的思想还是用空间去换时间；现在的分支预测技术甚至会利用到缓存，建立哈希表预测，已经变成了一个复杂的东西；



### 片内寄存器和外设寄存器

我们看的ARM的文档只描述了十几个寄存器的用法；这十几个寄存器被称为片内寄存器（这就是所谓的内核的组成部分），这十几个寄存器是控制处理器进行工作的核心；

但是其他的厂家（例如三星，高通...）可以通过设计不同的外围电路，最终生产出我们通常所说的处理器（例如骁龙...），这些ARM之外的厂家设计的寄存器是用来控制外部设备的；这些寄存器的信息就要查阅处理器对应的开发手册了；



### Thumb

这个东西我不打算学习，不过需要知道一下；

Thumb是arm提供的另一种16位的指令集；Thumb指令集可以节约资源；Thumb可以和arm混合使用；ARM指令中一个标志位用于确定当前的指令是Thumb指令还是ARM指令





## 寄存器⭐

自从ARM指令集更新了第八个版本，arm就进入了64位的时代，寄存器的数量也迎来了飞跃，从原来的R0-R12的13个通用寄存器，变为了X0-X29的30个通用寄存器，同时由于进入了64位时代，新的寄存器也自然变成64位寄存器，为了和原先的32位寄存器兼容，ARMv8的每个寄存器都可以被当作32位寄存器使用；

在ARMv8以后**如果将寄存器视作64位寄存器，则用Xn的方式引用；如果将寄存器视作32位寄存器，则用Wn的方式引用 **

### 通用寄存器

注：ARMv7到ARMv8的寄存器有变化，但是这里我决定从较为简单的ARMv7寄存器开始学习；

需要指出，**当处理器处于不同的状态之下时，处理器能访问的寄存器是不同的，即使同一个寄存器在不同的处理模式下也可能担负着不同的任务**；

| USR      | Sys  | FIQ      | IRQ      | ABT      | SVC      | UND      | MON      | HYP      |
| -------- | ---- | -------- | -------- | -------- | -------- | -------- | -------- | -------- |
| R0       |      |          |          |          |          |          |          |          |
| R1       |      |          |          |          |          |          |          |          |
| R2       |      |          |          |          |          |          |          |          |
| R3       |      |          |          |          |          |          |          |          |
| R4       |      |          |          |          |          |          |          |          |
| R5       |      |          |          |          |          |          |          |          |
| R6       |      |          |          |          |          |          |          |          |
| R7       |      |          |          |          |          |          |          |          |
| R8       |      | R8_fiq   |          |          |          |          |          |          |
| R9       |      | R9_fiq   |          |          |          |          |          |          |
| R10      |      | R10_fiq  |          |          |          |          |          |          |
| R11      |      | R11_fiq  |          |          |          |          |          |          |
| R12      |      | R12_fiq  |          |          |          |          |          |          |
| R13(sp)  |      | SP_fiq   | SP_irq   | SP_abt   | SP_svc   | SP_und   | SP_mon   | SP_hyp   |
| R14(lr)  |      | LR_fiq   | LR_irq   | LR_abt   | LR_svc   | LR_und   | LR_mon   | LR_hyp   |
| R15(pc)  |      |          |          |          |          |          |          |          |
| (A/C)PSR |      |          |          |          |          |          |          |          |
|          |      | SPSR_fiq | SPSR_irq | SPSR_abt | SPSR_svc | SPSR_und | SPSR_mon | SPSR_hyp |
|          |      |          |          |          |          |          |          | ELR_hyp  |

 上图中空白的格子表示，某模式与USR共享对应的寄存器，举个例子：如果现在从USR模式进入Sys模式，那么Sys模式下的R0仍旧保存着USR模式下R0的内容；所以当发生状态切换的时候，我们应当想办法把这些共享的寄存器种的内容先保存一下，以防原始数据在其他模式下被破坏，导致切换回原来的状态后发生错误；

说明一下特殊寄存器：

### sp

sp：stack pointer 栈指针寄存器；（我们都晓得cpu是分时间片处理多个进程的，当进程切换时，sp寄存器就存着下一个进程的栈地址）

### lr

lr：link register 连接寄存器；（当发生函数调用的时候，会把当前的地址记录在lr种，完成调用，需要返回的时候就按照lr中的地址返回即可；这个功能当然可以通过通用寄存器完成，但是arm还是提供了一个专用的寄存器以提高效率）

### pc

pc：program counter 程序计数器；（每一个片选时间都会+1...这个没什么好说的，它指向哪里处理器就计算什么）

### (A/C)PSR与SPSR

APSR：应用程序状态寄存器

CPSR：当前程序状态寄存器（**ARMv8中没有CPSR，取而代之的是PSATAE，详情->ARMv8的程序状态**）

SPSR：已保存程序状态寄存器

CPSR保存当前的进程的状态，当发生进程的切换时，CPSR的内容会被保存在SPSR中，而CPSR会保存新的进程的状态；如果需要切换回去的话，只需要把SPSR中的内容重新放回CPSR中即可；

这也是USR模式没有SPSR的原因...SPSR最大的用处就是在模式切换的时候保存原来的用户模式下的进程的状态，方便还原现场；

根据ARM的文档*ARM® Cortex®-A Series Version: 1.0 Programmer’s Guide for ARMv8-A* 的4.1.5

When taking an exception, the processor state is stored in the relevant Saved Program Status Register (SPSR), in a similar way to the CPSR in ARMv7. The SPSR holds the value of PSTATE before taking an exception and is used to restore the value of PSTATE when executing an exception return. (当发生异常的时候，进程的状态将会以一种**与ARMv7中的CPSR相似的方式**被存储在SPSR中)

| 31   | 30   | 29   | 28   | 27-22 | 21   | 20   | 19-10 | 9    | 8    | 7    | 6    | 5    | 4    | 3-0    |
| ---- | ---- | ---- | ---- | ----- | ---- | ---- | ----- | ---- | ---- | ---- | ---- | ---- | ---- | ------ |
| N    | Z    | C    | V    | /     | SS   | IL   | /     | D    | A    | I    | F    | /    | M    | M[3:0] |

**N**		Negative result (N flag).负数标志位
**Z**		Zero result (Z) flag.零结果标志位
**C**		Carry out (C flag).进位/借位标志位
**V**		Overflow (V flag).溢出标志位
**SS**		Software Step. Indicates whether software step was enabled when an exception was taken.软件步进，用于指示当异常发生的时候，是否允许软件步进
**IL**		Illegal Execution State bit. Shows the value of PSTATE.IL immediately before the exception was taken.非法执行标志位
**D**		Process state Debug mask. Indicates whether debug exceptions from watchpoint,breakpoint, and software step debug events that are targeted at the Exception level the exception occurred in were masked or not.用于指示是否处于Debug模式
**A**		SError (System Error) mask bit.是否使能系统错误
**I**		IRQ mask bit.是否使能IRQ
**F**		FIQ mask bit.是否使能FIQ
**M[4]**		Execution state that the exception was taken from. A value of 0 indicates AArch64.
**M[3:0]**		Mode or Exception level that an exception was taken from.

由此可见，SPSR可以看出当异常发生的时候的进程的信息；

### 注意区分SPSR和SP

SPSR是异常发生的时候，用于保存CPSR内容的；SP是异常发生的时候，用于保存通用寄存器内容的

### ARMv8中的程序状态寄存器

v8中并没有CPSR，取而代之的是一个叫做PSTATE的东西，**PSTATE不是一个寄存器，它是一组寄存器或者说是一系列标志位的合成**

Aarch64下，PSTATE中包含以下内容

```c
type ProcState is ( 
 bits (1) N, // Negative condition flag 
 bits (1) Z, // Zero condition flag 
 bits (1) C, // Carry condition flag 
 bits (1) V, // Overflow condition flag 
 bits (1) D, // Debug mask bit [AArch64 only] 
 bits (1) A, // SError interrupt mask bit 
 bits (1) I, // IRQ mask bit 
 bits (1) F, // FIQ mask bit 
 bits (1) PAN, // Privileged Access Never Bit [v8.1] 
 bits (1) UAO, // User Access Override [v8.2] 
 bits (1) DIT, // Data Independent Timing [v8.4] 
 bits (1) TCO, // Tag Check Override [v8.5, AArch64 only] 
 bits (2) BTYPE, // Branch Type [v8.5] 
 bits (1) ZA, // Accumulation array enabled [SME] 
 bits (1) SM, // Streaming SVE mode enabled [SME] 
 bits (1) ALLINT, // Interrupt mask bit 
 bits (1) SS, // Software step bit 
 bits (1) IL, // Illegal Execution state bit 
 bits (2) EL, // Exception level 
 bits (1) nRW, // not Register Width: 0=64, 1=32 
 bits (1) SP, // Stack pointer select: 0=SP0, 1=SPx [AArch64 only] 
 bits (1) SSBS, // Speculative Store Bypass Safe 
 )
```

通过以下寄存器可以实现对PSTATE的读写

NZCV

DAIF

CurrentEL

spsel

PAN

UAO

DIT

ALLINT

SSBS

````assembly
mrs x0, nzcv	@通过这种方式可以读取pstate的nzcv部分
````



## 基础语法⭐

### 大小写？

汇编是对大小写敏感的；不要使用大小写混写的方式，全部是大写可以，全部是小写也可以

### 汇编指令的基本写法

```assembly
Opcode{cond}{s} 	Rd, 	Rn, 	op2
/*操作{条件}{S} 目标寄存器 源寄存器	后续操作*/
```

**需要强调的是，如果需要条件码或者S，那么他们将紧跟再操作码后面**

**除了CMP，CMN，TEQ，TST指令，其余的指令要后接S才能影响CPSR**

如果命令后接上了条件码，那么要根据条件判断这条指令是否要执行，如果没有接条件码，那么默认AL执行(无条件执行)；条件判断的依据是CPSR

| 条件码 | 编码 | 含义             | 条件                 |
| ------ | ---- | ---------------- | -------------------- |
| EQ     | 0000 | 相等             | Z == 1               |
| NE     | 0001 | 不相等           | Z == 0               |
| CS/HS  | 0010 | 无符号大于等于   | C == 1               |
| CC/LO  | 0011 | 无符号小于       | C == 0               |
| MI     | 0100 | 负数             | N == 1               |
| PL     | 0101 | 零或正数         | N == 0               |
| VS     | 0110 | 溢出             | V == 1               |
| VC     | 0111 | 未溢出           | V == 0               |
| HI     | 1000 | 无符号大于       | C ==1 && Z == 0      |
| LS     | 1001 | 无符号小于或等于 | C == 0 &&Z == 1      |
| GE     | 1010 | 大于等于         | N == V               |
| LT     | 1011 | 小于             | N != V               |
| GT     | 1100 | 大于             | Z == 0 && (N == V)   |
| LE     | 1101 | 小于或等于       | Z == 1 \|\| (N != V) |
| AL     | 1110 | 无条件执行       | 无条件               |
| -      | 1111 | 非法条件         | -                    |



```assembly
/*举一个简单例子*/
MOV R3, #0x01 @作为flag

MOV R0, #FF
MOV R1, #FF

SUBS R0, R1 @这个指令执行之后结果为0，会将Z置1
MOVEQ R3, #0x02 @由于EQ只有在Z==1的时候执行，这里符合条件，所以会执行这条指令

/*这个程序执行完毕之后，R3中的值应当是0x02*/
```





### 立即数和非法立即数

Cortex-A系列对立即数是有限制的，由于指令编码之后只能给立即数留下12位用于存放立即数；

首先，我们自然是不可能用2^12种组合表达全部的2^32的数字；为了保证尽量覆盖2^32范围，ARM使用8位表示数，用另外4位表示对这个数进行循环右移；（**所谓循环右移，就是对一个32位的数来说，左移4位与右移28位相同；右移溢出的数据会被填充到左侧**）

因此ARM中的立即数是通过 对8位数右移循环 得到的，**但是还有一个问题**：4位表示的 位移循环 的只能表示16种，但是我们的目标是实现32种循环；因此arm又规定，**只能进行偶数位移**；

这样一来，我们就可以用12位较为全面的覆盖0-2^32，不过仍旧有一部分数字无法使用这个体系表示，ARM就把这些无法表示的数字定义为，非法立即数

### 寻址方式

常见的有7种寻址方式（印象中貌似在微机原理里学过捏）

#### 立即数寻

```assembly
;使用立即数寻址
ADD R0, R0, #0x3F
```

#### 寄存器寻址

```assembly
ADD R0, R1, R2
```

#### 寄存器间接寻址

```assembly
LDR R0, [R1] @ LDR可以将内存中的内容加载到寄存器中
@同时注意[]的写法，如果R1中的值是0x00000103，那么[R1]的含义是，地址为0x00000103的内存中 保存的值

STR R0, [R1] @ STR是将R0中的值放到R1表示的内存地中去
```

#### 寄存器位移寻址

```assembly
ADD R3, R2, R1, LSL #2
@ 表示将R1左移两位，然后加上R2，赋值给R3
```

#### 基地址寻址

```assembly
LDR R0, [R1, #4]
@ 表示将R1中的值加上4 所表示的内存地址中的内容，加载到R0中
LDR R0, [R1], #4
@ 表示R1中的值 指向的内存地址 中的值加4，加载到R0中
@ 例如R1中的值0x00000103，上述指令表示将内存地址0x00000107中的内容加载到R0
LDR R0, [R1, R2]
@ R1中的值+R2中的值 指向的内存地址中的数据 加载到R0中
```

#### 多寄存器寻址

```assembly
LDMIA R0!, {R1, R2, R3, R4}
@ LDM表示多寄存器存取
@ IA表示每次传送后地址，指针自动累加
@ ! 表示自动调节R0中的指针
@ 上述指令表示，将R0表示的内存地址中的数据加载到R1，
@ 将R0表示的内存地址+4 中的数据加载到R2中
@ 将R0表示的内存地址+8 中的数据加载到R3中...以此类推
@ 注： 为什么是+4？ 因为地址+4 表示跨越一个word（即32bit）
```

#### 相对寻址

````assembly
BL NEXT
MOV PC, LR
````

### ARM堆栈

| 高地址 |

| ........    |

| 低地址 |

**堆栈是先进后出的数据结构**；

堆栈的指针指向最上面一个地址，我们称之为满堆栈；

当堆栈指针指向最上面一个地址的上一个地址，我们称之为空堆栈

如果压栈时，第一个元素压到高地址，后续元素逐渐向低地址压入，称之为递增堆栈； 	反之称为递减堆栈

IA：每次传输后，地址+4

IB：每次传送前，地址+4

DA：每次传送后，地址-4

DB：每次传送前，地址-4

EA：空递减堆栈

FD：满递减堆栈

ED：空递增堆栈

FA：满递增堆栈

批量操作寄存器的时候会用到这些东西



### 数据操作（ALU操作）

#### MOV与MVN（赋值操作）

```assembly
MOV Rd, Op2
@将Op2传送到Rd中
MVN Rd， Op2
@将Op2取反传送到Rd，例如Op2=0x0F，执行玩之后Rd中的内容会变成OxF0
```



#### MOVK，MOVZ，MOVN

````assembly
@ movk 可以将一个立即数移动到寄存器中，同时保持其他的位不变
@ 例如
mov x0, #0xaaaa	@此时x0中的值是0x0000_0000_0000_aaaa
movk x0, #0xbbbbb, lsl #16 @此时x0中的值是0x0000_0000_bbbb_aaaa，可见并没有影响到之前移入x0的0xaaaa
````

```assembly
@ movz 可以将16bits数移动到寄存器中，可以对这个数左移0位，16位，32位或者48位；移动后会将立即数之外的位都清零
@ 例
mov x0 ,#0xffffffffffffffff
movz x0, #0x1111, lsl 16 @ 此时x0中的值：0x0000_0000_1111_0000
```

````assembly
@ movn 类似于mvn，将值移动到指定的寄存器中，然后取反
````

这几个指令对于重定位有很大的用处，movz和movk可以一部分一部分的将数据送到一个64bits的寄存器中，解决了arm指令只有32bits，无法一次性携带长达64bits数据的问题；



#### ADD与ADC（加法）

```assembly
ADD R0, R0, #4
@将R0中内容+4，存入R0中
ADDS R0, R0, #4
@ADDS除了会执行ADD的内容，还会产生进位标识符，如果R0+4会产生进位，那么ADDS会将进位的状态记录在CPSR中
ADC R0, R0, #4
@将R0中的内容+4+进位，存入R0中；进位是哪里来的？是从CPSR中取到的
```

#### SUB与SUC与RSB（减法）

用法与ADD与ADC几乎完全一样

```assembly
RSB Rd, Rn，Op2
@表示用Op2-Rn
```

#### MUL与MLA与UMULL与UMLAL与SMULL与SMLAL（乘法）

```assembly
MUL Rd, Rm, Rs
@ MUL表示乘法，Rd=Rm*Rs；
@ 注1:**MUL不能使用立即数，必须存入寄存器才能相乘**
@ 注2：如果Rm*Rs的结果大于32位，那么高位会被截断
MLA Rd,Rm,Rs,Rn
@ MLA表示累加乘法；Rd=Rm*Rs+Rn
UMULL RdLo, RdHi, Rm, Rs
@ 64位无符号乘法，使用两个32位寄存器承载运算结果
UMLAL RdLo, RdHi, Rm, Rs
@ 64位无符号累加乘法 (RdLo,RdHi) = Rm * Rs + (RdLo,RdHi)

@ SMULL与SMLAL是有符号版本
```

#### AND与EOR与ORR与BIC（逻辑运算）

````assembly
AND Rd, Rn, Op2
@ 逻辑与
EOR Rd, Rn, Op2
@ 逻辑异或
ORR Rd, Rn, Op2
@ 逻辑或
BIC Rd, Rn, Op2
@ 逻辑非
````

#### CMP与CMN与TEQ与TST（逻辑比较）

````assembly
CMP Rn,  Op2
@ 这个操作产生的结果会存入CPSR中的S标识符中
@ 这四个操作的特点在于，他们的运算结果会存入CPSR中； 	
````



#### 内存操作指令LDR

```assembly
LDR Rn Addr	@将Addr中的内容加载到Rn
@ 这里需要注意，内存的最小单位是Byte，1Byte=8bit；但是32位的ARMv7的LDR是以word为单位的，1 word = 4 byte = 32bit
@ 注2：LDR的第二个操作数不能是立即数，需要用另一个寄存器套一下
```

特别注意一下 **以字为单位**：

| 地址        | 0    | 1    | 2    | 3    | 4    |
| ----------- | ---- | ---- | ---- | ---- | ---- |
| 0x0000 0000 | 00   | 11   | 22   | 33   | 44   |

````assembly
LDR R0 [R1, #0x00]
@ 这个指令的结果是R0中的内容：0x33221100（33位于前面是因为“小端模式”的关系）

LDR R0, [R1, #0x01]
@ 这个的结果是：0x00332211 而非 0x44332211
@ 这就体现了 字为单位，0x0000_0000 0x0000_0001 0x0000_0002 0x0000_0003 这四个byte是一个字，无论对 0x00 0x01 0x02还是0x03执行LDR，结果都不会和0x0000_0004有关系；
@ 当LDR的Addr选择0x01时，R0中的值从0x01开始循环填充
````



#### STR,STP与LDRB,STRB,LDRH,STRH等

````assembly

STR Rn, Addr
@ 类似于LDR，STR是将Rn的值存储到Addr中，同样需要注意，小端模式和字为单位
STP r0, r1, Addr
@ STP是将一对寄存器中的值存入Addr指向的内存

LDRB Rn, Addr
@ 这个指令类似于LDR，但是LDRB是以Byte为单位的
STRB Rn, Addr
@ 同上

LDRH 
@ 以半字(16bit)为单位
STRH
@ 同上

LDRT
STRT
@ 用户模式下操作内存

LDRS
STRS
@ 带符号的操作，会影响CPSR
````



#### LDM与STM

````assembly
@ LDM这个指令之前在多寄存器寻址中见过
@ 首先LDM不会被单独使用，LDM后面一定会跟一个地址操作模式，例如IA
@ Rd被称作基址寄存器，R0中的内容指向存储器
@ 第二个参数是一系列寄存器，可以写{R1-R5}，也可以分开写，依次指定
LDMIA Rd!,{Ra-Rb}

@例：
LDMIA R0, {R1-R2}
@ 表示以R0中的值指向的地址为基地址，将基地址中的内容传送到R1中；
@ 然后R0 = R0 + 4，再将+4后的地址中的内容传送到R2中；
@ 关于"!"；如果Rd加了！，表示最后将经过递增(+4)的基地址存入Rd，如果不加！，执行完成后Rd中的值不变

@ 注：Rd不能用PC寄存器（R15）

STMIA R0, {R1-R2}
@ 表示将R1的值存入R0指向的内存，将R2的值存入R0+4指向的内存；用法和LDMIA相同，倒过来而已；
````

地址模式：

IA：每次传输后，地址+4

IB：每次传送前，地址+4

DA：每次传送后，地址-4

DB：每次传送前，地址-4

EA：空递减堆栈

FD：满递减堆栈

ED：空递增堆栈

FA：满递增堆栈



### 实现跳转

#### 使用PC寄存器实现跳转

````assembly
MOV LR, PC
MOV PC, [R1] 
@ 这种方式利用lr寄存器，先将最原始的pc存起来，然后直接更改pc完成转跳；当转跳过去的任务完成之后，再利用lr寄存器调回来；
````

#### 使用B直接进行关于label的跳转

````assembly
@实际上B和BL跳转是最常见的...
_START:
	B _HELLO
	
_HELLO:
	@......
````

但是B跳转时有限制的，它只能在上下32Byte的范围进行跳转；如果label离得太远就不能跳转了；

```assembly
@ 使用BL跳转
_START:
	BL _HELLO
	@......
_HELLO:
	@......
	@如果需要有条件跳转可以使用条件码,例如
	CMP R0, R1
	MOVEQ PC, LR@这样实现了，当R0==R1时跳转回去
```



### 操作状态寄存器

对状态寄存器（包括CPSR，APSR，SPSR_xxx）的操作需要用特殊的指令

#### MRS与MSR

````assembly
MRS R0, CPSR @将CPSR中的内容传送到一个通用寄存器中
MSR CPSR, R0 @将R0中的内容传送到CPSR中
MSR CPSR, #0x00000000 @将00000000写入cpsr中
````

这里需要注意的是，ARMv8中取消了CPSR这个寄存器，取而代之的是一个叫做PSTATE的东西，但是需要注意PSTATE并不是一个具体的寄存器，PSTATE是起着CPSR作用的一系列寄存器和标志位的合称；这部分内容详参本文章节： 寄存器->ARMv8中的程序状态寄存器



## MDK语法规则

如果你曾经搞过单片机，那么你对MDK一定很熟悉...这套体系是keil-MDK的伪指令；如果你需要的是单纯的arm嵌入式，看看mdk可以；如果你需要的是linux有关的内容，那就略过这部分，直接去看GNU风格的语法；

 

## 异常处理

ARM的中断源有七种：

reset:上电执行（虽然说是reset异常，但是实际上上电执行的也是reset）

data:预取指试图对非法内存单位进行操作时执行

fiq:快速中断（快速中断的优先级最高，通常用于处理高速设备的请求）

irq:通常中断（普通的中断，计算机系统中绝大部分外设都只配用这种普通的中断）

prefetch:预取指没有取到的时候执行

undef:执行过程中遇到未定义指令执行

swi:软中断指令被执行的时候执行

（上述异常的有限级别从上到下依次递减）



### 异常处理流程

如果一旦发生异常，要如何处理？

1. 硬件处理（硬件程序，被设计在电路上的）

   1. 将CPSR中的内容保存到SPSR中（如果不知道CPSR和SPSR是什么，可以了解以下ARM寄存器相关知识）

   2. CPSR的模式位将被设置成发生的异常的类型，处理器会进入相应的处理模式；如果当前异常不是FIQ中断，那么会禁止所有的IRQ中断（防止在处理中断时又进来一个IRQ中断）；如果当前异常是FIQ中断，那么会禁止FIQ中断（防止处理FIQ中断时，又来一个FIQ中断）；

   3. 保存返回地址，将发生异常的程序的下一条指令地址存入LR中（不知道LR寄存器是什么，可以去学习一下ARM寄存器）

   4. 将PC的值设置为相应的异常向量地址，跳转到异常处理程序

      （**这里涉及到异常向量表的问题，根据ARM的规定，0x0000_0000到0x0000_001C对应着7中异常处理程序的入口地址；0x0000_0000是reset异常，因此上电之后直接会进入reset异常处理；**

      **然而并不是所有的异常向量表都是这样**

      **在使用的时候，0x0000_0000~0x0000_001C这片内存区域在大多数设备上都是厂商写死在内存中的启动引导程序；因此大多数时候我们要用异常向量表还要重新映射一下地址，异常向量表是可以通过协处理器进行配置的**）

2. 异常处理（这部分就依赖于软件了**这部分CPU不会帮你做，需要你自己写程序完成**）

   1. **（保护现场）**：首先要保存被打断的程序的执行现场，所谓现场就是被打断的程序的寄存器状态，可以使用STMFD进行批量压栈（FD是满递减堆栈，从高地址向低地址压栈）

      ````assembly
      STMFD SP_excep!, {R0-R12,LR_excep}
      /*将R0-R12和LR_excep的内容存入SP_excep指向的内存中，SP_excep指向的内存自加*/
      ````

      当执行上述这段代码的时候处理器已经进入了异常处理工作模式，因此，此时要把现场放入异常处理模式下的SP寄存器里（注：不同模式下sp寄存器不通用，因此这里只能放入SP_excep）；

3. 异常返回（**这部分CPU也不会帮你做，需要自己写程序**）

   1.  按照SP_excep中记录的地址，将现场还原

   2. 将CPSR寄存器还原

   3. ``` assembly
      MOV PC, LR @跳转回被中断的程序（实际操作要比这个例子复杂一些）
      ```

注1：**因为ARM处理器流水线的存在，当异常返回的时候，不能直接使用LR寄存器中的值，需要根据异常的类型进行特殊处理**

注2：异常返回时，有两个动作必须执行；将SPSR放回到CPSR；将LR_excep的值给PC；如果这两个步骤分开执行，会产生问题，一旦CPSR给回去，那么LR_excep寄存器就无法访问，因为一旦回到USR，我们只访问USR的LR寄存器；为了应对这个问题，可以使用

``` assembly
MOVS PC, LR
```

这样，MOVS指令会将SPSR复制到CPSR，同时将LR赋值给PC；



### 软件中断异常的处理（SWI）

在用户程序中 软件中断异常 的处理是最常见的；这个异常是由用户程序自己产生的，当程序需要访问硬件的时候就要通过这个异常进行访问；

例如：如果想在屏幕上打印，就需要申请使用显示器，用户程序本身是没有使用外设的权力的，想要使用，只能使用SWI切换到内核态，这时候操作系统的内核代码就会按照用户程序的请求去帮助用户程序实现用户程序的需求；内核态是工作在特权模式下的，内核态有权访问硬件；

软件中断指令异常工作在SVC（Supervisor）下；

//todo swi如何可以调用什么系统调用？如何传参？



关于软中断号：软中断号只能从SWI 指令的机器码中获取



注：**SWI执行时，PC的值没有更新，PC仍旧指向后面第二条指令；但SWI中断产生时，处理器会将（PC - 4）存入LR_svc中，因此LR_svc直接就指向 后第一条指令，直接将其MOV到PC即可**

```assembly
MOV PC, LR_svc
```



### Undef异常处理

注：**PC寄存器处理方式同SWI**



### FIQ的处理

注：**当发生FIQ时，PC寄存器已经更新，此时PC指向后面的第三个指令，也就是指向 （当前指令地址 + 12byte）；但是FIQ中断产生的时候，处理器会将（PC - 4）存到LR_fiq中；因此LR_fiq中记录的地址是指向中断发生时 后第二条指令的；所以返回的时候，需要再减4，让PC指向 后第一条指令**

```assembly
SUBS PC, LR_fiq , #4
```



### IRQ的处理

注：**当发生IRQ时，PC寄存器已经更新，此时PC指向后面的第三个指令，也就是指向 （当前指令地址 + 12byte）；但是IRQ中断产生的时候，处理器会将（PC - 4）存到LR_irq中；因此LR_irq中记录的地址是指向中断发生时 后第二条指令的；所以返回的时候，需要再减4，让PC指向 后第一条指令**

```assembly
SUBS PC, LR_irq , #4
```



## GNU风格汇编语法⭐

很不幸，之前学习的MDK汇编伪指令并不是所有的编译器都支持...俺在树莓派上随便试了以下LCLA就没有通过...

并且从uboot来看，GNU风格的汇编语法貌似用的人更多，现在我或许需要重新学习GNU风格的汇编

### 基础语法规则

1. GNU风格中，#或者$表示立即数；@或者#表示注释（至于#到底是表示立即数还是表示注释，编译器能分的清楚，请放心）

2. #标号，指的是标号中的内容

3. 和MDK风格一样，GNU风格中，指令，伪指令，寄存器名称也是大小写敏感的；不过既可以都用大写，也可以都用小写，只要不混合使用即可

4. 如果一行代码太长了，可以使用"\"然后另起一行，但是要注意"\"后面不能存在任何字符，包括空白字符！

### 标号（Symbol / label）

标号只能由“a~z”   ,   “A~z”   ,   “0~9”   ,   "."   ,   "_"   组成，并且如果不是定义局部标号，则不能使用数字作为开头；

标号应当以冒号结尾

关于label，这个东西和高级语言中的函数或者变量都不太一样，我认为它被叫做标号就是因为它只起到了 助记符 的作用；一个标号可以是一个函数，也可以是一个变量，它具体是什么取决于程序怎么写；

### 标号和变量

GNU风格汇编 提供了用于定义不同类型的变量，并为其分配内存空间的伪指令

（相对高级语言，从汇编这里来看更能理解定义变量的本质：开辟一片内存空间，用于存放某个数据；这也是C语言没有提供定义长度可变的数组的原因，因为定义的时候，分配多少内存必须被确定好）

```assembly
@常见的有以下几种，看起来和C语言的变量类型差不多

.ascii	@定义一个字符串，并分配空间，具体分配多少要看有几个字节（教材上说.ascii定义字符串的时候需要在字符串尾加'\0'，但是我试了以下不加也是可以的...）
.asciz	@同上，但是不要求加'\0'
.string	@同.asciz
.byte	@定义一个字节，分配 1byte 空间，可以往里放各种一个byte可以放的下的东西，例如0xff或者'c'或者123
.short 	@可以放2个byte 例如0xffff
.quad	@分配8个byte
.space/.skip	@定义一块连续的内存，并且初始化，如果没有指定初始化数据，则初始化为0

```

所以想要定义一个变量可以这样写

```assembly
.section .data	@ 表示放在数据段里
.global int_aq	@ 如果需要定义成全局变量，还可以使用.global
int_a:
.int 123		@ 定义了一个int_a的段，以int_a为起始的地址的四个字节里放了一个int型的数字123

_start:
	@ 如果需要将int_a中的值装入寄存器：
	mov r0, #int_a 
```



### .equ .set

```assembly
.equ 标号, 值@为一个标号赋值，equ不会分配空间，它只能赋值

.set @和equ相似

/*例如*/
.equ int_a, 0x01
.set int_a, 0x01
```



### 内存对齐.align

这个指令是用来内存对齐的；内存最小的使用单位是1byte，也就是8bit，这就意味着我们可以每次只是用一个byte；

这样用内存是有可能会引发问题的，有一些操作是默认按照word或者half word为单位进行的（以word为单位为例，如果按照一个word为单位，即使指定的地址是0x03，实际上引用到的地址是0x00-0x03而不是0x03-0x06）；这意味着一旦出现之前使用了1个byte，后续也没有进行任何操作，那么有可能会导致数据被错误的修改或者使用；

.align的作用就在于内存对齐

```assembly
.align 2 @ 以4字节对齐（2^2）@ 
```

如果以四字节对齐，那么就算0x00被使用而0x01还没被用，下一个地址也会是0x04而不会去用0x01

### 局部标号

局部标号生效范围是一个 **宏** 之内；

局部标号的定义格式

```assembly
N{生效范围名称} @ N是一个0-99的数字，生效的范围，也可以不写
```

局部标号引用的语法

```assembly
%{F|B}{A|T}N{生效的范围} 
@ F表示编译器应当从前面寻找定义（fornt）
@ B表示编译器应当从后面寻找定义（back）
@ A表示编译器应当搜索整个宏的嵌套（all）
@ T表示编译器只需搜索宏的当前层次即可（this）

@ 若没有指定F|B，先向前搜索，再向后搜索
@ 若没有定义A|T，先搜索当前层次，搜索到最高层次，比当前层次低的层次不搜索
```



### 常量如何表示

1. 十进制数：以非0数字开头（123或者456这种默认是十进制数）
2. 二进制数：以0b（也可以写成0B）开头（例如0b01010101）
3. 八进制数：以0开头（例如0123表示八进制数）
4. 十六进制：以0x（或0X）开头的
5. 字符串：使用双引号引起来的内容会被视作字符串，其中可以使用例如'\n'这样的转义字符，遵循ascii规则
6. GNU中可以使用“.”表示当前指令的地址

### 表达式

GNU中可以使用+ - * / % > >= < <= << >> | & ^ ! == && ||等运算符，和C语言中的含义也一样；

### 分段

在说分段之前还是要简单学习一下啥子叫分段，为啥要分段，其实之前隐隐约约提到过，分段和冯诺依曼结构有关系，因为冯诺依曼结构的计算机将数据和代码一视同仁，把他们都放在一块内存里（也只有这么一块内存...）；所以为了区分二者，在逻辑上划分出了数据段和代码段；（哈弗结构简单粗暴，拥有两块内存，直接在物理上区分了数据段和代码段）

```assembly
.section <section_name>{, "<flags>"}
@ section_name有以下几种
@ .text 代码段
@ .data 已被初始化的数据段
@ .bss 	未被初始化的数据段
@ .rodata	字符串和#define定义的常量（实际上就是只读数据段）
@ .heap .stack 常量段

@ flags有以下几种
@ a 可分配
@ w 可写段
@ x 可执行段
```

用户是可以自己定义段的

```assembly
.section .hello		@ 自定义 一个叫.hello的段
.align 2			@ 对齐方式是4byte对齐
str:
.ascii "hello_world\n"	@ 将字符串"hello_world\n"，放在以str:标号为起始的一段内存空间中；这个行为非常像是 定义了一个字符串变量；
```



### .include 和 .extern

```assembly
.include "stdio.h" @引入stdio.h文件
```

```assembly
.extern function @ 告诉编译器 此处调用的函数是在外部文件中声明的
```



### .weak

弱定义：遇到使用了弱定义的标签，优先找其他地方的定义，如果没有，再用弱定义的内容；

```assembly
.weak function
@ 如果被 .weak 修饰；即使 仅声明不定义也是可以的；如果整个项目里定义了两个function，其中一个是弱定义，那么弱定义不会生效
```



### .macro宏定义

如果看过uboot的代码，会经常看到宏定义，汇编中的宏定义和C语言中的宏定义很相似；汇编中的宏定义还可以带参数

```assembly
.macro	set_vbar, regname, reg
	msr	\regname, \reg	
.endm

@ 这是uboot中的一个宏定义
@ 该宏定义的名称是 set_vbar
@ 该宏定义有两个参数，分别叫regname和reg
@ 调用该宏时应：

set_vbar CPSR, #0x00000000
@ 这个宏定义将被展开为
msr CPSR, #0x00000000
@ 意思是将0x00000000写入CPSR中
```



### .ldr指令和.ldr伪指令

和MDK风格一样...GNU风格中ldr同样即是指令，又是伪指令；取决于使用的时候的写法

```assembly
@ ldr伪指令的用法
ldr r1,=val @ 伪指令，将val的地址赋给r1
ldr pc,=0x0000ffff@伪指令，将0x0000ffff装入pc；这个用法可以实现pc的跳转

@ldr指令的用法
ldr r1, val	@ 指令，将val的内容赋给r1

```

扩展一下ldr伪指令的原理：

ldr rn, =expr

当expr是一个合法立即数的时候，ldr就会被翻译成mov指令；

当expr不是一个合法立即数的时候，ldr会先申请一段内存，然后把立即数存到内存里，然后把内存地址拿来用；（这种方式也被称为文字池）；

ldr伪指令的好处在于它不用考虑立即数的合法性问题





### adr伪指令

首先要说明，adr是伪指令，因此它不必遵守指令的编码规范；adr的编码规范如下：

| 31   | 30:29 | 28:24 | 23:5  | 4：0 |
| ---- | ----- | ----- | ----- | :--- |
| 0    | immlo | 10000 | immhi | rd   |

这个伪指令拥有21bits的立即数区域，并且是分开的；[39:29]这2位记录立即数的低位，[23:5]这19位记录立即数的高位；

其次，adr虽然和ldr的功能看起来非常相似，但是他们的实现原理完全不同；



adr是基于PC相对偏移地址进行读取的伪指令；

````assembly
@ 格式
adr xn, label

@ 举例
adr x0, _start
@ 这条指令将会
````



ldr是加载32bits的立即数或一个地址到指定的寄存器中；









### adrp伪指令

这个指令是ARMv8中新增加的指令；

```assembly
@ 格式
adrp rd, label
@ 含义是将label所在的内存页的起始地址，放入rd中
```

注：这里的内存页指的是以4kb为单位的连续的内存空间，和linux内核中的内存页不是一个东西

这个指令的编码格式相对特殊，不同于立即数区域12bits的指令，**adrp拥有21bits的立即数区域，并且在运行的过程中，这21bits会被扩展成一个33bits带符号的数**







### GNU编译&连接（不依赖lds文件）

目前这里需要注意一个地方

````shell
 # 以下是aarch64-linux-gnu-ld的说明
 -Ttext ADDRESS              Set address of .text section
 # 所以ld其实可以指定 链接后的程序的 代码段的起始地址
 
 aarch64-linux-gnu-ld test.o -Ttext 0x00000000 -o test.elf
 aarch64-linux-gnu-objcopy -O binary -S test.elf test.bin
 
 # 上面这个例子中，test.bin文件就是可以执行文件，因为我们规定了这个程序的入口地址是0x00000000，因此将这个文件加载到0x00000000就可以执行这个程序
 # 这种方法对uboot而言是非常重要的，因为uboot作为上电之后的执行的第一个或者第二个程序，确定程序内存入口是必要的
````



### GNU编译&链接（依赖lds文件）

复杂的工程，段的分布通常会非常复杂，lds文件的目的就是设置段的；这个文件可以定义：

1. 生成的目标文件的架构体系；

2. 程序以那个标号为入口；

3. 程序的其实内存位置；（**uboot里有用到，ARMv8的uboot将该地址定义为0x00000000，意味着这个可执行程序只要被拷贝到0x00000000为起始的内存地址，就可以被执行**）

4. 代码段，数据段，未初始化数据段....的排列顺序；

5. 在链接的时候，规定某个段内 "*.o" 文件的排列顺序；（例如可以手动规定，在text段内，开头是a.o的内容，随后是b.o的内容....）；因此在阅读大型项目而感觉无从下手的时候，可以看看lds中把哪个文件放在text段的开头，那么整个项目的入口就可以确定了；

如有需要修改这个文件，请参考GNU官网对lds的格式定义；



## 内联汇编（在C语言中使用汇编）



内联汇编：在C代码中插入一段汇编代码

**这部分内容最好去GNU官网查看GCC reference，文档的6.47有详细的说明，这篇文章只挑简单的内容学习**

```c
//内联汇编的格式
__asm__ __volatile__ ("汇编代码" //每条代码后要加”\n\t“
         :output //汇编输出给C代码的内容(返回结果)
         :input //C代码给汇编代码的内容（传递变量） 
         :clobber and scratch registers 
)@

//说明：
//1. 必须以__asm__或者asm开头；__volatile__是可以省略的，如果不写那么编译器会自动优化汇编代码，如果写上则代码会保持原样
//2. 对于output input以及changed registers；如果仅有output或者仅有input，是不能省略另一个冒号的；如果没有changed registers，则changed registers的冒号必须省略；

```

### 关于output

格式：[符号名] "约束" (变量)
约束：
	 	r：表示使用寄存器
    	 m：表示使用变量内存地址
    	 +：表示可读可写
     	=：表示只写
     	&：表示输出操作数不能使用输入要用到的寄存器

### 关于input

格式：[符号名] "约束" (变量/立即数)
约束：
         r：表示寄存器
         m：表示使用变量的内存地址
         i：表示使用立即数

### 关于clobber and scratch registers

*While the compiler is aware of changes to entries listed in the output operands, the inline
asm code may modify more than just the outputs.For example, calculations may require
additional registers, or the processor may overwrite a register as a side effect of a particular
assembler instruction. In order to inform the compiler of these changes, list them in the
clobber list*

*（译：尽管编译器能认识到 output列表中的内容会被改变，内联asm代码仍旧可能会在运行过程中修改output中没有被列出来的内容；例如，计算可能会需要额外的寄存器，或者处理器在执行某个汇编指令的时候会顺带改变其他的寄存器的值；为了告知编译器这些可能的变化，需要将这些寄存器列在clobber中）*

注：我的理解是：如果使用add指令时，将结果先存放在寄存器x0中，然后再将x0的值给返回给c语言的寄存器，此时虽然使用了x0，但是x0并不在input或者output的定义中，这种情况下我们就应当在clobber中声明x0；（**例4验证了这个东西**）

*"cc"
The "cc" clobber indicates that the assembler code modifies the flags register.
On some machines, GCC represents the condition codes as a specific hardware
register; "cc" serves to name this register. On other machines, condition code
handling is different, and specifying "cc" has no effect. But it is valid no matter
what the target.*

*cc：这个clobber指明了，汇编代码会改变标志寄存器；在一些平台上，gcc将条件代码表示为特定的硬件寄存器，cc就用于指代这些硬件寄存器；在别的平台上，条件代码的处理是不同的，这时候指定cc就没效果；但是无论目标是什么，指定cc总是不会出错的* （**例5验证这个东西**）

### 内联汇编举例

#### 内联汇编例1：

```c
asm(
    "mrs r0, cpsr\n\t" //每条指令的末尾要加"\n\t"
    "bic r0, r0, #0x80\n\t"
    "msr cpsr, r0"
    //这个例子中没有用到output那三个东西，都省略掉
);

```

#### 内联汇编例2：

```c
#include "stdio.h"
void main()
{
        printf("hello_world\n");
        // assembly
        int a,b = 2,c = 3;
        asm(
            "add %0, %1, %2\n\t"//这个例子中，使用%0代指a（a是input与output中声明的第一个标识）
            :"=r" (a)
            :"r" (b), "r" (c)
                        );
        printf("a=%d\n",a);
}
```

```shell
# 例子2的输出
hello_world
a=5
```

#### 内联汇编例3：

```c
#include "stiod.h"
void main()
{
        printf("hello_world\n");
        // assembly
        int a,b = 2,c = 3;
        asm(
             "adds %[result], %[op1], %[op2]\n\t"
              :[result] "=r" (a)
              :[op1] "r" (b), [op2] "r" (c)
              //注：这个例子中没有继续使用%0,%1...这样的方式调用参数；而是使用一个[名称]代表参数；明显这样更容易阅读
                        );
        printf("a=%d\n",a);
}
```

```shell
#例3的输出
hello_world
a=5
```

#### 内联汇编例4：在clobbe and scratch registers声明用到的寄存器

````c
//使用了额外的寄存器，但是没有在clobber中声明
#include "stdio.h"

void main()
{
        printf("hello_world\n");

        // ass

        int a,b = 2,c = 2;
        asm(
                        "add x0, %[op1], %[op2]\n\t"
                        "sub x0, %[op1], %[op2]\n\t"
                        "mov %[result], x0"
                        :[result] "=r" (a)
                        :[op1] "r" (b), [op2] "r" (c)
                        );
        printf("a=%d\n",a);
}
````

````shell
# 输出如下
hello_world
a=2
````

```c
//使用了额外的寄存器，同时在clobber中声明
#include "stdio.h"

void main()
{
        printf("hello_world\n");

        // ass

        int a,b = 2,c = 2;
        asm(
                        "add x0, %[op1], %[op2]\n\t"
                        "sub x0, %[op1], %[op2]\n\t"
                        "mov %[result], x0"
                        :[result] "=r" (a)
                        :[op1] "r" (b), [op2] "r" (c)
                        :"x0"
                        );
        printf("a=%d\n",a);
}
```

```shell
# 输出如下
hello_world
a=0
```

这个例子中，可以看到，虽然两个程序均能通过编译，使用了寄存器x0但是没有在clobber中声明的程序，得到的结果是错误的；

#### 内联汇编例5：

```c
#include "stdio.h"

void main()
{
        printf("hello_world\n");

        // ass
        unsigned long result_b, result_a;
        int a = 2, b = 2, c;
        asm(
                        "mrs %[result_b], nzcv\n\t"
                        "subs %[result_c], %[op1], %[op2]\n\t"
                        "mrs %[result_a], nzcv\n\t"
                        :[result_a] "=r" (result_a), [result_b] "=r" (result_b), [result_c] "=r"(c)
                        :[op1] "r" (a), [op2] "r" (b)
                        :"x1"
                        );
        printf("before=%x\nresult of calculate=%u\nafter=%x\n",result_b, c, result_a);
}
```

```shell
#输出为
hello_world
before=60000000
result of calculate=2684354562
after=80000000
#0110 0000 0000 0000 0000 0000 0000 0000表示在没有执行减法之前，nzvc是0110
#1000 0000 0000 0000 0000 0000 0000 0000表示在执行减法运算之后，运算结果为负数,产生了借位
```



```
```



```
```



### 如何查看C语言文件对应的汇编代码？（实例分析）

这是一个在 内联汇编例5 的时候遇到了一个问题，问题如下：

```c
#include "stdio.h"

void main()
{
        int real_op_1, real_op_2;
        int op1 = 2, op2 = 2;
        asm(
                        "mov %[real_op_1],%[op1]\n\t"
                        "mov %[real_op_2],%[op2]\n\t"
                        :
                        :[op1] "r" (op1), [op2] "r" (op2), [real_op_1]"r"(real_op_1), [real_op_2]"r"(real_op_2)
                        );
        printf("real_op_1=%d\nreal_op_2=%d\n",real_op_1,real_op_2);
}
```

上述代码的输出如下：

```shell
real_op_1=85
real_op_2=-1792014384
```

这里的问题是，op1和op2在c语言代码中被赋值为2，为什么将这两个参数传递到汇编里，再经过一次mov之后，就变成了很奇怪的数？

为了解决这个问题，我决定看看编译器里到底发生了什么

使用gcc -S test.c先汇编一哈，看看对应的汇编代码是啥；

```shell
gcc -S test.c #这个命令将生成test.S
```

接下来我将试着分析，c语言是被翻译成汇编语言之后，是怎样工作的

```assembly
        .arch armv8-a
        .file   "test.c"
        .text
        .section        .rodata
        .align  3
.LC0: @这是代码中使用过的一个字符串；
        .string "real_op_1=%d\nreal_op_2=%d\n"
        .text
        .align  2
        .global main
        .type   main, %function
main:
.LFB0:
        .cfi_startproc @ 用来生成调试信息的伪指令
        stp     x29, x30, [sp, -32]! @将x29，x30的值存入sp-32指向的内存；x29是栈帧寄存器=x86中的bp寄存器，用于存放偏移地址；x30是LR，用于存放返回地址；
        .cfi_def_cfa_offset 32
        .cfi_offset 29, -32
        .cfi_offset 30, -24
        mov     x29, sp	@将sp的值引入x29
        mov     w0, 2	@将立即数2放入w0
        str     w0, [sp, 28] @将w0中的值放入sp+28中，这步对应给op1赋值
        mov     w0, 2	@将立即数2放入w0
        str     w0, [sp, 24] @将w0f中的值放入sp+24中，这步对应给op2赋值
        ldr     w0, [sp, 28] @将sp+28中的内容写入w0，也就是将2写入w0
        ldr     w1, [sp, 24] @将sp+24中的内容写入w1，也就是将2写入w1
        ldr     w2, [sp, 20] @将sp+20的内容写入w2？该指令是什么？
        ldr     w3, [sp, 16] @将sp+16的内容写入w2？该指令是什么？
#APP
// 7 "test.c" 1
        mov x2,x0 @将x0中的值放入x2，之前w2中曾被写入了sp+20的内容，这时候应该会被覆盖
        mov x3,x1 @类似于上面一句

// 0 "" 2
#NO_APP
        ldr     w2, [sp, 16] @ 将sp+16的值放入w2中
        ldr     w1, [sp, 20] @ 将sp+20的值放入w1中
        @ 我认为这里出现了问题，如果在ASM中，将op1和op2的值传递到了x2和x3中，那么此处调用的就应该是x2和x3，为何调用的是w2和w1(或者说是x2和x1)？
        
        adrp    x0, .LC0
        add     x0, x0, :lo12:.LC0 @此处和重位有关，详见杂项-重定位；这一句和上一句联用的含义是，将.LC0的绝对地址存入x0中
        bl      printf @打印
        nop
        ldp     x29, x30, [sp], 32
        .cfi_restore 30
        .cfi_restore 29
        .cfi_def_cfa_offset 0
        ret
        .cfi_endproc
.LFE0:
        .size   main, .-main
        .ident  "GCC: (Debian 10.2.1-6) 10.2.1 20210110"
        .section        .note.GNU-stack,"",@progbits
```

从生成的test.S来看，寄存器完全对不上





## Demo：hello world



```assembly
.section .rodata #接下来的内容放入只读数据段
hellostr:
.ascii "hello\n" #定义一个字符串，并且分配内存

.section .text	#接下来的内容放入代码段
.global _start

_start:
        mov x0, #1
        ldr x1, =hellostr
        mov x2, #6
        mov x8, #64  //syscall write
        svc #0


        mov x0, #0
        mov x8, #93  //syscall exit
        svc #0
```

汇编-链接

```shell
aarch64-linux-gnu-as main.S -o main.o
aarch64-linux-gnu-ld main.o -o main
```

代码分析

**首先要了解，这里的各种指令，伪指令，寄存器同样是大小写敏感的；如果用小写就全部用小写，如果用大写就全部用大写，不要混用**

首先看寄存器的名称，都是"xn"说明这是按照64位寄存器使用的；


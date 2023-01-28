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



### 进程内存的分布结构









## 寄存器⭐

自从ARM指令集更新了第八个版本，arm就进入了64位的时代，寄存器的数量也迎来了飞跃，从原来的R0-R12的13个通用寄存器，变为了X0-X29的30个通用寄存器，同时由于进入了64位时代，新的寄存器也自然变成64位寄存器，为了和原先的32位寄存器兼容，ARMv8的每个寄存器都可以被当作32位寄存器使用；

在ARMv8以后**如果将寄存器视作64位寄存器，则用Xn的方式引用；如果将寄存器视作32位寄存器，则用Wn的方式引用 **

在实际进行编程的时候，寄存器的使用应当遵循一些约定（例如ATPCS或者AAPCS...）本章也会对这些约定做简单介绍



### ARMv7的寄存器

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

#### sp

sp：stack pointer 栈指针寄存器；（我们都晓得cpu是分时间片处理多个进程的，当进程切换时，sp寄存器就存着下一个进程的栈地址）

#### lr

lr：link register 连接寄存器；（当发生函数调用的时候，会把当前的地址记录在lr种，完成调用，需要返回的时候就按照lr中的地址返回即可；这个功能当然可以通过通用寄存器完成，但是arm还是提供了一个专用的寄存器以提高效率）

#### pc

pc：program counter 程序计数器；（每一个片选时间都会+1...这个没什么好说的，它指向哪里处理器就计算什么）

#### (A/C)PSR与SPSR

APSR：应用程序状态寄存器

CPSR：当前程序状态寄存器（**ARMv8中没有CPSR，取而代之的是PSATAE，详情->ARMv8的程序状态**）

SPSR：已保存程序状态寄存器

CPSR保存当前的进程的状态，当发生进程的切换时，CPSR的内容会被保存在SPSR中，而CPSR会保存新的进程的状态；如果需要切换回去的话，只需要把SPSR中的内容重新放回CPSR中即可；

这也是USR模式没有SPSR的原因...SPSR最大的用处就是在模式切换的时候保存原来的用户模式下的进程的状态，方便还原现场；

根据ARM的文档*ARM® Cortex®-A Series Version: 1.0 Programmer’s Guide for ARMv8-A* 的4.1.5

>  When taking an exception, the processor state is stored in the relevant Saved Program Status Register (SPSR), in a similar way to the CPSR in ARMv7. The SPSR holds the value of PSTATE before taking an exception and is used to restore the value of PSTATE when executing an exception return. (当发生异常的时候，进程的状态将会以一种**与ARMv7中的CPSR相似的方式**被存储在SPSR中)

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



#### 注意区分SPSR和SP

SPSR是异常发生的时候，用于保存CPSR内容的；SP是异常发生的时候，用于保存通用寄存器内容的



#### ATPCS对寄存器的规定

如果两个程序之间发生了调用（函数A调用函数B），那么 寄存器的使用 应当满足以下的规范：

1. 子程序之间传递参数时，如果参数数量小于4个，可以使用寄存器R0-R3传递参数，如果参数大于4个，多余的参数就要使用堆栈传递
2. r4-r11可被用于子程序内部保存局部变量；进入子程序之前应当保存这些寄存器的内容，退出子程序的时候应当恢复他们的初始值；
3. 寄存器r12被作为scratch寄存器，被记作ip，这种用法时常出现在 子程序代码段的连接中
4. r13是sp（所以说这些规则都是32位的规则，arm64中x13不是sp），r13只能用作sp
5. r14是lr，用于保存返回地址，如果子程序中在别的地方保存了返回地址，那么r14是可以用来放其余数据的
6. r15是pc，r15只能用做pc



### ARMv8的寄存器

#### AAPCS对寄存器的规定

ARMv8寄存器的变动较大，首先ARMv8中寄存器变多了，共有31个通用寄存器，记作x0-x30（或者w0-w30）；ARMv8函数调用规范服从的是AAPCS（顺便一提AAPCS是2007年提出的规范...比ARMv8诞生的要早得多...）

x0-x7：参数寄存器，可以用于传递参数和返回结果（32位ARM的参数寄存器只有r0-r3）

x9-x15：调用者寄存器（32位ARM中起作用的是寄存器r4-r11），对于被调用的函数来说，这几个寄存器可以随意使用；但是对于主函数来说，如果有需要保存的数据，一定要手动保存到栈中，调用结束后也要手动还原现场；

x18-x29：被调用者寄存器；对于被调用函数来说，这几个寄存器可以随意使用，无需做任何处理（实际上是需要考虑现场恢复的问题的，但是编译器会帮你处理好）

x8：间接结果寄存器

x16-x17：x16是IP0，x17是IP1，这两个寄存器是临时寄存器

x18：保留

x29：FP指向当前栈底

x30：LR

注意：

1. ARMv8中没有CPSR这个寄存器了，取而代之的是PSTATE；
2. ARMv8中不在可以主动使用PC寄存器；

《ARM® Cortex®-A SeriesVersion: 1.0 Programmer’s Guide for ARMv8-A》中4.1详细说明了aarch64中的寄存器变化



#### 调用者寄存器 和 被调用者寄存器

在AAPCS中，x9-x15和x18-x29之间有什么区别？

假定一个情景：假设现在函数A要调用函数B

此时我们称函数A为caller（调用者），函数B为callee（被调用者）

首先要明确一个原则：如果caller调用了callee，那么在调用callee 之前与之后 有些关键的寄存器数据应当保持一致；

为了保证这个原则，有三种解决方案：

1. caller和callee约定好“caller/callee保存”；自己保存自己的
2. caller调用callee之前，将寄存器存入自己的栈，当callee返回之后，将caller栈 中保存的原本状态写回寄存器；
3. callee运行的过程中，如果遇到一个需要使用的寄存器，就把这个寄存器里的内容单独取出来存在栈里，结束的时候单独恢复这一个寄存器的值

ARMv8采用的是方案1；

方案1和方案2相比：无法确定callee会用到的寄存器，因而在进行切换的时候，必须将寄存器全部保存，且在回调时又需要全部写入寄存器；这可能是一个相当耗费时间的操作，如果栈在内存里延迟还不会太大，但是一旦栈在磁盘或者更慢速的设备里，这样的操作就会带来灾难性的后果....

方案1和方案3相比：在程序执行的过程中，有很多与寄存器实际上和恢复现场没啥子关系，例如参数寄存器，临时寄存器等等；所以如果用到一个寄存器就要保存&恢复，有一部分工作量其实是不必要的；

再来详细的说明一下方案1：

ARMv8遵顼的Aarch64PCS（procedure call standard）做出了规定：

x9-x15是调用者寄存器，即在发生调用之前，如果程序员希望x9-x15中某些寄存器中的数据被保留到调用后**则应当在调用之前将数据入栈，这个操作需要由程序员手动进行，调用结束后也应当手动的恢复，这些工作编译器是不会帮你做的**；站在callee的视角，这些寄存器都是可以随意使用的；

类似的x18-x29是被调用者寄存器，如果callee要使用这些寄存器，必须由callee将初始值入栈，用完之后是要恢复的；**不过这些寄存器的入栈&恢复由编译器来完成，所以并不需要程序员手动编写相应代码**







#### ARMv8中的状态寄存器

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



#### ARMv8中的PC

《ARM® Cortex®-A SeriesVersion: 1.0 Programmer’s Guide for ARMv8-A》中有如下描述：

> One feature of the original ARMv7 instruction set was the use of R15, the Program Counter (PC) as a general-purpose register. The PC enabled some clever programming tricks, but it introduced complications for compilers and the design of complex pipelines. Removing direct access to the PC in ARMv8 makes return prediction easier and simplifies the ABI specification. The PC is never accessible as a named register. Its use is implicit in certain instructions such as PC-relative load and address generation. The PC cannot be specified as the destination of a data processing instruction or load instruction.

*译：PC是原先ARMv7指令集中R15的一个特性，PC是一个通用寄存器，PC可以实现一些巧妙的编程技巧，但是PC的存在也使得复杂流水线的设计和编译器产生了一些问题；ARMv8移除了对PC的直接访问，这使得回归预测就更加简单，同时简化了ABI规范；PC再也不能作为一个寄存器名称被访问；PC的使用被隐含在了一些指令中，例如对PC相对加载和地址生成；PC寄存器不能被用作数据处理的目的寄存器或者源寄存器*

也就是说，PC不能用了，ARMv8中不再能使用`mov pc， lr`返回了；

那么应该如何返回？

这里的建议是直接用`ret`指令，不加任何参数的情况下， 这条指令会跳转到lr保存的地址；





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

这个方式类似于C语言中的指针

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

这几个指令对于重定位有很大的用处，movz和movk可以一部分一部分的将数据送到一个64bits的寄存器中，解决了arm指令只有32bits，无法一次性携带长达64bits数据的问题；（这个特性对于重定位而言可谓是非常有用！！！）



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



#### LDR与LDRB与LDRH与LDRT（内存操作指令）

```assembly
LDR Rn Addr	@将Addr中的内容加载到Rn
@ 这里需要注意，内存的最小单位是Byte，1Byte=8bit；但是32位的ARMv7的LDR是以word为单位的，1 word = 4 byte = 32bit
@ 注2：LDR的第二个操作数不能是立即数，需要用另一个寄存器套一下
```

特别注意一下 **以字为单位**：假设内存中0x00-0x04的内存状态如下表；设R1中的值为0

| 地址 | 0x00 | 0x01 | 0x02 | 0x03 | 0x04 |
| ---- | ---- | ---- | ---- | ---- | ---- |
| 内容 | 00   | 11   | 22   | 33   | 44   |

````assembly
@ 在上述条件下执行指令：
LDR R0 [R1, #0x00]
@ 这个指令的结果是R0中的内容：0x33221100（33位于前面是因为“小端模式”的关系）

LDR R0, [R1, #0x01]
@ 这个的结果是：0x00332211 而非 0x44332211
@ 这就体现了 所谓的字为单位，0x0000_0000 0x0000_0001 0x0000_0002 0x0000_0003 这四个byte是一个字，无论对 0x00 0x01 0x02还是0x03执行LDR，结果都不会和0x0000_0004有任何关系；
@ 当LDR的Addr选择0x01时，R0中的值从0x01开始循环填充
````

```assembly
LDRB Rn, Addr
@ 这个指令类似于LDR，但是LDRB是以Byte为单位的
@ 例如
ldrb r0, [r1] @将存储器地址为r1的字节数据读入r0，并且将高24bits清空
ldrb r0, [r1, #8] @将存储地址为r1+8的字节数据读入r0，并且将高24bits清空
```

````assembly
LDRH 
@ 以半字(16bit)为单位
@ 例如
ldrb r0, [r1] @将存储器地址为r1的2字节数据读入r0，并且将高16bits清空
ldrb r0, [r1, #8] @将存储地址为r1+8的2字节数据读入r0，并且将高16bits清空
````

```assembly
LDRT
@ 以用户模式操作内存
@ 例如进行异常处理的时候需要以用户模式操作内存，就可以用ldrt
```









#### STR,STP与,STRB,STRH等

````assembly

STR Rn, Addr
@ 类似于LDR，STR是将Rn的值存储到Addr中，同样需要注意，小端模式和字为单位
STP r0, r1, Addr
@ STP是将一对寄存器中的值存入Addr指向的内存
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

ARM汇编代码调用C语言的函数时，.extern是一个重要的方法



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



## 异常处理

**异常处理其实是编程中相当重要的部分，而且异常处理其实相当常见...每次调用printf就会产生一次异常处理捏**

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

   1. 按照SP_excep中记录的地址，将现场还原

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





## 汇编，链接，装载，执行：一个程序从代码到进程经历了什么？

（**注：这部分的内容以ARM64为目标平台**）

强烈推荐去看看CSAPP，这个笔记只对后续用到的部分进行粗略的学习；

一段代码从文本变成可执行文件，需要经历 预编译，编译，汇编，链接，这四个步骤中，这篇笔记着重了解后两步；



首先准备2个C语言文件：main.c和sum.c；（汇编阶段我们以main.c举例）

```c
//main.c
int sum(int *a, int n);

int array[2] = {1,2};

int main()
{
        int val = sum(array,2);
        return val;
}
```

```c
//sum.c
int sum(int *a, int n)
{
        int i, s = 0;
        for(i = 0; i < n; i++)
        {
                s += a[i];
        }
        return s
}
```



对main.c进行编译，生成main.s方便后续分析；请注意，这里的main.s只不过是由main.c翻译而来的由汇编语言写成的代码，main.s只是代码，只是代码，只是代码；

```shell
pi@raspberrypi:$ gcc -S main.c -o main.s
```





### 汇编（as）与ELF文件：

使用as对一个.s（汇编语言编写的代码）进行汇编，会产生一个.o文件（**我们一般称其为“目标文件”**）；这个过程中汇编器做了什么？目标文件里又包含了什么信息？

```shell
#首先将.s文件汇编生成.o文件
aarch64-linux-gnu-as main.s -o main.o
```

`main.s`经过汇编之后生成的`main.o`这个目标文件是ELF格式文件，即executable and linkable format（即可执行与可链接格式）；使用readelf命令可以查看ELF文件的内容；

```shell
pi@raspberrypi:~/test_as_2 $ readelf -a main.o
ELF Header:
  Magic:   7f 45 4c 46 02 01 01 00 00 00 00 00 00 00 00 00
  Class:                             ELF64
  Data:                              2's complement, little endian
  Version:                           1 (current)
  OS/ABI:                            UNIX - System V
  ABI Version:                       0
  Type:                              REL (Relocatable file)
  Machine:                           AArch64
  Version:                           0x1
  Entry point address:               0x0
  Start of program headers:          0 (bytes into file)
  Start of section headers:          768 (bytes into file)
  Flags:                             0x0
  Size of this header:               64 (bytes)
  Size of program headers:           0 (bytes)
  Number of program headers:         0
  Size of section headers:           64 (bytes)
  Number of section headers:         12
  Section header string table index: 11

Section Headers:
  [Nr] Name              Type             Address           Offset
       Size              EntSize          Flags  Link  Info  Align
  [ 0]                   NULL             0000000000000000  00000000
       0000000000000000  0000000000000000           0     0     0
  [ 1] .text             PROGBITS         0000000000000000  00000040
       0000000000000028  0000000000000000  AX       0     0     4
  [ 2] .rela.text        RELA             0000000000000000  00000240
       0000000000000048  0000000000000018   I       9     1     8
  [ 3] .data             PROGBITS         0000000000000000  00000068
       0000000000000008  0000000000000000  WA       0     0     8
  [ 4] .bss              NOBITS           0000000000000000  00000070
       0000000000000000  0000000000000000  WA       0     0     1
  [ 5] .comment          PROGBITS         0000000000000000  00000070
       0000000000000028  0000000000000001  MS       0     0     1
  [ 6] .note.GNU-stack   PROGBITS         0000000000000000  00000098
       0000000000000000  0000000000000000           0     0     1
  [ 7] .eh_frame         PROGBITS         0000000000000000  00000098
       0000000000000038  0000000000000000   A       0     0     8
  [ 8] .rela.eh_frame    RELA             0000000000000000  00000288
       0000000000000018  0000000000000018   I       9     7     8
  [ 9] .symtab           SYMTAB           0000000000000000  000000d0
       0000000000000150  0000000000000018          10    11     8
  [10] .strtab           STRTAB           0000000000000000  00000220
       000000000000001d  0000000000000000           0     0     1
  [11] .shstrtab         STRTAB           0000000000000000  000002a0
       0000000000000059  0000000000000000           0     0     1
Key to Flags:
  W (write), A (alloc), X (execute), M (merge), S (strings), I (info),
  L (link order), O (extra OS processing required), G (group), T (TLS),
  C (compressed), x (unknown), o (OS specific), E (exclude),
  p (processor specific)

There are no section groups in this file.

There are no program headers in this file.

There is no dynamic section in this file.

Relocation section '.rela.text' at offset 0x240 contains 3 entries:
  Offset          Info           Type           Sym. Value    Sym. Name + Addend
00000000000c  000b00000113 R_AARCH64_ADR_PRE 0000000000000000 array + 0
000000000010  000b00000115 R_AARCH64_ADD_ABS 0000000000000000 array + 0
000000000014  000d0000011b R_AARCH64_CALL26  0000000000000000 sum + 0

Relocation section '.rela.eh_frame' at offset 0x288 contains 1 entry:
  Offset          Info           Type           Sym. Value    Sym. Name + Addend
00000000001c  000200000105 R_AARCH64_PREL32  0000000000000000 .text + 0

The decoding of unwind sections for machine type AArch64 is not currently supported.

Symbol table '.symtab' contains 14 entries:
   Num:    Value          Size Type    Bind   Vis      Ndx Name
     0: 0000000000000000     0 NOTYPE  LOCAL  DEFAULT  UND
     1: 0000000000000000     0 FILE    LOCAL  DEFAULT  ABS main.c
     2: 0000000000000000     0 SECTION LOCAL  DEFAULT    1
     3: 0000000000000000     0 SECTION LOCAL  DEFAULT    3
     4: 0000000000000000     0 SECTION LOCAL  DEFAULT    4
     5: 0000000000000000     0 NOTYPE  LOCAL  DEFAULT    3 $d
     6: 0000000000000000     0 NOTYPE  LOCAL  DEFAULT    1 $x
     7: 0000000000000000     0 SECTION LOCAL  DEFAULT    6
     8: 0000000000000014     0 NOTYPE  LOCAL  DEFAULT    7 $d
     9: 0000000000000000     0 SECTION LOCAL  DEFAULT    7
    10: 0000000000000000     0 SECTION LOCAL  DEFAULT    5
    11: 0000000000000000     8 OBJECT  GLOBAL DEFAULT    3 array
    12: 0000000000000000    40 FUNC    GLOBAL DEFAULT    1 main
    13: 0000000000000000     0 NOTYPE  GLOBAL DEFAULT  UND sum

No version information found in this file.
```

其中：



#### elf文件的elf header

elf头中包含的诸多内容中较为重要的是：

Magic：魔数，这个值决定了该文件的格式；例如java文件的Magic就是cafebabe（coffee baby），只有以cafebabe开头的文件才会被java虚拟机认为是java程序；

Class：文件类型，表明这个文件是64elf还是32elf

Data：大小端等信息

Type ELF：说明文件是Relocatable file还是Executable file（可执行文件）还是shared object file（共享对象文件）还是core dump file（core dump文件）；例子中这个文件是relocatable file（可重定位文件）

Entry point address：入口指针，这个值指向程序的入口，因为目前我们分析的是一个可重定位文件而非可执行文件，因此没有入口，所以这里是0x00

Start of section headers：表示段表（section table）的起始地址；这个例子中888（换算成十六进制是0x378）



#### elf文件的section header

section header中记录了程序的“段信息”（也就是我们常说的数据段，代码段...的段信息）；

段信息包括：

```c
// /usr/include/elf.h中定义了section header的结构体

typedef struct
{
  Elf64_Word    sh_name;                /* Section name (string tbl index) */
  Elf64_Word    sh_type;                /* Section type */
  Elf64_Xword   sh_flags;               /* Section flags */
  Elf64_Addr    sh_addr;                /* Section virtual addr at execution */
    //请注意，在没有进行链接的阶段，Address均为0x00
  Elf64_Off     sh_offset;              /* Section file offset */
  Elf64_Xword   sh_size;                /* Section size in bytes */
  Elf64_Word    sh_link;                /* Link to another section */
  Elf64_Word    sh_info;                /* Additional section information */  Elf64_Xword   sh_addralign;           /* Section alignment */
  Elf64_Xword   sh_entsize;             /* Entry size if section holds table */
} Elf64_Shdr;

```

我们的例子中有11个段（Nr=0的那个不算）：.text（代码段），.rela.text（需要重定位的指令），.data（数据段），.bss（未初始化数据段），.comment（存放编译器版本信息），.note.GNU-stack，.eh_frame（），.rela.eh_frame（），.symtab（符号表），.strtab（字符串表），.shstrtab（section header string table）；

详细说明一下其中部分表的作用：

rela.text：用于保存text段需要重定位的指令；

data数据段：保存 已经初始化的全局变量 和 已经初始化的局部静态变量（注意：这里只存放这两种数据，普通的局部变量并不会放在data里）

bss未初始化数据段：保存 未初始化的全局变量 和 未初始化的局部静态变量（注意：初始化为0 会被视为没有初始化...）bss段实际上在这个阶段是不占位置的

strtab字符串表：这个段中会存储elf文件中用到的各种字符串

section header中给出了各个段的offset（偏移地址），所以我们可以直观的看到经过汇编之后的elf文件的数据信息分布：

| elf header      | 起始偏移地址：00000000                                       |
| --------------- | ------------------------------------------------------------ |
| .text           | 起始偏移地址：0x40；size=0x28                                |
| .data           | 起始偏移地址：0x68；size=0x08                                |
| .bss            | 起始偏移地址：0x70；size=0x00                                |
| 注：            | .bss实际上是没有占位置的，如果本例中bss的size不等于0，comment段的起始位置也不会受到bss的size的影响 |
| .comment        | 起始偏移地址：0x70；size=0x28                                |
| .note.GNU-stack | 起始偏移地址：0x98；size=0x00                                |
| .eh_frame       | 起始偏移地址：0x98；size=0x38                                |
| .symtab         | 起始偏移地址：0xd0；size=0x150                               |
| .strtab         | 起始偏移地址：0x220；size=0x1d                               |
| 注：            | 0x220+0x1d=0x23d，但.rela.text的偏移地址是0x240；中间空缺<br>的2个字节应该由于内存对齐引起的(4字节对齐) |
| .rela.text      | 起始偏移地址：0x240；size=0x48                               |
| .rela.eh_frame  | 起始偏移地址：0x288；size=0x18                               |
| .shstrtab       | 起始偏移地址：0x2a0；size=0x59                               |

**这里要注意，在完成汇编之后，各个段虽然拿到了偏移地址，但是Address（虚拟地址）还是0**



#### elf文件中.text段中的具体内容

text段即为代码段，这个段中存储着程序中的代码；

使用objdump对main.o进行反汇编可以看到代码段的内容

````shell
# objdump的使用
objdump -s -d main.o # -s表明段以十六进制打印出来，-d表示反汇编
````

````shell
pi@raspberrypi:~/test_as_2 $ objdump -s -d main.o
#...
0000000000000000 <main>:
   0:   a9be7bfd        stp     x29, x30, [sp, #-32]!
   4:   910003fd        mov     x29, sp
   8:   52800041        mov     w1, #0x2                        // #2
   c:   90000000        adrp    x0, 0 <main>
  10:   91000000        add     x0, x0, #0x0
  14:   94000000        bl      0 <sum>
  18:   b9001fe0        str     w0, [sp, #28]
  1c:   b9401fe0        ldr     w0, [sp, #28]
  20:   a8c27bfd        ldp     x29, x30, [sp], #32
  24:   d65f03c0        ret
````

关注一下偏移地址为0x0c，0x10，0x14这3条指令

```assembly
#...
#偏移地址 机器码		指令		操作数
   c:   90000000        adrp    x0, 0 <main>
  10:   91000000        add     x0, x0, #0x0
  14:   94000000        bl      0 <sum>
#...
```

这几条指令明显的对应着C语言中的

```c
 int val = sum(array,2);
```

从机器码的角度看，这三条指令操作码后的内容是0，也就是说这几条指令引用的符号地址是0，0当然不可能是符号真正的地址；

为什么会这样？因为这一句代码中使用了`sum`函数，而`sum`函数在main.c中没有定义，汇编器无法确定符号地址；

这个地址，在链接的时候才会被具体的设置；



#### elf文件中.symtab符号表的详细说明

使用readelf -s [文件名]可以查看符号表

```shell
pi@raspberrypi:~/test_as_2 $ readelf -s main.o

Symbol table '.symtab' contains 14 entries:
   Num:    Value          Size Type    Bind   Vis      Ndx Name
     0: 0000000000000000     0 NOTYPE  LOCAL  DEFAULT  UND
     1: 0000000000000000     0 FILE    LOCAL  DEFAULT  ABS main.c
     2: 0000000000000000     0 SECTION LOCAL  DEFAULT    1
     3: 0000000000000000     0 SECTION LOCAL  DEFAULT    3
     4: 0000000000000000     0 SECTION LOCAL  DEFAULT    4
     5: 0000000000000000     0 NOTYPE  LOCAL  DEFAULT    3 $d
     6: 0000000000000000     0 NOTYPE  LOCAL  DEFAULT    1 $x
     7: 0000000000000000     0 SECTION LOCAL  DEFAULT    6
     8: 0000000000000014     0 NOTYPE  LOCAL  DEFAULT    7 $d
     9: 0000000000000000     0 SECTION LOCAL  DEFAULT    7
    10: 0000000000000000     0 SECTION LOCAL  DEFAULT    5
    11: 0000000000000000     8 OBJECT  GLOBAL DEFAULT    3 array
    12: 0000000000000000    40 FUNC    GLOBAL DEFAULT    1 main
    13: 0000000000000000     0 NOTYPE  GLOBAL DEFAULT  UND sum
```

符号表将在链接过程中起着无比重要的作用；符号表的结构被定义在/usr/include/elf.h中的

```c
//  /usr/include/elf.h
typedef struct
{
  Elf64_Word    st_name;                /* Symbol name (string tbl index) */
  unsigned char st_info;                /* Symbol type and binding */
  unsigned char st_other;               /* Symbol visibility */
  Elf64_Section st_shndx;               /* Section index */
  Elf64_Addr    st_value;               /* Symbol value */
  Elf64_Xword   st_size;                /* Symbol size */
} Elf64_Sym;
```

这是64位的elf符号表的结构

其中：

st_name：符号名

st_info：符号类型和绑定信息

st_other：符号能见度？（这个貌似目前也没用到...）

st_shndx：符号所在的段目录（即符号在哪个段，如果这个符号就在本文件里；那么这里的值就是符号所在的段，例如text或者data等..但是如果这个符号不是本文件里的，需要从外部链接，则会有所不同，下文详细介绍）

st_value：符号的值

st_size：符号的大小，对于包含着数据的符号这个值则表示数据的长度；



**符号类型与绑定（st_info）：**

```c
//同样是定义在/usr/include/elf.h中的
/* Legal values for ST_BIND subfield of st_info (symbol binding).  */

#define STB_LOCAL       0               /* Local symbol */
#define STB_GLOBAL      1               /* Global symbol */
#define STB_WEAK        2               /* Weak symbol */
#define STB_NUM         3               /* Number of defined types.  */
#define STB_LOOS        10              /* Start of OS-specific */
#define STB_GNU_UNIQUE  10              /* Unique symbol.  */
#define STB_HIOS        12              /* End of OS-specific */
#define STB_LOPROC      13              /* Start of processor-specific */
#define STB_HIPROC      15              /* End of processor-specific */

/* Legal values for ST_TYPE subfield of st_info (symbol type).  */

#define STT_NOTYPE      0               /* Symbol type is unspecified */
#define STT_OBJECT      1               /* Symbol is a data object */
#define STT_FUNC        2               /* Symbol is a code object */
#define STT_SECTION     3               /* Symbol associated with a section */
#define STT_FILE        4               /* Symbol's name is file name */
#define STT_COMMON      5               /* Symbol is a common data object */
#define STT_TLS         6               /* Symbol is thread-local data object*/
#define STT_NUM         7               /* Number of defined types.  */
#define STT_LOOS        10              /* Start of OS-specific */
#define STT_GNU_IFUNC   10              /* Symbol is indirect code object */
#define STT_HIOS        12              /* End of OS-specific */
#define STT_LOPROC      13              /* Start of processor-specific */
#define STT_HIPROC      15              /* End of processor-specific */
```

从定义来看，符号的绑定 指的是符号的生效范围，是local，global，或者是weak；

符号类型 实际上是相当丰富的，可以是未定义，可以是一个对象，可以是一个函数，一个文件，一个段等等...



**符号所在段（st_shndx）：**

```c
/* Special section indices.  */

#define SHN_UNDEF       0               /* Undefined section */
#define SHN_LORESERVE   0xff00          /* Start of reserved indices */
#define SHN_LOPROC      0xff00          /* Start of processor-specific */
#define SHN_BEFORE      0xff00          /* Order section before all others
                                           (Solaris).  */
#define SHN_AFTER       0xff01          /* Order section after all others
                                           (Solaris).  */
#define SHN_HIPROC      0xff1f          /* End of processor-specific */
#define SHN_LOOS        0xff20          /* Start of OS-specific */
#define SHN_HIOS        0xff3f          /* End of OS-specific */
#define SHN_ABS         0xfff1          /* Associated symbol is absolute */
#define SHN_COMMON      0xfff2          /* Associated symbol is common */
#define SHN_XINDEX      0xffff          /* Index is in extra table.  */
#define SHN_HIRESERVE   0xffff          /* End of reserved indices */
```

常用的特殊段有：

SHN_ABS：符号包含了一个绝对值

SHN_COMMON：表示这类的符号要在链接的时候被处理；（如果定义了一个未初始化的全局变量，这个变量就会被归到这里）

SHN_UNDEF：表示这个符号没有被定义，需要到其他的文件中找

**符号值（st_value）**

如果符号是一个函数或者是一个变量，那么符号的值就是这个符号的**地址**；

1. （对于目标文件）如果符号不是上面说的common类型的，那么符号值是**段中的 偏移地址**
2. （对于目标文件）如果符号是common类型的，那么符号值是符号的"对齐属性"
3. （对于可执行文件）st_value是符号的虚拟地址；

#### elf文件中.strtab字符串表

使用readelf -x 指定打印strtab信息

```shell
pi@raspberrypi:~/test_as_2 $ readelf -x 10 main.o

Hex dump of section '.strtab':
  0x00000000 006d6169 6e2e6300 24640024 78006172 .main.c.$d.$x.ar
  0x00000010 72617900 6d61696e 0073756d 00       ray.main.sum.
```

strtab的中的字符串是代码中用到的字符串，诸如函数的名字（例如main函数使用的"main"就可以在这里被找到），变量的名字（例如程序中声明的数组的名字”array“可以在这被找到），还有文件的名字（main.c）；

**但是 strtab段 不包括程序中用于输出的字符串！（如果程序中有printf("helloworld")之类的代码，那么"helloworld"这个字符串将会被放在.rodata中）**

要注意这个段里的内容实际上是连续的，这样我们只需要用strtab段的基地址+偏移地址就能取到这个段中的所有字符串



### 静态链接（ld）：



#### 为什么要链接？

汇编阶段结束后，会发现两个问题：

1. 查看符号表会发现有一些符号的类型是未定义类型；
2. 查看代码段内容，发现有一些机器码使用了假地址；

引起这两个问题的原因是，编译的时候，有一些符号定义在另一个文件里；（例如main.c中用到的函数`sum`定义在sum.c中）

为了解决这个问题，就需要进行链接，将几个文件撮成一个完整的文件；

如此一来只要程序没写错，那么所有的符号就都能在一个文件中被找到，这样就不再会有未定义的符号，之前未定义的符号暂定的假地址也可以被重新分配地址；



#### 链接器如何把多个文件捏成一个？

方法有两种：

1. 将每个elf文件头尾相连拼在一起，这种方法执行起来简单，但是由于内存页对齐的问题，会造成极大的内存浪费；

2. 将每个elf文件中相同的段合并在一起，这种方法规避了内存的浪费，但是需要重新对文件中的数据和符号进行重新解析和重定位；

目前通用的方法是第二种方法；

使用链接器完成链接，将两个目标文件 链接 成一个 可执行文件

```shell
ld main.o sum.o -e main -o main #-e指定程序入口，也就是入口函数
```



#### 静态链接到底做了什么？

静态链接的主要任务有2个：

1. 空间和地址的分配；
2. 符号的解析与重定位；

接下来对可执行文件`main`进行分析



#### 1.静态链接->空间和地址的分配

````shell
pi@raspberrypi:~/test_as_2 $ readelf -a main
ELF Header:
  Magic:   7f 45 4c 46 02 01 01 00 00 00 00 00 00 00 00 00
  Class:                             ELF64
  Data:                              2's complement, little endian
  Version:                           1 (current)
  OS/ABI:                            UNIX - System V
  ABI Version:                       0
  Type:                              EXEC (Executable file)
  Machine:                           AArch64
  Version:                           0x1
  Entry point address:               0x400120
  Start of program headers:          64 (bytes into file)
  Start of section headers:          4800 (bytes into file)
  Flags:                             0x0
  Size of this header:               64 (bytes)
  Size of program headers:           56 (bytes)
  Number of program headers:         4
  Size of section headers:           64 (bytes)
  Number of section headers:         8
  Section header string table index: 7

Section Headers:
  [Nr] Name              Type             Address           Offset
       Size              EntSize          Flags  Link  Info  Align
  [ 0]                   NULL             0000000000000000  00000000
       0000000000000000  0000000000000000           0     0     0
  [ 1] .text             PROGBITS         0000000000400120  00000120
       0000000000000088  0000000000000000  AX       0     0     4
  [ 2] .eh_frame         PROGBITS         00000000004001a8  000001a8
       0000000000000050  0000000000000000   A       0     0     8
  [ 3] .data             PROGBITS         0000000000410fe8  00000fe8
       0000000000000008  0000000000000000  WA       0     0     8
  [ 4] .comment          PROGBITS         0000000000000000  00000ff0
       0000000000000027  0000000000000001  MS       0     0     1
  [ 5] .symtab           SYMTAB           0000000000000000  00001018
       0000000000000210  0000000000000018           6    12     8
  [ 6] .strtab           STRTAB           0000000000000000  00001228
       000000000000005d  0000000000000000           0     0     1
  [ 7] .shstrtab         STRTAB           0000000000000000  00001285
       000000000000003a  0000000000000000           0     0     1
Key to Flags:
  W (write), A (alloc), X (execute), M (merge), S (strings), I (info),
  L (link order), O (extra OS processing required), G (group), T (TLS),
  C (compressed), x (unknown), o (OS specific), E (exclude),
  p (processor specific)

There are no section groups in this file.

Program Headers:
  Type           Offset             VirtAddr           PhysAddr
                 FileSiz            MemSiz              Flags  Align
  LOAD           0x0000000000000000 0x0000000000400000 0x0000000000400000
                 0x00000000000001f8 0x00000000000001f8  R E    0x10000
  LOAD           0x0000000000000fe8 0x0000000000410fe8 0x0000000000410fe8
                 0x0000000000000008 0x0000000000000008  RW     0x10000
  GNU_STACK      0x0000000000000000 0x0000000000000000 0x0000000000000000
                 0x0000000000000000 0x0000000000000000  RW     0x10
  GNU_RELRO      0x0000000000000fe8 0x0000000000410fe8 0x0000000000410fe8
                 0x0000000000000008 0x0000000000000018  R      0x1

 Section to Segment mapping:
  Segment Sections...
   00     .text .eh_frame
   01     .data
   02
   03     .data

There is no dynamic section in this file.

There are no relocations in this file.

The decoding of unwind sections for machine type AArch64 is not currently supported.

Symbol table '.symtab' contains 22 entries:
   Num:    Value          Size Type    Bind   Vis      Ndx Name
     0: 0000000000000000     0 NOTYPE  LOCAL  DEFAULT  UND
     1: 0000000000400120     0 SECTION LOCAL  DEFAULT    1
     2: 00000000004001a8     0 SECTION LOCAL  DEFAULT    2
     3: 0000000000410fe8     0 SECTION LOCAL  DEFAULT    3
     4: 0000000000000000     0 SECTION LOCAL  DEFAULT    4
     5: 0000000000000000     0 FILE    LOCAL  DEFAULT  ABS main.c
     6: 0000000000410fe8     0 NOTYPE  LOCAL  DEFAULT    3 $d
     7: 0000000000400120     0 NOTYPE  LOCAL  DEFAULT    1 $x
     8: 00000000004001bc     0 NOTYPE  LOCAL  DEFAULT    2 $d
     9: 0000000000000000     0 FILE    LOCAL  DEFAULT  ABS sum.c
    10: 0000000000400148     0 NOTYPE  LOCAL  DEFAULT    1 $x
    11: 00000000004001e0     0 NOTYPE  LOCAL  DEFAULT    2 $d
    12: 0000000000410ff0     0 NOTYPE  GLOBAL DEFAULT    3 _bss_end__
    13: 0000000000400148    96 FUNC    GLOBAL DEFAULT    1 sum
    14: 0000000000410ff0     0 NOTYPE  GLOBAL DEFAULT    3 __bss_start__
    15: 0000000000410ff0     0 NOTYPE  GLOBAL DEFAULT    3 __bss_end__
    16: 0000000000410ff0     0 NOTYPE  GLOBAL DEFAULT    3 __bss_start
    17: 0000000000400120    40 FUNC    GLOBAL DEFAULT    1 main
    18: 0000000000410ff0     0 NOTYPE  GLOBAL DEFAULT    3 __end__
    19: 0000000000410fe8     8 OBJECT  GLOBAL DEFAULT    3 array
    20: 0000000000410ff0     0 NOTYPE  GLOBAL DEFAULT    3 _edata
    21: 0000000000410ff0     0 NOTYPE  GLOBAL DEFAULT    3 _end

No version information found in this file.
````

1. 可以发现相对于main.o；test中的**Section Headers里**，text段，data段等的**Address不再是0**；Address表示的虚拟地址，这表明，经过链接，这些段已经获得了虚拟地址；
2. 相对于main.o这样的REL（可重定位文件），test这样的EXEC（可执行文件）多了一个Program Headers；其中有两个load；第一个load加载虚拟地址0x400000；第二个load加载0x410fe8；如果在section header中查找会发现0x410fd8对应的是.data段；那么0x400000是什么？每个可执行ELF文件，使用的都是虚拟地址；并且对于不同的ELF而言，虚拟地址是独立的，对于64位的ELF文件而言，进程的虚拟地址就是从0x400000开始分配的（对32位文件而言是0x08048000开始）

同时，在链接时，链接器会将各个目标文件中的相同的段进行合并

##### EXEC文件的.text段

查看main(EXEC文件)的`.text`段：

```shell
pi@raspberrypi:~/test_as_2 $ objdump -s -d main
#...
Disassembly of section .text:

0000000000400120 <main>:
  400120:       a9be7bfd        stp     x29, x30, [sp, #-32]!
  400124:       910003fd        mov     x29, sp
  400128:       52800041        mov     w1, #0x2                        // #2
  40012c:       90000080        adrp    x0, 410000 <sum+0xfeb8>
  400130:       913fa000        add     x0, x0, #0xfe8
  400134:       94000005        bl      400148 <sum>
  400138:       b9001fe0        str     w0, [sp, #28]
  40013c:       b9401fe0        ldr     w0, [sp, #28]
  400140:       a8c27bfd        ldp     x29, x30, [sp], #32
  400144:       d65f03c0        ret

0000000000400148 <sum>:
  400148:       d10083ff        sub     sp, sp, #0x20
  40014c:       f90007e0        str     x0, [sp, #8]
  400150:       b90007e1        str     w1, [sp, #4]
  400154:       b9001bff        str     wzr, [sp, #24]
  400158:       b9001fff        str     wzr, [sp, #28]
  40015c:       1400000c        b       40018c <sum+0x44>
  400160:       b9801fe0        ldrsw   x0, [sp, #28]
  400164:       d37ef400        lsl     x0, x0, #2
  400168:       f94007e1        ldr     x1, [sp, #8]
  40016c:       8b000020        add     x0, x1, x0
  400170:       b9400000        ldr     w0, [x0]
  400174:       b9401be1        ldr     w1, [sp, #24]
  400178:       0b000020        add     w0, w1, w0
  40017c:       b9001be0        str     w0, [sp, #24]
  400180:       b9401fe0        ldr     w0, [sp, #28]
  400184:       11000400        add     w0, w0, #0x1
  400188:       b9001fe0        str     w0, [sp, #28]
  40018c:       b9401fe1        ldr     w1, [sp, #28]
  400190:       b94007e0        ldr     w0, [sp, #4]
  400194:       6b00003f        cmp     w1, w0
  400198:       54fffe4b        b.lt    400160 <sum+0x18>  // b.tstop
  40019c:       b9401be0        ldr     w0, [sp, #24]
  4001a0:       910083ff        add     sp, sp, #0x20
  4001a4:       d65f03c0        ret
```

可见链接将main.o中的`.text`和sum.o中的`.text`放在了一起，他们的地址是连贯的；可见链接并没有粗暴的将两个文件首尾相接，而是对同类段进行了归纳和整理；



##### EXEC文件的.data段

```shell
#main.o中的数据段
pi@raspberrypi:~/test_as_2 $ readelf -x 3 main.o

Hex dump of section '.data':
  0x00000000 01000000 02000000                   ........
  
  
# sum.o的数据段（这个例子中sum.c中没有会被写入数据段的内容...）
pi@raspberrypi:~/test_as_2 $ readelf -x 2 sum.o
Section '.data' has no data to dump.

# main的数据段
pi@raspberrypi:~/test_as_2 $ readelf -x 3 main

Hex dump of section '.data':
  0x00410fe8 01000000 02000000                   ........
```

根据data段的规则:

main.o中的data段存放的应该是数组array={1,2}；

sum.o中data段是空的

main中的data段，将上述两者的data段进行了整合；（这个例子中sum.o的数据段是空的...如果sum.o的数据段中有内容的话，这里也能看到链接后的文件会将其整合）

*（注：这里要说明一下为什么0x01000000=1，0x02000000=2；这个现象是由于小端模式引起的，01 00 00 00在内存中的分布如下*

| *01* | *00* | *00* | *00* |
| ---- | ---- | ---- | ---- |

*小端模式读取的时候应当以字节为单位，从后向前读取；也就是00 00 00 01）*



**当链接器将各个目标文件中的相同段进行了合并，每个符号就都拥有了唯一的地址，此时再也没有所谓的未知符号（当然前提时程序没写错...）**



#### 2.静态链接->符号的重定位

在完成了汇编之后，我们通过查看ELF的.rela段就可以找到有哪些符号需要重定位；在汇编阶段，汇编器如果遇到一个地址不能确定的符号引用，就会生成一个重定位条目，并将之记录在.rela段中；

通过使用readelf -r [文件名]去查看，一个**目标文件中**的**.rela段**，可以查看**目标文件**中有哪些label需要重定位，以main.o为例：

```shell
pi@raspberrypi:~/test_as_2 $ readelf -r main.o

Relocation section '.rela.text' at offset 0x240 contains 3 entries:
  Offset          Info           Type           Sym. Value    Sym. Name + Addend
00000000000c  000b00000113 R_AARCH64_ADR_PRE 0000000000000000 array + 0
000000000010  000b00000115 R_AARCH64_ADD_ABS 0000000000000000 array + 0
000000000014  000d0000011b R_AARCH64_CALL26  0000000000000000 sum + 0

Relocation section '.rela.eh_frame' at offset 0x288 contains 1 entry:
  Offset          Info           Type           Sym. Value    Sym. Name + Addend
00000000001c  000200000105 R_AARCH64_PREL32  0000000000000000 .text + 0
```

上述信息表明这文件里，在.text和.eh_frame中有需要重定位的符号；



##### .rela中包含什么信息？

.rela被定义在elf.h中

````c
// 在/usr/include/elf.h中可以找到rela的结构体定义

/* I have seen two different definitions of the Elf64_Rel and
   Elf64_Rela structures, so we'll leave them out until Novell (or
   whoever) gets their act together.  */
typedef struct
{
  Elf64_Addr    r_offset;               /* Address */
  Elf64_Xword   r_info;                 /* Relocation type and symbol index */
} Elf64_Rel;
typedef struct
{
  Elf64_Addr    r_offset;               /* Address */
  Elf64_Xword   r_info;                 /* Relocation type and symbol index */
  Elf64_Sxword  r_addend;               /* Addend */
} Elf64_Rela;
/*关于Rel与Rela，用哪个取决于你的架构，ARM用的是Rela；*/
/*Rel与Rela的区别只有r_addend这个参数，这个参数是一个加数，对于使用Rela的处理器，用户需要手动的指定这个加数；但是用Rel的处理器并不是没有这个参数...他们只是根据处理器架构给这个参数设置了一个默认值*/
````

```c
//关于r_info的一些代码
#define ELF64_R_SYM(i)                  ((i) >> 32)	//重定位条目的符号表的索引
#define ELF64_R_TYPE(i)                 ((i) & 0xffffffff) //重定位入口的type（这个type决定了重定位的算法）
#define ELF64_R_INFO(sym,type)          ((((Elf64_Xword) (sym)) << 32) + (type))
```

**r_offset：**重定位符号引用 在自己的段内的偏移地址；（例如某句代码引用了一个重定位条目符号，那么r_offset就是该句代码在代码段中的偏移地址）

**r_info：**从elf.h的定义来看，r_info的高32位是 重定位条目（也就是需要被重定位的符号） 在 符号表中的偏移地址；低32位是重定位条目的类型（这个类型决定了要以什么样的算法去计算重定位地址），重定位类型还是比较多的，在静态链接中最重要的类型有两个：1.相对地址的重定位；2.绝对地址的重定位；https://github.com/ARM-software/abi-aa/blob/main/aaelf64/aaelf64.rst#relocation-codes 中详细记录了各中不同的类型和对应的计算方法

**r_addend：**这个参数就是一个固定的常数；

注：重定位的计算公式会涉及到以下几个东西：

S：指的是符号的地址

A：r_addend

P：引用符号的运行时地址



#### 重定位例子具体分析：

具体分析2个例子：

在main.o中的.rela段中有如下信息：

```shell
pi@raspberrypi:~/test_as_2 $ readelf -r main.o

Relocation section '.rela.text' at offset 0x240 contains 3 entries:
  Offset          Info           Type           Sym. Value    Sym. Name + Addend
00000000000c  000b00000113 R_AARCH64_ADR_PRE 0000000000000000 array + 0
000000000010  000b00000115 R_AARCH64_ADD_ABS 0000000000000000 array + 0
000000000014  000d0000011b R_AARCH64_CALL26  0000000000000000 sum + 0
#...
```

有三个重定位条目；重定位类型根据Info的低32位可以确定（ 查阅 https://github.com/ARM-software/abi-aa/blob/main/aaelf64/aaelf64.rst#relocation-codes ）

1. 0x113 -> R_<CLS>_ ADR_PREL_PG_HI21 -> 计算公式：Page(S+A)-Page(P)
2. 0x115 -> R_<CLS>_ ADD_ABS_LO12_NC -> 计算公式：S + A
3. 0x11b -> R_<CLS>_CALL26 -> 计算公式：S+A-P

其中1和2共同完成了一个绝对地址的重定位（根据文档对R_<CLS>_ ADR_PREL_PG_HI21类型的描述，这个类型和R_<CLS>_ ADD_ABS_LO12_NC类型是搭配在一起使用的）

3完成了一个相对地址的重定位



##### 实例1：绝对地址重定位

``` shell
# readelf -r main.o
   Offset          Info           Type           Sym. Value    Sym. Name + Addend
00000000000c  000b00000113 R_AARCH64_ADR_PRE 0000000000000000 array + 0
000000000010  000b00000115 R_AARCH64_ADD_ABS 0000000000000000 array + 0
# 首先分析第2行代码
# 由r_info的高32位可知，需要被重定位的符号在符号表中的偏移地址是0x0b；查找可知是array
# 由r_info的低32位可知，对应的type是0x113，查阅资料可知是R_<CLS>_ ADR_PREL_PG_HI21，对应的计算公式是：Page(S+A)-Page(P)
# 这里的S是符号array的虚拟地址，0x410fe8；A是addend，0；Page(expr)的算法是将低12位归零；因此Page(S+A) = 0x410000
# P是这句代码的地址0x40012c；Page(P) = 0x400000
# 重定位的结果是0x010000；

# 对第3行进行分析
# 由r_info的低32位可知，对应的type是0x115，查阅资料可知是R_AARCH64_ADD_ABS_LO12_NC，对应的计算公式是：S + A（从Type也可以看到是R_AARCH64_ADD_ABS）
# S是符号array在符号表中的虚拟地址，0x410fe8
# A是附加常量addend，这里是0
# 因此重定位的结果应该是0x41 0f e8
```

让我们对照一下链接前后的情况：

```shell
# 链接之前 objdump -s -d main.o
   c:   90000000        adrp    x0, 0 <main>
  10:   91000000        add     x0, x0, #0x0
# 链接之后 objdump -s -d main
 40012c:       90000080        adrp    x0, 410000 <sum+0xfeb8>
 400130:       913fa000        add     x0, x0, #0xfe8
```

1. **关于第一条adrp指令，objdump可能出现了一些错误**：查阅 https://developer.arm.com/documentation/ddi0596/2021-12/Base-Instructions/ADRP--Form-PC-relative-address-to-4KB-page-?lang=en 可以看到adrp的格式如下：

   | 31   | 30：29                 | 28：24 | 23：5                   | 4：0 |
   | ---- | ---------------------- | ------ | ----------------------- | ---- |
   | 1    | 立即数的低2位（immlo） | 10000  | 立即数的高19位（immhi） | Rd   |

   根据这个规则，机器码是0x90 00 00 80；那么立即数应该是0x10（注意！二进制1000=0x10）；因此代码应该是 `adrp x0，0x10`而非objdump中显示的`adrp    x0, 410000 <sum+0xfeb8>`；这里我们以机器码为准，机器码中的立即数是0x10，根据adrp的机制，立即数在使用的时候应当左移12位，也就是0x10000（与我们计算得到的重定位的结果相同）；

   adrp的机制：

   step1：将PC的低12bits清零，也就是0x40012c -> 0x400000

   step2：将立即数左移12bits

   step3：将两者相加，结果存入目标寄存器

   因此目标寄存器X0中会被存入0x410000

   

2. 关于第二条命令add：由于第一条指令已经在X0寄存器中写入了0x410000，再加上0xfe8，X0中的内容实际上就是S + A的值；也就是符号`array`的虚拟地址；

这两条命令，最后的目的就是在于将array的地址，直接放在X0寄存器中，以供后续的程序调用；虽然adrp指令使用了PC，但最后得到的结果仍旧是S + A，因此并不是相对地址重定位，而是两条命令共同完成了一个绝对地址重定位；至于为什么费这么大的周折，请参照下文->*问什么要区分相对地址与绝对地址* 和 *ARM64中的特殊重定位手段*



##### 实例2：相对地址重定位

对本例中，对函数`sum`的重定位就是一个相对地址的重定位

```shell
# readelf -r main.o
   Offset          Info           Type           Sym. Value    Sym. Name + Addend
000000000014  000d0000011b R_AARCH64_CALL26  0000000000000000 sum + 0
# 查表可知r_info低32位（0x11b）对应的type是R_AARCH64_CALL26
# 对应的计算公式是：S + A - P
# S是符号sum在符号表中的地址：0x400148
# A是附加常数，0
# P是当程序运行到这句代码的时候，PC指向的地址；链接后这句代码的地址是0x400134

# S + A - P = 0x400148 + 0 - 0x400134 = 0x14

```

对照一下链接前后的情况

```shell
# 链接前 objdump -s -d main.o
14:   94000000        bl      0 <sum>
# 链接后 objdump -s -d main
400134:       94000005        bl      400148 <sum>

```

**此时结果看起来好像不太对？为什么我们算出来是0x14，而机器码中填入的确是00 00 05？**

**这个现象是由BL指令的机制引起的**

https://developer.arm.com/documentation/ddi0596/2021-12/Base-Instructions/BL--Branch-with-Link-?lang=en（BL指令官方文档）

从上述文档中，可以看到BL的机器码遵循以下格式

| 31:26  | 25:0           |
| ------ | -------------- |
| 100101 | 26bits的立即数 |

BL指令会无条件的跳转到：当前位置 + （立即数 * 4）的位置；

也就是会跳转到：0x400134 + 0x05 * 0x04 = 0x400148；查看main的代码段，会发现0x400148正好是函数`sum`的起始地址；由此看来重定位完美的完成了任务；



#### 为什么要区分相对地址和绝对地址？

相对地址重定位，公式是S+A-P：这个公式最后计算得到的实际上是`符号地址（S）`与`PC地址（P）`之间的差值；这种方式会用于类似于`BL`这样的转跳指令；因为这类指令的实现逻辑就是`PC+立即数`转调至目标，其中立即数是PC与目标之间的差值；

绝对地址重定位，公式是S+A：这个公式得到的就是`符号地址`这个地址和PC没有任何关系；这种方式会用于类似于MOV这类操作，实现逻辑和PC没有任何关系，立即数 指向哪里就去哪里取数据；



##### 为什么ARM64中绝对地址寻址需要多条指令才能完成？

这个问题和 **ARM64的寻址范围** 以及 **ARM64的编码方式** 有关....

毫无疑问ARM64的寻址范围高达2^64；这意味着在不考虑诸如内核空间等问题的情况下数据可能出现在0~2^64之间的任何一个位置；而ARM64的编码方式仍旧是32-bit编码，这又意味着一条ARM指令中不可能放下64-bit的立即数，甚至都不能放下32-bit的立即数；因此，我们无法 只用一条指令 就将 一个表示地址的64bits立即数 放到寄存器中！

（对应的，相对地址寻址可以用一条指令完成，但是如果去仔细查看BL的指令说明，会发现BL的寻址能力实际上是有限的，他只能对PC ±4KB范围内的符号进行寻址，一旦超出这个范围，BL就找不到目标了）

为了解决这个问题，ARM提供了很多种解决方案，这些方案的核心思想就在于，分多次将立即数存入寄存器；

可以举两个例子：

###### 解决方案1

例如可以将一个64bits的立即数砍成4段，用4条指令一段一段的送入同一个寄存器；

参考文章：

https://stackoverflow.com/questions/38570495/aarch64-relocation-prefixes/38608738#38608738

（部分翻译）

*...*

*Aarch64重定位必须解决立即数的问题，实际上重定位问题实际上是涉及到两个问题：1是找到程序想要使用的真正的值（这个问题是纯粹的重定位的问题）；2是需要一个能将这个值放入寄存器的方法，因为任何指令都不可能直接容纳长达64bits的 立即数 ；*

*第二个问题可以使用group relocation解决，一个group中每个重定位类型都被用于计算 64bits值中的16bits的部分；因此在一个group中，只有4中重定位的类型（从G0排到G3）（**李富贵注：根据我的理解，所谓的group relocation，将一个64bits的地址，砍成4段，每段16bits，拼起来就能拼成完整的64bits，正好汇编指令里提供了movk这样的指令，这样的操作也很容易被实现**）*

*这种分割出16bits的切片以保存立即数的方法适合movk，movz，movn；其他的指令，例如b，bl，adrp，adr等等，则另有其他的重定位类型*

...

*G0重定位，被用于加载低16bits[15:0]的值，除非被明确的禁止，否则应当检查被加载的值是否<=2^16；G1应当检查是否小于2^32，G2应当检查是否小于2^48，G3就不用检查了（**李富贵注：这里的检查，指的是检查完成操作后，寄存器的值；例如：G0检查，检查的是将一个数送入寄存器的低16bits后，寄存器中的值 是否大于2^16?   G1检查，检查的是将16bits的数据送入寄存器[31:16]后，寄存器中的数是否大于2^32 **）*

*运算符：*

*为了书面的美观，重定位的名字中并没有包含R_AARCH64_ 前缀（以下提到的relocation name本身都应该加一个R_AARCH64_前缀）*

````tex
Operator    | Relocation name | Operation | Inst | Immediate | Check
------------+-----------------+-----------+------+-----------+----------
:abs_g0:    | MOVW_UABS_G0    | S + A     | movz | X[15:0]   | 0≤X≤2^16
------------+-----------------+-----------+------+-----------+----------
:abs_g0_nc: | MOVW_UABS_G0_NC | S + A     | movk | X[15:0]   | 
------------+-----------------+-----------+------+-----------+----------
:abs_g1:    | MOVW_UABS_G1    | S + A     | movz | X[31:16]  | 0≤X≤2^32
------------+-----------------+-----------+------+-----------+----------
:abs_g1_nc: | MOVW_UABS_G1_NC | S + A     | movk | X[31:16]  | 
------------+-----------------+-----------+------+-----------+----------
:abs_g2:    | MOVW_UABS_G2    | S + A     | movz | X[47:32]  | 0≤X≤2^48
------------+-----------------+-----------+------+-----------+----------
:abs_g2_nc: | MOVW_UABS_G2_NC | S + A     | movk | X[47:32]  | 
------------+-----------------+-----------+------+-----------+----------
:abs_g3:    | MOVW_UABS_G3    | S + A     | movk | X[64:48]  | 
            |                 |           | movz |           |
------------+-----------------+-----------+------+-----------+----------
:abs_g0_s:  | MOVW_SABS_G0    | S + A     | movz | X[15:0]   | |X|≤2^16
            |                 |           | movn |           |
------------+-----------------+-----------+------+-----------+----------
:abs_g1_s:  | MOVW_SABS_G1    | S + A     | movz | X[31:16]  | |X|≤2^32
            |                 |           | movn |           |
------------+-----------------+-----------+------+-----------+----------
:abs_g2_s:  | MOVW_SABS_G2    | S + A     | movz | X[47:32]  | |X|≤2^48
            |                 |           | movn |           |
------------+-----------------+-----------+------+-----------+----------
````

*这种重定位的典型用法*

```assembly
Unsigned 64 bits                     
movz    x1,#:abs_g3:u64               
movk    x1,#:abs_g2_nc:u64            
movk    x1,#:abs_g1_nc:u64            
movk    x1,#:abs_g0_nc:u64
@ 李富贵注:
@ 1.首先将一个16bit的数使用movz移动到x1中，由于movz的特性，这个操作会同时将[63:48]之外的内容全部清空
@ 2. 后续的3个movk操作，将操作数移入x1中即可（这里一定要复习以下movk和movz，不了解这两个指令是无法理解这个过程的）

Signed 64 bits
movz  x1,#:abs_g3_s:u64
movk  x1,#:abs_g2_nc:u64
movk  x1,#:abs_g1_nc:u64
movk  x1,#:abs_g0_nc:u64
```

*group relocation也可以用如下的操作符*

```tex
Operator    | Relocation name | Operation | Inst | Immediate | Check
------------+-----------------+-----------+------+-----------+----------
[implicit]  | LD_PREL_LO19    | S + A - P | ldr  | X[20:2]   | |X|≤2^20
------------+-----------------+-----------+------+-----------+----------
[implicit]  | LD_PREL_LO21    | S + A - P | adr  | X[20:0]   | |X|≤2^20
------------+-----------------+-----------+------+-----------+----------
[implicit]  | LD_PREL_LO21    | S + A - P | adr  | X[20:0]   | |X|≤2^20
------------+-----------------+-----------+------+-----------+----------
:pg_hi21:   | ADR_PREL_PG     | Page(S+A) | adrp | X[31:12]  | |X|≤2^32
            | _HI21           | - Page(P) |      |           |
------------+-----------------+-----------+------+-----------+----------
:pg_hi21_nc:| ADR_PREL_PG     | Page(S+A) | adrp | X[31:12]  | 
            | _HI21_NC        | - Page(P) |      |           |
------------+-----------------+-----------+------+-----------+----------
:lo12:      | ADD_ABS_LO12_NC | S + A     | add  | X[11:0]   | 
------------+-----------------+-----------+------+-----------+----------
:lo12:      | LDST8_ABS_LO12  | S + A     | ld   | X[11:0]   | 
            | _NC             |           | st   |           |
------------+-----------------+-----------+------+-----------+----------
:lo12:      | LDST16_ABS_LO12 | S + A     | ld   | X[11:1]   | 
            | _NC             |           | st   |           |
------------+-----------------+-----------+------+-----------+----------
:lo12:      | LDST32_ABS_LO12 | S + A     | ld   | X[11:2]   | 
            | _NC             |           | st   |           |
------------+-----------------+-----------+------+-----------+----------
:lo12:      | LDST64_ABS_LO12 | S + A     | prfm | X[11:3]   | 
            | _NC             |           |      |           |
------------+-----------------+-----------+------+-----------+----------
:lo12:      | LDST128_ABS     | S + A     | ?    | X[11:4]   | 
            | _LO12_NC        |           |      |           |
```



###### 解决方案2

抑或是向上面的例子一样，使用adrp指令，以page+offset的方式，将寻址范围扩大；

查阅adrp的指令说明（https://developer.arm.com/documentation/ddi0596/2021-12/Base-Instructions/ADRP--Form-PC-relative-address-to-4KB-page-?lang=en），可以清晰的看到adrp指令可以容纳21bits的立即数，并且adrp会以PC所在的Page为基准，将21bits的立即数左移12bits，扩展为33bits的带符号立即数，因此，adrp能够将寻址范围扩展到PC±4GB的范围；

这个方法虽然在过程中使用了PC，但只是寻址范围与PC有关，而获得结果还是一个绝对地址（可用于MOV之类的指令）；



### 进程的内存分布结构

从”静态链接“这个章节可以看出来，程序是运行在所谓的虚拟地址空间里的；虽然最终肯定是需要物理内存去承载程序的，但程序们会认为自己身处一片2^32bits（32位为例）的广阔空间中，可实际上这只是一种错觉...物理意义上的内存条或许连2GB都没有...

32位地址空间的分布如下:

```tex
++++++++++++++++ 0xffff_ffff
|  内核空间1g   | 用户进程不得访问内核空间
++++++++++++++++ 0xc000_0000
|              |
|  用户空间3g   | 用户空间进程之间是独立的
|              |
++++++++++++++++ 0x0000_0000
```

每个进程的用户空间都是独立的；如果不做特殊处理，进程与进程之间是看不到对方的用户空间的；（**32位地址空间中的内核空间和用户空间的比例并不一定是1：3，这是可以配置的；**）

用户空间中也有结构：（以linux进程标准的内存布局为例）

````tex
++++++++++++++ 0xc000_0000
|1.随机栈偏移|
|-----------|
|2.用户栈	 | 
|....	    |
|-----------|
|3.共享库    |
|-----------|
|...        |
|4. 运行时堆 |
|-----------|
|5. .data/.bss|
|-----------|
|6. .init.text.rodata|
|------------|
|7. 未使用      |
++++++++++++++ 0x0000_0000
````

详细解释以下用户空间的结构：

1. 随机栈偏移：这个东西是linux5.13引入的一个策略；是一个安全性策略
2. 栈：栈用于保存 用户进程和子进程的 参数，返回值，局部变量；
3. 共享库：静态链接的时候是不存在这个部分的...共享库是动态链接的产物，linux的.so文件和windows里的.dll文件就是共享库；多个文件引用同一个文件时，就可以将被引用的这个文件编译成动态库，然后进行动态链接，这样就不需要多次加载同一个东西了；
4. 堆：C语言中每次malloc()就是在从堆里申请内存
5. ....后面的几个段之前都见过了（略



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
//2. 对于output input以及clobber；如果仅有output或者仅有input，是不能省略另一个冒号的；同时，如果没有changed registers，则changed registers的冒号必须省略；

```

### 关于output

格式：[符号名] "约束" (变量)
约束：
	 	r：表示使用寄存器
    	 m：表示使用变量内存地址
    	 +：表示可读可写
     	=：表示只写
     	&：表示输出操作数不能使用输入要用到的寄存器，但是这个符号只能以'+&'或者'=&'的方式使用，即可以使用"+&r" "+&m" “=&r” "=&m"（**详参笔记：内联汇编代码分析->内联汇编分析1**）

### 关于input

格式：[符号名] "约束" (变量/立即数)
约束：
         r：表示寄存器
         m：表示使用变量的内存地址
         i：表示使用立即数

要注意不要随意修改input中的内容：

> Warning: Do not modify the contents of input-only operands (except for inputs tied to outputs). The compiler assumes that on exit from the asm statement these operands contain the same values as they had before executing the statement. It is not possible to use clobbers to inform the compiler that the values in these inputs are changing. One common work-around is to tie the changing input variable to an output variable that never gets used. Note, however, that if the code that follows the asm statement makes no use of any of the output operands, the GCC optimizers may discard the asm statement as unneeded (see [Volatile], page 599). 

*译：不要去修改仅作为输入的操作符的内容（除了与输出绑定的输入）；编译器会假定从asm语句退出时 这些操作符 与asm语句执行之前 的值是相同的；因为没有办法使用clobbers通知编译器input中的数据会在执行asm语句时改变；常用的处理措施是将会改变的input变量和不会被用到的output变量绑定；然而仍旧要注意，如果asm语句的输出操作符没有被用到，那么GCC可能会认为这个asm语句没有意义，而将之优化掉；*



### 关于clobber and scratch registers

> While the compiler is aware of changes to entries listed in the output operands, the inline asm code may modify more than just the outputs.For example, calculations may require additional registers, or the processor may overwrite a register as a side effect of a particular assembler instruction. In order to inform the compiler of these changes, list them in the clobber list

*（译：尽管编译器能认识到 output列表中的内容会被改变，内联asm代码仍旧可能会在运行过程中修改output中没有被列出来的内容；例如，计算可能会需要额外的寄存器，或者处理器在执行某个汇编指令的时候会顺带改变其他的寄存器的值；为了告知编译器这些可能的变化，需要将这些寄存器列在clobber中）*

注：我的理解是：如果使用add指令时，将结果先存放在寄存器x0中，然后再将x0的值给返回给c语言的寄存器，此时虽然使用了x0，但是x0并不在input或者output的定义中，这种情况下我们就应当在clobber中声明x0；（**例4验证了它的必要性，如果用到了却没有声明，会引起结果的错误**）

clobber中也有两个特殊的参数：“cc”和“memory”（详参GCC 6.47.2.6 Clobbers and Scratch Registers）

> "cc"
>
> The "cc" clobber indicates that the assembler code modifies the flags register. On some machines, GCC represents the condition codes as a specific hardware register; "cc" serves to name this register. On other machines, condition code handling is different, and pecifying "cc" has no effect. But it is valid no matter what the target.

*cc：这个clobber指明了，汇编代码会改变标志寄存器；在一些平台上，gcc将条件代码表示为特定的硬件寄存器，cc就用于指代这些硬件寄存器；在别的平台上，条件代码的处理是不同的，这时候指定cc就没效果；但是无论目标是什么，cc都是一个合法的* 

“cc”貌似在ARM汇编里不起作用...至少在我举得例子里没有发现有什么作用；（**详细参照内联汇编例6**）

> "memory"
>
> The "memory" clobber tells the compiler that the assembly code performs memory reads or writes to items other than those listed in the input and output operands (for example, accessing the memory pointed to by one of the input parameters). To ensure memory contains correct values, GCC may need to flush specific register values to memory before executing the asm. Further, the* compiler does not assume that any values read from memory before an asm remain unchanged after that asm; it reloads them as needed. Using the "memory" clobber effectively forms a read/write memory barrier for the compiler. *Note that this clobber does not prevent the processor from doing speculative reads past the asm statement. To prevent that, you need processor-specific fence instructions.



### 内联汇编demo

#### 内联汇编例1：基础的使用方法

```c
asm(
    "mrs r0, cpsr\n\t" //每条指令的末尾要加"\n\t"
    "bic r0, r0, #0x80\n\t"
    "msr cpsr, r0"
    //这个例子中没有用到output那三个东西，都省略掉
);

```

#### 内联汇编例2：使用%n的方式代指参数

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

#### 内联汇编例3：为参数取一个名字

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
        int result_b, result_a, result_c;
        int a = 2, b = 2;
        asm(
                        "mrs %[result_b], nzcv\n\t"
                        "subs %[result_c], %[op1], %[op2]\n\t"
                        "mrs %[result_a], nzcv\n\t"
                        :[result_a] "=r" (result_a), [result_b] "=r" (result_b), [result_c] "=r"(result_c)
                        :[op1] "r" (a), [op2] "r" (b)
                        );
        printf("before=%x\nresult of calculate=%d\nafter=%x\n",result_b, result_c, result_a);
}
```

```shell
#输出为
pi@raspberrypi:~/test_asm $ ./test
hello_world
before=60000000
result of calculate=-1610612734
after=80000000
pi@raspberrypi:~/test_asm $ ./test
hello_world
before=60000000
result of calculate=-1610612734
after=80000000
pi@raspberrypi:~/test_asm $ ./test
hello_world
before=60000000
result of calculate=-1610612734
after=80000000
pi@raspberrypi:~/test_asm $
# 0110 0000 0000 0000 0000 0000 0000 0000表示在没有执行减法之前，nzvc是0110
# 1000 0000 0000 0000 0000 0000 0000 0000表示在执行减法运算之后，运算结果为负数,产生了借位
# 但是这里运算本身的结果是有问题的！
```

？有没有发现这里出现了一个问题，为什么参数a和b都是2，而在asm中进行了减法之后就变成了1610612734这样一个奇怪的值？我们需要分析一下是否是代码出现了错误

#### 内联汇编例6："cc"对状态寄存器的影响

```c
// without "cc"
#include "stdio.h"

void main()
{
        printf("hello_world\n");

        // ass
        int result_b, result_a, result_c;
        int a = 2, b = 1;
        asm(
                        "mrs %[result_b], nzcv\n\t"
                        "subs %[result_c], %[op1], %[op2]\n\t"
                        "mrs %[result_a], nzcv\n\t"
                        :[result_a] "+&r" (result_a), [result_b] "+&r" (result_b), [result_c] "+&r"(result_c)
                        :[op1] "r" (a), [op2] "r" (b)
                        );
        printf("before=%x\nresult of calculate=%d\nafter=%x\n",result_b, result_c, result_a);
}
```

```shell
## 输出
pi@raspberrypi:~/test_asm $ ./test
hello_world
before=60000000
result of calculate=1
after=20000000
```

```c
// with "cc"
#include "stdio.h"

void main()
{
        printf("hello_world\n");

        // ass
        int result_b, result_a, result_c;
        int a = 2, b = 1 ;
        asm(
                        "mrs %[result_b], nzcv\n\t"
                        "subs %[result_c], %[op1], %[op2]\n\t"
                        "mrs %[result_a], nzcv\n\t"
                        :[result_a] "+&r" (result_a), [result_b] "+&r" (result_b), [result_c] "+&r"(result_c)
                        :[op1] "r" (a), [op2] "r" (b)
                        :"cc"
                        );
        printf("before=%x\nresult of calculate=%d\nafter=%x\n",result_b, result_c, result_a);
}
```

```shell
## 输出
pi@raspberrypi:~/test_asm $ ./test
hello_world
before=60000000
result of calculate=1
after=20000000
```

这样看起来好像“cc”这个字段好像没什么用....





### 内联汇编代码分析（实例分析）

#### 内联汇编分析1：

有问题代码：

```c
#include "stdio.h"

void main()
{
        printf("hello_world\n");

        // ass
        int result_b, result_a, result_c;
        int a = 2, b = 2;
        asm(
                        "mrs %[result_b], nzcv\n\t"
                        "subs %[result_c], %[op1], %[op2]\n\t"
                        "mrs %[result_a], nzcv\n\t"
                        :[result_a] "=r" (result_a), [result_b] "=r" (result_b), [result_c] "=r"(result_c)
                        :[op1] "r" (a), [op2] "r" (b)
                        );
        printf("before=%x\nresult of calculate=%d\nafter=%x\n",result_b, result_c, result_a);
}
```

```shell
#输出为
pi@raspberrypi:~/test_asm $ ./test
hello_world
before=60000000
result of calculate=-1610612734
after=80000000
pi@raspberrypi:~/test_asm $
# 0110 0000 0000 0000 0000 0000 0000 0000表示在没有执行减法之前，nzvc是0110
# 1000 0000 0000 0000 0000 0000 0000 0000表示在执行减法运算之后，运算结果为负数,产生了借位
# 但是这里运算本身的结果是有问题的！
```

这是一个在 *内联汇编例5* 的时候遇到了一个问题：为什么参数a=2和参数b=2传入asm之后做subs，结果以参数result_c输出；为何result_c的结果不是0？

用gcc将这个案例翻译为汇编程序看看：

```shell
pi@raspberrypi:~/test_asm $ gcc -S test.c -o test.s
pi@raspberrypi:~/test_asm $ cat test.s
#...略
        ldr     w0, [sp, 44] # 将参数装入w0（x0）中
        ldr     w1, [sp, 40] # 将参数装入w1（x1）中
#APP
// 10 "test.c" 1
        mrs x1, nzcv #### 这里出现了问题，w0和w1目前应该是存放两个输入参数的地方，但是这里将nzcv的状态存入了x1
        subs x0, x0, x1 #### 然后又用x1进行了运算
        mrs x2, nzcv

// 0 "" 2
#NO_APP
  #...略
```

根据汇编的代码分析，在asm中，运算前nzcv的状态被存在了x1中，而x1原本是传输参数的寄存器（w1和x1是同一个寄存器	），这就导致了错误；（除去这个错误，还有一处错误，参与subs运算的应该是result_c,op1,op2这3个参数，但是通过汇编文件可以看出来实际上只有x0和x1两个寄存器参与了运算）

**这个错误的原因在于声明output寄存器时，使用了"=r"，但是"=r"仅仅声明了output要使用寄存器，且output是只读的；这两个限制条件并没有限制output不允许使用input使用过的寄存器，因此，gcc在处理asm语句的时候，使用了input中使用过的寄存器**

````c
#include "stdio.h"

void main()
{
        printf("hello_world\n");

        // ass
        int result_b, result_a, result_c;
        int a = 2, b = 2;
        asm(
                        "mrs %[result_b], nzcv\n\t"
                        "subs %[result_c], %[op1], %[op2]\n\t"
                        "mrs %[result_a], nzcv\n\t"
                        :[result_a] "+&r" (result_a), [result_b] "+&r" (result_b), [result_c] "+&r"(result_c)
                        :[op1] "r" (a), [op2] "r" (b)
                        );
        printf("before=%x\nresult of calculate=%d\nafter=%x\n",result_b, result_c, result_a);
}
````

```shell
pi@raspberrypi:~/test_asm $ ./test
hello_world
before=60000000
result of calculate=0
after=60000000
```

经过修改，减法结果输出正常

 

## 混合汇编

不同于内联汇编将一段汇编代码嵌入C语言程序中；混合汇编指的是在C语言代码中调用汇编语言写出来的文件，或者是在汇编代码中调用C语言写出来的文件；

混合汇编应当符合ATPCS规范；(ARM64应该符合AACPS，AACPS是ATPCS的一个改进版本，内容有差异，但是基本概念类似)



### ATPCS规则

（以下规则都是32位arm的规则，如果目标平台是v8，请参照ARMv8的寄存器说明）

#### 寄存器使用规范

在使用内联汇编的时候，应当遵守ATPCS规则，这个规则规定了寄存器的使用规范

1. 子程序之间传递参数时，如果参数数量小于4个，可以使用寄存器R0-R3传递参数，如果参数大于4个，多余的参数就要使用堆栈传递
2. r4-r11可被用于子程序内部保存局部变量；进入子程序之前应当保存这些寄存器的内容，退出子程序的时候应当恢复他们的初始值；
3. 寄存器r12被作为scratch寄存器，被记作ip，这种用法时常出现在 子程序代码段的连接中
4. r13是sp（所以说这些规则都是32位的规则，arm64中x13不是sp），r13只能用作sp
5. r14是lr，用于保存返回地址，如果子程序中在别的地方保存了返回地址，那么r14是可以用来放其余数据的
6. r15是pc，r15只能用做pc

#### 堆栈使用规范

1. ATPCS规定堆栈以FD（满递减堆栈）为标准
2. 规定堆栈以8字节对齐

关于FD：满：即堆栈指针指向最后入栈的数据；递减：即先入栈的位于高地址，后入栈的位于低地址

````shell
# 例：假设原本栈中已经有数据a，现在需要将数据b压入栈中
|  |......
| 数据a |0x18 <-指针指向
|  |0x10
|  |0x08
|  |0x00
# 数据b入栈后
|  |......
| 数据a |0x18 
| 数据b |0x10 <-指针指向
|  |0x08
|  |0x00
````

#### 参数传递规范

1. 如果参数数量在4个以内，则依次使用r0，r1，r2，r3传递参数

2. 如果参数数量大于4个，则前四个仍旧使用r0，r1，r2，r3；后续的参数使用堆栈传，且最后一个参数应当先入栈

   ````c
   // 例如：
   void func(int a, int b, int c, int d, int e, int f);
   //如果要传递参数，
   // a-> r0
   // b-> r1
   // c-> r2
   // d-> r3
   // f-> 入栈
   // e-> 入栈
   ````

**因此在写函数的时候尽量将函数的参数控制在4个以内，如果控制不住就用结构体压缩参数数量**

#### 参数返回规范

1. 如果返回的是一个32bits数据，使用r0；
2. 如果返回的是一个64bits数据，使用r0和r1
3. 如果位数更多，就要借助内存了



### AAPCS规则

大体上的思路接和ATPCS一致，但寄存器使用有差异，详参->寄存器



### 混合汇编demo：

（参照https://www.bilibili.com/video/BV1vS4y1q7fQ/?spm_id_from=333.788&vd_source=6b8fe2a721fda958c6ea9641e14f5327）

#### 混合汇编实例1：C语言调用汇编函数（add）

```c
//main_add.c
#include "stdio.h"

extern int add(int a, int b);

void main()
{
        int a=1;
        int b=2;
        int c;
        c = add(a, b);
        printf("a+b=%d",c);
}
```

```assembly
.global add # 这里要注意add一定要声明成全局符号，否则别的文件中无法引用它
add:
        add x2, x1, x0
        mov x0, x2
        ret
```

```shell
pi@raspberrypi:~/test_complex $ gcc main_add.c add.s -o main_add
pi@raspberrypi:~/test_complex $ ./main_add
a+b=3pi@raspberrypi:~/test_complex $
```

从结果来看是成功的运行了

#### 混合汇编实例2：C语言调用汇编函数（strcopy）

```c
//main.c
#include "stdio.h"

extern void strcopy(char* des, char* src);

void main()
{
        char* srcstr = "helloworld";
        char desstr[] = "test";
        strcopy(desstr,srcstr);
        printf("%s",desstr);
}
```

```assembly
# strcoyy.s
.global strcopy
strcopy:
        ldrb w2, [x1], #1
        strb w2, [x0], #1
        cmp w2, #0
        bne strcopy
        ret
```

```shell
pi@raspberrypi:~/test_complex_strcopy $ gcc main.c strcoyy.s -o main
pi@raspberrypi:~/test_complex_strcopy $ ./main
helloworldpi@raspberrypi:~/test_complex_strcopy $
```

这个例子其实还是值得分析的...有很多值得注意的点：

1. 在main函数调用strcopy时，第一个参数desster被放入x0中，第二个参数srcstr被放入了x1中，这就是AAPCS！
2. 在函数strcopy中，使用的是ldrb和strb，这两个指令是以byte为单位进行操作的，这是由于一个字母只占一个byte
3. 在函数strcopy中，ldrb于strb使用的是基地址寻址，`strb w2,[x0],#1`这句代码，每次执行x0 = x0 + 1；所以指针实际上是不断后移的
4. 在这个例子中字符串srcstr的长度大于字符串desstr的长度，但是strcopy仍旧复制成功了，因为例子中的汇编程序是按照内存指针操作的；不过这个操作是不安全的操作，因为很可能会改变预期外的内存中的数据；however it is funny！
5. 我这里这个例子的运行平台是ARMv8，所以返回的时候用了ret而非mov pc，lr；因为在ARMv8中pc已经不能被当操作数用了



#### 混合汇编实例3：汇编语言调用C函数

**实际上这才是最常用的形式...**

##### 1.在汇编中调用标准库的puts函数

本例来源于： https://stackoverflow.com/questions/8422287/how-to-call-c-functions-from-arm-assembly

```assembly
.extern exit, puts

.data
msg: .ascii "hello world"

.text
.global main
main:
        ldr x0, =msg
        bl puts
        mov x0, #0
        bl exit
```

执行结果

```shell
pi@raspberrypi:~/test_complex_c_call_ass $ gcc ass_call_puts.s -o ass_call_puts
pi@raspberrypi:~/test_complex_c_call_ass $ ./ass_call_puts
hello world
```

这个例子中有几个需要注意的点：

1. exit函数和puts函数并不是这个文件里定义的函数，这两个函数是来自于标准库的函数，因此需要使用extern说明
2. 这里例子中，程序是从main开始的，因为编译使用的是gcc，gcc会默认被编译的程序是从main开始执行的；如果将main替换位_start还坚持使用gcc，那么gcc就会报错
3. 如果不执行exit，汇编程序是不会退出的（在程序不发生错误的前提下）
4. 这个例子在调用puts时使用了x0传递参数；在调用exit时，也使用了x0传递参数；符合AAPCS



##### 2.在汇编中调用一个我们自己写的函数

```assembly
@  ass_call_addfunc.s
.extern exit, printf, add_func @声明 exit printf add_func是外部函数

.data
str: .ascii "%d" @ 这个字符串将被用于printf

.text
.global main
main:
        mov x0, #1
        mov x1, #2
        mov x2, #3
        mov x3, #4
        mov x4, #5 @ 这里的x0-x4这5个参数是add_func的参数，由于arm64遵守AAPCS，所以可以使用最多8个寄存器传递参数
        bl add_func

        mov x1, x0 @ add_func的返回值会被放在x0中，先将这个返回值保存在x1里；
        ldr x0, =str @ 准备调用printf，x0第一个参数表示字符串
        bl printf
       
        mov x0, #0
        b exit
```

```c
// add.c
int add_func(int a, int b,int c,int d,int e)
{
        return a + b + c + d + e;
}
```

```shell
pi@raspberrypi:~/test_complex_c_call_ass $ gcc ass_call_addfunc.s add.c -o ass_call_addfunc
pi@raspberrypi:~/test_complex_c_call_ass $ ./ass_call_addfunc
15
```



##### 3.在汇编中调用一个参数大于8个的函数

`````assembly
@  ass_call_addfunc.s
.extern exit, printf, add_func

.data
str: .ascii "%d"

.text
.global main
main:
        mov x0, #1
        mov x1, #2
        mov x2, #3
        mov x3, #4
        mov x4, #5
        mov x5, #6
        mov x6, #7
        mov x7, #8
        mov x8, #9 @ 这里虽然将9赋给了x8，但是x8是不会直接作为参数传递给add_func的
        str x8, [sp] @ 第九个参数的传递实际上依靠的是栈，这里将x8中的值加载到栈中，完成参数传递

        bl add_func

        mov x1, x0
        ldr x0, =str

        bl printf
        mov x0, #0
        b exit
`````

```c
int add_func(int a, int b,int c,int d,int e, int f,int g, int h, int i)
{
        return a + b + c + d + e + f + g + h + i;
}
```

```shell
pi@raspberrypi:~/test_complex_c_call_ass $ gcc ass_call_addfunc.s add.c -o ass_call_addfunc
pi@raspberrypi:~/test_complex_c_call_ass $ ./ass_call_addfunc
45
```






# isolation and system call entry exit

6s081文档

https://pdos.csail.mit.edu/6.828/2020/tools.html

## trap

`在用户代码中运行程序` 和 `在内核中执行程序` 之间的转换 称之为 `trap`

当进行内核调用，或者出现page fault，或者出现了中断 使得当前程序需要响应内核设备驱动；者之间出现的内核态和用户态之间的切换称为 trap；



## 硬件部分的支持

CPU中包含很多硬件上的设计以支持模式的切换；这些设计大多体现在寄存器上

### pc寄存器

程序计数器

### MODE标志位

表明当前是用户模式还是内核模式

当处于用户空间的时候，这个标志位对应user mode；

在处于内核空间的时候，这个标志位对应supervision mode；

当处于管理者模式的时候，确实会获得一些特权

1. 其中的一项特权是可以读写控制寄存器，例如可以读写SATP寄存器，可以读写SEPC，SATP......
2. 还有，处于supervision mode的时候可以使用PTE_U没有被设置的page table；

### SATP寄存器

该寄存器指向页表

 ### SEPC寄存器

在trap过程中保存程序计数器的值，可以使用这个值跳回到用户进程



### STVEC寄存器

指向处理trap指令的起始地址，也就是保存`rampoline page`的地址；详情请参照trap的过程

### SSCRATCH寄存器

 和STVEC寄存器类似，SSRATCH用于保存`trapframe page`的地址

## trap过程

### 进入内核模式的过程

-----------------------



### 用户空间->ecall->trampoline->usertrap

在trap的最开始，cpu所有的状态都设置成运行用户代码的状态，而非运行内核代码的状态；

以write为例

write -> ecall -> uservec -> usertrap -> syscall -> sys_write

`ecall`会切换到具有supervisor mode的内核中。

`uservec`位于`kernel/trampoline.S`是一个汇编函数

`usertrap`位于`kernel/trap.c`

`syscall`函数就会根据传入的系统调用号去查找对应的函数，针对这个例子就是sys_write函数；



返回用户空间：

usertrapret 

`usertrapret`也位于trap.c

最终还需要`trampoline.S`中的`userret`来恢复ecall之后的调用；



使用gdb追踪这个过程，追踪sh.c中的write函数

在编译后，sh.c会生成一个sh.asm，通过这个文件可以查看指令的地址

```assembly
0000000000000de2 <write>:
.global write
write:
 li a7, SYS_write
     de2:       48c1                    li      a7,16
 ecall # 从这里确定，ecall的地址是0x0de4
     de4:       00000073                ecall
 ret
     de8:       8082                    ret
```

```shell
# gdb操作

# 在ecall处设置一个断点
(gdb) b *0x0de4  # 在内存地址0x0de4设置一个断点
Breakpoint 1 at 0xde4
(gdb) c
Continuing.
[Switching to Thread 1.3]

Thread 3 hit Breakpoint 1, 0x0000000000000de4 in ?? ()
=> 0x0000000000000de4:  00000073                ecall # 这里可以看到成功的命中断点，下一个命令就是ecall命令

# 打印当前的寄存器值
(gdb) info reg # 打印全部的寄存器内容
ra             0xe8c    0xe8c
sp             0x3e90   0x3e90
gp             0x505050505050505        0x505050505050505
tp             0x505050505050505        0x505050505050505
t0             0x505050505050505        361700864190383365
t1             0x505050505050505        361700864190383365
t2             0x505050505050505        361700864190383365
fp             0x3eb0   0x3eb0
s1             0x12f1   4849
a0             0x2      2 # write的第一个参数： 文件描述符
a1             0x3e9f   16031 # write的第二个参数，要输出的字符串的地址
a2             0x1      1
a3             0x505050505050505        361700864190383365
a4             0x505050505050505        361700864190383365
a5             0x24     36
a6             0x505050505050505        361700864190383365
a7             0x10     16
s2             0x24     36
s3             0x0      0
s4             0x25     37
s5             0x2      2
s6             0x3f50   16208
s7             0x1438   5176
s8             0x64     100
s9             0x6c     108
s10            0x78     120
s11            0x70     112
t3             0x505050505050505        361700864190383365
t4             0x505050505050505        361700864190383365
t5             0x505050505050505        361700864190383365
t6             0x505050505050505        361700864190383365
pc             0xde4    0xde4

# 来看一看a1寄存器中的指针指向的内存中的内容
(gdb) x/2c $a1 # examine 指令缩写为x ，用于打印内存中的值
0x3e9f: 36 '$'  48 '0'

# 看一看satp中的值
(gdb) print/x $satp # /x表示以16进制打印
$2 = 0x8000000000087f63
```

需要注意的是satp中的值是一个物理地址，这个寄存器并不会告诉我们虚拟地址和物理地址之间的映射关系；

我们使用的qemu模拟器可以打印当前的页表

```shell
# 在qemu中按下ctrl+a c，进入console模式
(qemu) info mem
vaddr            paddr            size             attr
---------------- ---------------- ---------------- -------
0000000000000000 0000000087f60000 0000000000001000 rwxu-a-
0000000000001000 0000000087f5d000 0000000000001000 rwxu-a-
# 0x2000这个page是一个guard page，用来防止进程使用过多的stack page（防止越位）
# 注意看这个guard page的标志位，u没有被设置，因此用户模式下，不能访问这个page
# 如果访问了，就会产生page fault，这也是一种保护
0000000000002000 0000000087f5c000 0000000000001000 rwx----
0000000000003000 0000000087f5b000 0000000000001000 rwxu-ad
# 下面这两个page的虚拟地址很大，他们是trampoline trapframe，几乎位于虚拟地址的顶端，用来to switch to the kernel
0000003fffffe000 0000000087f6f000 0000000000001000 rw---ad
0000003ffffff000 0000000080007000 0000000000001000 r-x--a-
(qemu)
```

接下来我们向下单执行一步，观察pc寄存器的变化

```shell
(gdb) print $pc
$3 = (void (*)()) 0xde4

(gdb) stepi
0x0000003ffffff000 in ?? ()
=> 0x0000003ffffff000:  14051573                csrrw   a0,sscratch,a0

(gdb) print $pc
$4 = (void (*)()) 0x3ffffff000
```

**可以见到，在执行了ecall之后，程序计数器的值变得很大**

**对比qemu输出的页表信息，会发现这个0x3ffffff000就是trampoline page**

解下来我们可以打印出0x3ffffff000这个地址后面的指令，看看接下来程序要干什么

```shell
(gdb) x/6i 0x3ffffff000
=> 0x3ffffff000:        csrrw   a0,sscratch,a0
   0x3ffffff004:        sd      ra,40(a0)
   0x3ffffff008:        sd      sp,48(a0)
   0x3ffffff00c:        sd      gp,56(a0)
   0x3ffffff010:        sd      tp,64(a0)
   0x3ffffff014:        sd      t0,72(a0)
(gdb)
```

对比`kernel/trampoline.S`，会发现我们将要执行`uservec`函数

ecall本身不会切换page table，这意味着trap的处理代码必须存在于每一个用户页表中，否则就存在找不到trap处理代码的风险，这就是`trampoline page`，它由kernel小心的映射到每一个user page table中，以保证内核能够执行trap机制的最初的一些指令；

至于为什么trampoline是0x3ffffff000？ 这个地址由STVEC寄存器所设置

```shell
(gdb) print/x $stvec
$6 = 0x3ffffff000
```

**必须强调的是，尽管trampoline在user page table中被映射，但是想要访问这段内容，必须使用supervisor mode，从PTE_U就可以看出来**

ecall的工作只有三项：

1. 设置supervisor mode
2. 保存sepc
3. 将stvec寄存器中保存的地址加载到pc中

此时距离能够执行内核中的c语言代码还有很长一段路要走，比如我们至少要切换kernel page table指针，搞一块kernel stack frame，然后还要跳转到kernel c代码...

有一些架构确实会用ecall完成上述工作，但是riscv不会；riscv觉得应该给软件足够的自由；

接下来的一个关键问题是，ecall之后，通用寄存器是不会发生变化的，所以ecall之后，需要将通用寄存器的内容保存下来。否则一旦使用这些通用寄存器，就会覆盖原来的值，导致无法恢复现场；

xv6有一个`trapframe page`，地址是0x0000003fffffe000，可以将32个寄存器的内容放在这块内存中；（trapframe page的地址是保存在SSRATCH寄存器中的）

同时定义了一个`trapframe`结构体，该数据结构定义在`kernel/proc.h`中

```c
//这个结构体的注释中还标注了偏移地址
struct trapframe {
  /*   0 */ uint64 kernel_satp;   // kernel page table
  /*   8 */ uint64 kernel_sp;     // top of process's kernel stack
  /*  16 */ uint64 kernel_trap;   // usertrap()
  /*  24 */ uint64 epc;           // saved user program counter
  /*  32 */ uint64 kernel_hartid; // saved kernel tp
  /*  40 */ uint64 ra;
  /*  48 */ uint64 sp;
  /*  56 */ uint64 gp;
  /*  64 */ uint64 tp;
  /*  72 */ uint64 t0;
  /*  80 */ uint64 t1;
  /*  88 */ uint64 t2;
  /*  96 */ uint64 s0;
  /* 104 */ uint64 s1;
  /* 112 */ uint64 a0;
  /* 120 */ uint64 a1;
  /* 128 */ uint64 a2;
  /* 136 */ uint64 a3;
  /* 144 */ uint64 a4;
  /* 152 */ uint64 a5;
  /* 160 */ uint64 a6;
  /* 168 */ uint64 a7;
  /* 176 */ uint64 s2;
  /* 184 */ uint64 s3;
  /* 192 */ uint64 s4;
  /* 200 */ uint64 s5;
  /* 208 */ uint64 s6;
  /* 216 */ uint64 s7;
  /* 224 */ uint64 s8;
  /* 232 */ uint64 s9;
  /* 240 */ uint64 s10;
  /* 248 */ uint64 s11;
  /* 256 */ uint64 t3;
  /* 264 */ uint64 t4;
  /* 272 */ uint64 t5;
  /* 280 */ uint64 t6;
};
```

通过执行`uservec`函数，将寄存器的值存在trapframe page里；

```assembly
.globl uservec
uservec:
        csrrw a0, sscratch, a0 # 交换a0和sscratch的值，
        # save the user registers in TRAPFRAME
        sd ra, 40(a0) # 将ra中的值 放到a0+40地址中
       	#...后续操作同理

        # save the user a0 in p->trapframe->a0
        csrr t0, sscratch #将a0原本的值放到p->trapframe->a0中
        sd t0, 112(a0)

        # restore kernel stack pointer from p->trapframe->kernel_sp
        ld sp, 8(a0)

        # make tp hold the current hartid, from p->trapframe->kernel_hartid
        ld tp, 32(a0)

        # load the address of usertrap(), p->trapframe->kernel_trap
        ld t0, 16(a0)

        # restore kernel page table from p->trapframe->kernel_satp
        ld t1, 0(a0) # 将a0+0中的值放到t1里，a0+0中的值是kernel_satp
        csrw satp, t1 # 把kernel_satp放到satp寄存器中，使之生效
        # csrw之后，我们就从user page table切换到了kernel page table 中
        sfence.vma zero, zero

        # a0 is no longer valid, since the kernel page
        # table does not specially map p->tf.

        # jump to usertrap(), which does not return
        jr t0 # 跳转到usertrap函数，这个函数的地址也是固定的
```

**这里隐藏了一个问题：为什么我们从user page table切换到了kernel page table，页表都发生了变化，为什么虚拟地址还能用，程序还没有崩溃？**

答案是这个切换过程发生在trampoline.S中，trampoline代码在用户空间和内核空间中，都被映射到了同一个地址，所以页表的切换没有影响到这个程序；



让我们继续，`uservec`函数最后通过`jr t0`转跳到了`usertrap`函数，这是一个C语言函数，在`kernel/trap.c`中；

### usertrap()

很多种情况下都会进入usertrap函数，比如，中断，除零错误，使用一个未被映射的虚拟地址等等；因此usertrap需要考虑的情况还是挺多的...甚至我们还可以从kernel中触发trap，不过这种情况我们暂时不讨论，从kernel中触发trap的处理过程和从用户空间触发的trap区别还是比较大的；

```c
//从用户空间触发的trap会来到这个函数中
void
usertrap(void)
{
  int which_dev = 0;

  if((r_sstatus() & SSTATUS_SPP) != 0)
    panic("usertrap: not from user mode");

  // send interrupts and exceptions to kerneltrap(),
  // since we're now in the kernel.
  w_stvec((uint64)kernelvec); //写stvec寄存器，将其指向kernelvec变量，这个值是内核空间处理trap的起始地址
  // ！！ 为什么这里需要对stevc的值进行修改？
  // 正如之前所言，我们不止可以在用户空间引发trap，也可以在内核空间引发trap
  // 我们目前正位于内核态，如果此时有中断之类的事触发了trap，而我们又没有处理stvec中的值时；我们将会跳转到用户空间用于处理trap的代码中
  // 而不幸的是，xv6针对用户态/内核态引发的trap的处理机制不一样；

  struct proc *p = myproc(); // 拿到当前进程

  // save user program counter.
  p->trapframe->epc = r_sepc(); // 存储sepc，因为程序在内核中执行的时候，有可能会切换到另一个进程，此时sepc就会被覆写，为了防止这种事情发生，我们需要留存一个副本

  if(r_scause() == 8){ // 查看当前的trap是什么原因引起的，编号8就代表trap来自system call
    // system call

    if(p->killed)
      exit(-1);

    // sepc points to the ecall instruction,
    // but we want to return to the next instruction.
    p->trapframe->epc += 4; // 设置sepc = sepc + 4,因为我们返回到用户空间之后需要跳过ecall，如果不+4的话，ecall又会被执行一次，我们就会陷入死循环

    // an interrupt will change sstatus &c registers,
    // so don't enable until done with those registers.
    intr_on(); // 使能中断，因为中断会被trap关闭，而有些系统调用又很费时间，为了防止在这期间中断无法使用，我们需要手动打开中断

    syscall(); // syscall，这个就很熟悉了
  } else if((which_dev = devintr()) != 0){
    // ok
  } else {
    printf("usertrap(): unexpected scause %p pid=%d\n", r_scause(), p->pid);
    printf("            sepc=%p stval=%p\n", r_sepc(), r_stval());
    p->killed = 1;
  }

  if(p->killed)
    exit(-1);

  // give up the CPU if this is a timer interrupt.
  if(which_dev == 2)
    yield();

  usertrapret();
}
```



### 接下来我们进入返回用户模式的过程

-------------------------------



### usertrapret()

在完成系统调用后，`usertrap`将会执行`usertrapret`以返回用户空间

```c
usertrapret(void)
{
  struct proc *p = myproc();

  // we're about to switch the destination of traps from
  // kerneltrap() to usertrap(), so turn off interrupts until
  // we're back in user space, where usertrap() is correct.
  intr_off(); //关闭中断，这个过程中一旦发生中断，会导致一些关键寄存器被覆写从而导致严重的错误

  // send syscalls, interrupts, and exceptions to trampoline.S
  w_stvec(TRAMPOLINE + (uservec - trampoline)); // 将stevc的值恢复为 用户空间用于处理trap的代码所在的位置

  // set up trapframe values that uservec will need when
  // the process next re-enters the kernel.
  p->trapframe->kernel_satp = r_satp();         // kernel page table
  p->trapframe->kernel_sp = p->kstack + PGSIZE; // process's kernel stack
  p->trapframe->kernel_trap = (uint64)usertrap;
  p->trapframe->kernel_hartid = r_tp();         // hartid for cpuid()

  // set up the registers that trampoline.S's sret will use
  // to get to user space.

  // set S Previous Privilege mode to User.
  unsigned long x = r_sstatus();
  x &= ~SSTATUS_SPP; // clear SPP to 0 for user mode
  x |= SSTATUS_SPIE; // enable interrupts in user mode
  w_sstatus(x); // 这里设置了一些标志位，这些标志位将在sret指令执行时发挥作用

  // set S Exception Program Counter to the saved user pc.
  w_sepc(p->trapframe->epc); // 将保存的sepc寄存器的值重新放到sepc寄存器中

  // tell trampoline.S the user page table to switch to.
  uint64 satp = MAKE_SATP(p->pagetable);

  // jump to trampoline.S at the top of memory, which
  // switches to the user page table, restores user registers,
  // and switches to user mode with sret.
  uint64 fn = TRAMPOLINE + (userret - trampoline);
  ((void (*)(uint64,uint64))fn)(TRAPFRAME, satp);// fn是一个地址，这里的执行方式是以函数指针的方式执行的，fn指向的是trampoline中的userret函数，同时传入两个参数，这两个参数会被存在a0和a1寄存器中
}
```

### userret

```assembly
.globl userret
userret:
        # userret(TRAPFRAME, pagetable)
        # switch from kernel to user.
        # usertrapret() calls here.
        # a0: TRAPFRAME, in user page table.
        # a1: user page table, for satp.

        # switch to the user page table.
        csrw satp, a1 # 切换页表，a1是我们传递进来的参数，指向用户页表
        sfence.vma zero, zero

        # put the saved user a0 in sscratch, so we
        # can swap it with our a0 (TRAPFRAME) in the last step.
        ld t0, 112(a0) 
        csrw sscratch, t0

        # restore all but a0 from TRAPFRAME
        ld ra, 40(a0)
        ld sp, 48(a0)
        ld gp, 56(a0)
        ld tp, 64(a0)
        ld t0, 72(a0)
        ld t1, 80(a0)
        ld t2, 88(a0)
        ld s0, 96(a0)
        ld s1, 104(a0)
        ld a1, 120(a0)
        ld a2, 128(a0)
        ld a3, 136(a0)
        ld a4, 144(a0)
        ld a5, 152(a0)
        ld a6, 160(a0)
        ld a7, 168(a0)
        ld s2, 176(a0)
        ld s3, 184(a0)
        ld s4, 192(a0)
        ld s5, 200(a0)
        ld s6, 208(a0)
        ld s7, 216(a0)
        ld s8, 224(a0)
        ld s9, 232(a0)
        ld s10, 240(a0)
        ld s11, 248(a0)
        ld t3, 256(a0)
        ld t4, 264(a0)
        ld t5, 272(a0)
        ld t6, 280(a0)

        # restore user a0, and save TRAPFRAME in sscratch
        csrrw a0, sscratch, a0

        # return to user mode and user pc.
        # usertrapret() set up sstatus and sepc.
        sret
```

总的来说这个函数在按照我们之前保存在`trapframe page`中的值恢复寄存器的值；

`sret`指令会

1. 将sepc中的值复制到pc中
2. 允许中断发生
3. 切换到user mode

然后一个系统调用就完成了



### 最后的问题：用户程序如何拿到系统调用的返回值？

**结合write调用的实例，如果你去看sys_write的实现，会发现我们之前保存在trapframe中的a0的值被覆写了，这是故意的，这也是系统调用向用户空间传递返回值的方法**

```assembly
.global write
write:
 li a7, SYS_write
     de2:       48c1                    li      a7,16
 ecall
     de4:       00000073                ecall
 ret
     de8:       8082                    ret
```


















































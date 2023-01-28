###  从源码开始构建u-boot

# 准备工作



## 获取源码

```shell
git clone https://source.denx.de/u-boot/u-boot.git
```

(https://www.denx.de/wiki/U-Boot)这里附上u-boot的官网网址，如有需要请访问官方网站；

git上拉下来的代码分支是master，切换到离我最近的版本，2021.10发布的版本；

```
git checkout v2021.10
```

## u-boot关于CPU与board的代码

首先需要区分什么是CPU什么是外围电路，关于CPU有一个具体的型号，查阅开发板资料就可以找到；外围电路包含了I2C，UART串口等等信息，以树莓派4b为例，他的CPU型号是arm架构的BCM2835（注：实际上我用的树莓派4b应该不是BCM2835而是BCM2711，不过不知为何sysinfo中显示cpu是2835，后面的手册将均使用2711的手册），这块CPU属ARM-CortexA53（Armv8）架构；

（关于arm的各种名词，ARMv8指的是一种指令集架构，而Cortex是一种内核名称，这里简单介绍一下：在armv7之前的内核命名方式都是以数字命名的，例如ARM7，ARM9，ARM11，实际上他们的指令集架构都是在ARMv7之前的；ARMv7推出后，核心的命名方式发生了变化，有了我们熟悉的Cortex-A，Cortex-R，Cortex-M的划分）

### 关于CPU的文件

```
路径/u-boot/arch/arm/cpu/armv8
Kconfig            fel_utils.S                       smccc-call.S		
Makefile           fsl-layerscape                    spin_table.c
bcmns3             fwcall.c                          spin_table_v8.S
cache.S            generic_timer.c                   spl_data.c
cache_v8.c         hisilicon                         start.S
config.mk          linux-kernel-image-header-vars.h  tlb.S
cpu-dt.c           lowlevel_init.S                   transition.S
cpu.c              psci.S                            u-boot-spl.lds
exception_level.c  sec_firmware.c                    u-boot.lds
exceptions.S       sec_firmware_asm.S                xen
```

(总的来说这个路径下还是有不少文件的...however我们并不用每个都打开看看)

这些文件中，需要特别注意文件 start.S这个文件是uboot的整个流程的起点，第一行代码就在start.S中；

### 关于外围电路（Board）的文件

外围类似PC中的南桥，基本上可以理解为低速设备总线，usb，i2c，uart等等设备的代码会被放在board中；

```
/u-boot/board/raspberrypi
```

这部分代码通常都会被在board中归类存放，找起来也很简单，只需要按照厂商的名字搜索即可；



## 启动流程（BL0，BL1，BL2...）

一般而言，上电之后芯片会有如下的操作流程（当然，各个型号的CPU/开发板/启动流程都不尽相同，但是大多都遵循着分步骤启动的原则）

### step1

BL0，它会初始化一些外围电路和watch dog 等等（BL0通常是芯片中自带的很小很小的一段程序）；然后他会将存储介质（例如sd卡）中的头4k内容移动到片内存储中；（存储介质的前4k被称为BL1）

### step2

BL1代码开始执行，但4k的代码不足以完成整个启动，因此它的主要任务还不是真正的启动；他的主要内容如下：

1. 判断一下BL1（他自己）是处在SDRAM内存当中还是处在静态内存SRAM

   中，如果是在SRAM静态内存中，BL1会初始化一块更大的内存（SDRAM）

2. 将存储介质中4k后面的部分（BL2）加载到上述初始化的SDRAM内存中

3. 将程序入口跳转到BL2

### step3

BL2会将真正的OS拷贝到内存中，然后将程序的入口跳转到OS

## 为什么会有u-boot-spl.bin和u-boot.bin?

通常，上述的BL1与BL2会被合成为一个文件：uboot.bin；这个文件会被烧录在flash或sd卡中；

（spl-> second program loader  二级程序加载器）

同时，有的时候uboot也会被分成两个部分，第一个部分BL1，第二个部分BL2，BL1被称为u-boot-spl.bin一般比较小，但是有比4k大；此时BL1会跳过BL2，直接去初始化SDRAM，然后将剩余的部分加载到SDRAM运行，相当于抢占了BL2的一些工作，直接将整个uboot按照“准备工作”部分和“实际运行”部分进行了划分；

## 异常地址的映射

根据ARM的规则，如果发生异常，那么要跳转到0x0000 0000 进行异常处理；但实际上0x0000 0000 这个地址通常都是BL0是ROM（read only mem），我们甚至都无法修改，这就牵扯出了一个问题，我们要如何处理异常？

### 当程序运行在片内内存SRAM中时候

有的芯片会单独的规划出一片内存做异常处理向量表；此时如果发生异常，程序就不会跳转到0x 0000 0000 而是跳转到芯片所规划的异常向量表，此时你可以选择写代码的时候将异常处理代码拷贝到芯片指定的内存地址（异常处理向量表）之处；

### 当程序运行在SDRAM中的时候

ARM为我们考虑了这个方面，在CP15协处理器中，有一个叫做VBAR的寄存器。这个寄存器中的地址被配置好之后，如果再出现异常，异常会跳转到VBAR中存的地址中去；

# 一些杂记



## 关于哈佛结构和冯诺依曼结构

哈佛结构中，有两块独立的存储机构，一块负责存储指令，一块负责存储数据；这样做的缺点是，这两块独立的存储机构，均需要和CPU进行交流，以32位机为例，他们各自都需要有32根地址总线和32根数据总线；这样走线的花销太大，但是不可否认的是，这样的速度相对较快；

冯诺依曼认为，指令本身也是一种数据，所以不需要两个独立的存储机构，只需要一块存储，这块存储中即保存有指令，又保存有数据（也就是我们更熟悉的代码段和数据段），当一段程序运行的时候，只需要把指令和数据都加载到一块内存中，那么就只需要一组32位地址总线和32位数据总线即可，冯诺依曼结构也是我们当前PC使用的结构，这个结构可能性高，但是相对而言速度没有哈佛高；为了弥补速度差距，使用了cache，所有的数据在进入cpu之前会进入cache中进行备份，实际上程序中的很多数据都是短时间内被多次使用的，所以cache这种设计提高了速度；

那么ARM是什么结构？早期ARM使用的是冯诺依曼结构，因为那么时候arm的核心速度比较低，根本没有必要搞哈佛；但是随着arm的核心速度变快，arm采取了，片外使用冯诺依曼，片内使用哈佛结构的设计，它拥有两个独立的cache：i_cache和d_cache，前者是代码cache，后者是数据cache；**这也是uboot在初始化时会清理d_cache和i_cache的原因，因为在这个阶段还没有完全的区分代码段和数据段，所以有些数据会被缓存在错误的地方，导致cache中的内容和ram中的内容不一致；**



## 分支预测

对arm而言，每当执行一个指令的时候，后几条指令就已经被读取到了流水线中，等待被执行；

但是实际上由于代码中经常使用循环和判断，使原本取到流水线中的代码失效（例如，执行循环操作时，本来流水线中已经加载了循环之后的代码，但是由于没能跳出循环，导致已经被加载的指令无法被执行，还需要卸载掉，重新加载下一次循环有关的指令）；

为了减少这中浪费，cpu使用了分支预测，分支预测的实现方式有多种，但是本质上都是为了减少上述情况下的效率浪费；

**但是无论如何，arm的流水线决定了当前代码执行的时候，后续的指令已经被装填，因此在进行初始化的时候，有时必须要清空分支中已经被加载的指令，防止有指令被错误的执行；**

## 开漏（开集）输出&推挽输出

### 开漏或开集

指的是，对三极管的集电极或者MOS管的漏极作为输出时，加上拉电阻，防止三极管关断时，输出的值因为浮空而不能确定；

当加上 上拉电阻 的时候，一旦处于关断的阶段，那么输出就会变成高电位；

### 推挽（push-pull）

推挽使用了两个互补的npn与pnp三极管，基极如果施加导通电压，就会有一个管子输出高电平，另一个管子截至，如果基极施加低电压，则有一个管子输出低电平，另一个管子截至，使用这种方式基本消灭了不定的状态



# 开始编译

## 交叉编译

首先我们需要明确，树莓派使用的核心是arm架构的，而非传统x86架构，架构的不同导致如果不做任何特殊处理，在x86平台上编译出来的东西在arm平台上是无法正常使用的；

当然可以选择直接在arm平台上进行编译，但是鉴于x86高性能的优势，所以一般情况下我们还是选择交叉编译（即，在x86平台上编译产生arm平台上的文件）

### 制作配置文件

在真正的make之前需要生成关于树莓派的配置文件，这些文件位于路径：u-boot/configs/下

```shell
LAPTOP-55A4PF8J% ls |grep rpi
rpi_0_w_defconfig
rpi_2_defconfig
rpi_3_32b_defconfig
rpi_3_b_plus_defconfig
rpi_3_defconfig
rpi_4_32b_defconfig
rpi_4_defconfig
rpi_arm64_defconfig
rpi_defconfig
LAPTOP-55A4PF8J%
```

我们选择rpi_4_defconfig，在uboot的根目录下执行

make rpi_4_defconfig

```
LAPTOP-55A4PF8J% make rpi_4_defconfig
  YACC    scripts/kconfig/zconf.tab.c
  LEX     scripts/kconfig/zconf.lex.c
  HOSTCC  scripts/kconfig/zconf.tab.o
  HOSTLD  scripts/kconfig/conf
#
# configuration written to .config
#
LAPTOP-55A4PF8J%
```

这个过程中如果报错，缺少库，安装对应的库即可

### 编译产生结果

安装交叉编译的工具

```
sudo apt install gcc-aarch64-linux-gnu
```

**设置一个环境变量**(这个环境变量会告诉make接下来的工作要用什么编译器进行捏**这个步骤很重要**)

```
export CROSS_COMPILE=aarch64-linux-gnu-
##然后make即可
make -j 12
##使用12个线程进行编译
```

等待编译完成，如果中间有提示缺少什么文件，安装对应的开发库即可；

编译完成后会在uboot的根目录下发现u-boot.bin文件

## 编译生成的结果

编译会生成两个比较重要的东西，u-boot和u-boot.bin

u-boot是比较大的，包含了一些地址信息，标号信息等调试信息

u-boot.bin就是最后我们使用的文件，它是很紧凑的代码

## 如何使用objdump分析生成的结果

使用

```
 aarch64-linux-gnu-objdump -S u-boot |less
 ## less 可以让我们进行随意的翻页查看
```

# uboot代码分析



```
/u-boot/arch/arm/cpu/armv8/start.S
```

整个uboot的运行都是从这个文件开始的

分析：

### inlcude文件

```c
#include <asm-offsets.h>
#include <config.h>
#include <linux/linkage.h>
#include <asm/macro.h>
#include <asm/armv8/mmu.h>

///lifugui：注意include的文件，这些文件一般有两个路径
///1.是uboot根目录下方的include文件夹
///2.是arch/arm/include
```

(至于为什么要去这两个地方找include文件，这是makefile里规定的，后面会讲到)

### _start开始

```assembly
正式开始:(编辑器不能正确显示汇编与C混合的语法高亮...)

.globl	_start
_start:
#if defined(CONFIG_LINUX_KERNEL_IMAGE_HEADER)
#include <asm/boot0-linux-kernel-header.h>
#elif defined(CONFIG_ENABLE_ARM_SOC_BOOT0_HOOK)
/*
 * Various SoCs need something special and SoC-specific up front in
 * order to boot, allow them to set that in their boot0.h file and then
 * use it here.
 */
/*
lifugui:首先判定CONFIG_LINUX_KERNEL_IMAGE_HEADER，这个东西和EFI加载有关，他会为uboot的头添加一些关于大小端，数据段，文本段大小的信息，以便EFI相关的加载器获取信息
*/
/*
lifugui:某些soc根据要求需要在bootloader头有hook来指导BL0,如果存在这个要求的话就会引用boot0.h并且不会执行 b reset
*/
#include <asm/arch/boot0.h>
#else
	b	reset
	/*
	如果没有上述的复杂情况，就会直接进行到这里执行b reset
	*/
#endif

        
/*-----------------------------------------------------*/
	.align 3///这里使用align 3保持一个8字节强制对齐

/*lifugui:这里定义了_TEXT_BASE，_end_ofs，_bss_start_ofs，_bss_end_ofs
_TEXT_BASE是做什么用的？
答：这是u-boot被拷贝到SDRAM内存中的起始地址
根据objdump产生的反汇编代码我们可以看到_TEXT_BASE的值为00080000
	0000000000080008 <_TEXT_BASE>:
   80008:       00080000        .word   0x00080000
   8000c:       00000000        .word   0x00000000
   从
   */
.globl	_TEXT_BASE
_TEXT_BASE:
	.quad	CONFIG_SYS_TEXT_BASE

/*
 * These are defined in the linker script.
 */
.globl	_end_ofs
_end_ofs:
	.quad	_end - _start

.globl	_bss_start_ofs
_bss_start_ofs:
	.quad	__bss_start - _start

.globl	_bss_end_ofs
_bss_end_ofs:
	.quad	__bss_end - _start


```

### reset

```assembly
reset:
	/* Allow the board to save important registers */
	b	save_boot_params
	/*
	lifugui:从代码上来看这个save_boot_params仅仅是跳转了一下然后又跳转回来了；save_boot_params的作用在于保存一些board相关的寄存器，从代码中也会发现这个函数实际上被定义为了weak，也就是说如果真的需要它，那么它会被定义在别的地方；如果这块板子有需要，那么它一般被定义在lowlevel.S中
	*/

/*
lifugui:save_boot_params_ret的目标在于4K对齐，不过从objdump的结果看来，并没有用到这个部分
*/
.globl	save_boot_params_ret
save_boot_params_ret:

#if CONFIG_POSITION_INDEPENDENT
	/* Verify that we're 4K aligned.  */
	adr	x0, _start
	ands	x0, x0, #0xfff
	b.eq	1f
0:
	/*
	 * FATAL, can't continue.
	 * U-Boot needs to be loaded at a 4K aligned address.
	 *
	 * We use ADRP and ADD to load some symbol addresses during startup.
	 * The ADD uses an absolute (non pc-relative) lo12 relocation
	 * thus requiring 4K alignment.
	 */
	wfi
	b	0b
1:

	/*
	 * Fix .rela.dyn relocations. This allows U-Boot to be loaded to and
	 * executed at a different address than it was linked at.
	 */
pie_fixup:
	adr	x0, _start		/* x0 <- Runtime value of _start */
	ldr	x1, _TEXT_BASE		/* x1 <- Linked value of _start */
	subs	x9, x0, x1		/* x9 <- Run-vs-link offset */
	beq	pie_fixup_done
	adrp    x2, __rel_dyn_start     /* x2 <- Runtime &__rel_dyn_start */
	add     x2, x2, #:lo12:__rel_dyn_start
	adrp    x3, __rel_dyn_end       /* x3 <- Runtime &__rel_dyn_end */
	add     x3, x3, #:lo12:__rel_dyn_end
pie_fix_loop:
	ldp	x0, x1, [x2], #16	/* (x0, x1) <- (Link location, fixup) */
	ldr	x4, [x2], #8		/* x4 <- addend */
	cmp	w1, #1027		/* relative fixup? */
	bne	pie_skip_reloc
	/* relative fix: store addend plus offset at dest location */
	add	x0, x0, x9
	add	x4, x4, x9
	str	x4, [x0]
pie_skip_reloc:
	cmp	x2, x3
	b.lo	pie_fix_loop
pie_fixup_done:
#endif

/*...省略...*/

WEAK(save_boot_params)
	b	save_boot_params_ret 
	/*lifugui:这里又会跳转回去save_boot_params_ret*/
ENDPROC(save_boot_params)

```

### spl阶段的异常向量表

```assembly
#ifdef CONFIG_SYS_RESET_SCTRL
	bl reset_sctrl 
#endif

#if defined(CONFIG_ARMV8_SPL_EXCEPTION_VECTORS) || !defined(CONFIG_SPL_BUILD)
.macro	set_vbar, regname, reg
	msr	\regname, \reg
.endm
	adr	x0, vectors
#else
.macro	set_vbar, regname, reg
.endm
#endif
	/*
	 * Could be EL3/EL2/EL1, Initial State:
	 * Little Endian, MMU Disabled, i/dCache Disabled
	 */
	switch_el x1, 3f, 2f, 1f
3:	set_vbar vbar_el3, x0
	mrs	x0, scr_el3
	orr	x0, x0, #0xf			/* SCR_EL3.NS|IRQ|FIQ|EA */
	msr	scr_el3, x0
	msr	cptr_el3, xzr			/* Enable FP/SIMD */
	b	0f
2:	mrs	x1, hcr_el2
	tbnz	x1, #34, 1f			/* HCR_EL2.E2H */
	set_vbar vbar_el2, x0
	mov	x0, #0x33ff
	msr	cptr_el2, x0			/* Enable FP/SIMD */
	b	0f
1:	set_vbar vbar_el1, x0
	mov	x0, #3 << 20
	msr	cpacr_el1, x0			/* Enable FP/SIMD */
0:

#ifdef COUNTER_FREQUENCY
	branch_if_not_highest_el x0, 4f
	ldr	x0, =COUNTER_FREQUENCY
	msr	cntfrq_el0, x0			/* Initialize CNTFRQ */
#endif

/*...省略...*/

#ifdef CONFIG_SYS_RESET_SCTRL
reset_sctrl:
	switch_el x1, 3f, 2f, 1f
3:
	mrs	x0, sctlr_el3
	b	0f
2:
	mrs	x0, sctlr_el2
	b	0f
1:
	mrs	x0, sctlr_el1

0:
	ldr	x1, =0xfdfffffa
	and	x0, x0, x1

	switch_el x1, 6f, 5f, 4f
6:
	msr	sctlr_el3, x0
	b	7f
5:
	msr	sctlr_el2, x0
	b	7f
4:
	msr	sctlr_el1, x0

7:
	dsb	sy
	isb
	b	__asm_invalidate_tlb_all
	ret
#endif
```

上面这段代码的作用是：

1. 如果定义了CONFIG_SYS_RESET_SCTRL，那么就会跳转到reset_sctrl标号，reset_sctrl的作用是将系统相关的寄存器恢复成默认的状态；由于uboot本身也可能是由其他固件引导的（例如BL0），所以为了保证BL0的操作不会对uboot产生意料之外的影响，这里提供了reset_sctrl；特别说明一下，reset_sctrl最后的

   ``` assembly
   7:
   	dsb	sy
   	isb
   	b	__asm_invalidate_tlb_all
   	ret
   ```

   是为了保证所有的操作被成功写入寄存器，这里进行了mmu和cache关闭操作，那么如果有缓存的tlb在这个时候这些缓存的tlb数据就是无效的，这里对可能缓存的tlb进行全部无效化，确保后续任何可能的mmu开启操作不会使用到这些无用的tlb条目而导致系统异常。

2. 随后会判断：如果定义了CONFIG_ARMV8_SPL_EXCEPTION_VECTORS或者没有定义CONFIG_SPL_BUILD，就会进入

   ```assembly
   .macro	set_vbar, regname, reg		## macro是一个伪指令
   	msr	\regname, \reg	
   .endm							  ## macro结束于endm处		
   ## macro定义了一个名称为set_vbar的宏，它拥有参数regname和reg
   ## 这个宏会将 \reg 中的内容写入到 \regname中
   	adr	x0, vectors
   ```

3. 如果没有定义CONFIG_ARMV8_SPL_EXCEPTION_VECTORS并且定义了CONFIG_SPL_BUILD则什么都不会做；程序仅仅会定义一个叫做set_vbar的宏，但是这个宏实际上什么都不会做；
4. 随后，如果确实需要设置异常向量；那么会使用switch_el进行判断，switch_el是一个宏，定义位于\#include <asm/macro.h>中，会判断当前所处的异常等级；当处于el3等级时，会操作scr_el3寄存器（这是一个armv8中新增的寄存器，可以查阅相关的文档），将scr_el3的低四位设置为1；表示设置处理器处于非安全模式，任何级别的物理irq中断，物理fiq，异常abort中断，异常SError中断都将被路由到el3级别； 当处于el2时...（略）；当处于el1时...（略）
5. 如果设置COUNTER_FREQUENCY，则会判断当前的异常等级，如果当前不处于最高，即EL3，那么会将配置的COUNTER_FREQUENCY设置为时钟频率

### 勘误

```assembly
4:	isb

	/*
	 * Enable SMPEN bit for coherency.
	 * This register is not architectural but at the moment
	 * this bit should be set for A53/A57/A72.
	 */
#ifdef CONFIG_ARMV8_SET_SMPEN
	switch_el x1, 3f, 1f, 1f
3:
	mrs     x0, S3_1_c15_c2_1               /* cpuectlr_el1 */
	orr     x0, x0, #0x40
	msr     S3_1_c15_c2_1, x0
	isb
1:
#endif

	/* Apply ARM core specific erratas */
	bl	apply_core_errata

/*...(省略)...*/

WEAK(apply_core_errata)

	mov	x29, lr			/* Save LR */
	/* For now, we support Cortex-A53, Cortex-A57 specific errata */

	/* Check if we are running on a Cortex-A53 core */
	branch_if_a53_core x0, apply_a53_core_errata

	/* Check if we are running on a Cortex-A57 core */
	branch_if_a57_core x0, apply_a57_core_errata
0:
	mov	lr, x29			/* Restore LR */
	ret

apply_a53_core_errata:

#ifdef CONFIG_ARM_ERRATA_855873
	mrs	x0, midr_el1
	tst	x0, #(0xf << 20)
	b.ne	0b

	mrs	x0, midr_el1
	and	x0, x0, #0xf
	cmp	x0, #3
	b.lt	0b

	mrs	x0, S3_1_c15_c2_0	/* cpuactlr_el1 */
	/* Enable data cache clean as data cache clean/invalidate */
	orr	x0, x0, #1 << 44
	msr	S3_1_c15_c2_0, x0	/* cpuactlr_el1 */
	isb
#endif
	b 0b

apply_a57_core_errata:

#ifdef CONFIG_ARM_ERRATA_828024
	mrs	x0, S3_1_c15_c2_0	/* cpuactlr_el1 */
	/* Disable non-allocate hint of w-b-n-a memory type */
	orr	x0, x0, #1 << 49
	/* Disable write streaming no L1-allocate threshold */
	orr	x0, x0, #3 << 25
	/* Disable write streaming no-allocate threshold */
	orr	x0, x0, #3 << 27
	msr	S3_1_c15_c2_0, x0	/* cpuactlr_el1 */
	isb
#endif

#ifdef CONFIG_ARM_ERRATA_826974
	mrs	x0, S3_1_c15_c2_0	/* cpuactlr_el1 */
	/* Disable speculative load execution ahead of a DMB */
	orr	x0, x0, #1 << 59
	msr	S3_1_c15_c2_0, x0	/* cpuactlr_el1 */
	isb
#endif

#ifdef CONFIG_ARM_ERRATA_833471
	mrs	x0, S3_1_c15_c2_0	/* cpuactlr_el1 */
	/* FPSCR write flush.
	 * Note that in some cases where a flush is unnecessary this
	    could impact performance. */
	orr	x0, x0, #1 << 38
	msr	S3_1_c15_c2_0, x0	/* cpuactlr_el1 */
	isb
#endif

#ifdef CONFIG_ARM_ERRATA_829520
	mrs	x0, S3_1_c15_c2_0	/* cpuactlr_el1 */
	/* Disable Indirect Predictor bit will prevent this erratum
	    from occurring
	 * Note that in some cases where a flush is unnecessary this
	    could impact performance. */
	orr	x0, x0, #1 << 4
	msr	S3_1_c15_c2_0, x0	/* cpuactlr_el1 */
	isb
#endif

#ifdef CONFIG_ARM_ERRATA_833069
	mrs	x0, S3_1_c15_c2_0	/* cpuactlr_el1 */
	/* Disable Enable Invalidates of BTB bit */
	and	x0, x0, #0xE
	msr	S3_1_c15_c2_0, x0	/* cpuactlr_el1 */
	isb
#endif
	b 0b
ENDPROC(apply_core_errata)
```

这部分代码是由于arm的设计缺陷，导致有一些东西需要进行手动的设置，从注释也可以看出来，注释指出A53/A57/A72系列的芯片应当进行这样的设置；

### 低平台初始化

````assembly

	/*
	 * Cache/BPB/TLB Invalidate
	 * i-cache is invalidated before enabled in icache_enable()
	 * tlb is invalidated before mmu is enabled in dcache_enable()
	 * d-cache is invalidated before enabled in dcache_enable()
	 */

	/* Processor specific initialization */
	bl	lowlevel_init
	
	/*...（省略）...*/
	/*-----------------------------------------------------------------------*/

WEAK(lowlevel_init)
	mov	x29, lr			/* Save LR */

#if defined(CONFIG_GICV2) || defined(CONFIG_GICV3)
	branch_if_slave x0, 1f
	ldr	x0, =GICD_BASE
	bl	gic_init_secure
1:
#if defined(CONFIG_GICV3)
	ldr	x0, =GICR_BASE
	bl	gic_init_secure_percpu
#elif defined(CONFIG_GICV2)
	ldr	x0, =GICD_BASE
	ldr	x1, =GICC_BASE
	bl	gic_init_secure_percpu
#endif
#endif

#ifdef CONFIG_ARMV8_MULTIENTRY
	branch_if_master x0, x1, 2f

	/*
	 * Slave should wait for master clearing spin table.
	 * This sync prevent salves observing incorrect
	 * value of spin table and jumping to wrong place.
	 */
#if defined(CONFIG_GICV2) || defined(CONFIG_GICV3)
#ifdef CONFIG_GICV2
	ldr	x0, =GICC_BASE
#endif
	bl	gic_wait_for_interrupt
#endif

	/*
	 * All slaves will enter EL2 and optionally EL1.
	 */
	adr	x4, lowlevel_in_el2
	ldr	x5, =ES_TO_AARCH64
	bl	armv8_switch_to_el2

lowlevel_in_el2:
#ifdef CONFIG_ARMV8_SWITCH_TO_EL1
	adr	x4, lowlevel_in_el1
	ldr	x5, =ES_TO_AARCH64
	bl	armv8_switch_to_el1

lowlevel_in_el1:
#endif

#endif /* CONFIG_ARMV8_MULTIENTRY */

2:
	mov	lr, x29			/* Restore LR */
	ret
ENDPROC(lowlevel_init)
````

1. 首先设置GIC（Generic Interrupt Controller）中断控制器，对于arm而言，一共只有两个中断总线，IRQ和FIQ，linux只用到了IRQ；但是实际上中断复杂多样，不可能所有的中断都直接连在IRQ上，因此诞生了中断控制器，中断控制器是一个物理上存在的设备；这里先不展开具体的初始化过程；

### 自旋启动“从核”

```assembly
#if defined(CONFIG_ARMV8_SPIN_TABLE) && !defined(CONFIG_SPL_BUILD)
	branch_if_master x0, x1, master_cpu
	b	spin_table_secondary_jump
	/* never return */
#elif defined(CONFIG_ARMV8_MULTIENTRY)
	branch_if_master x0, x1, master_cpu

	/*
	 * Slave CPUs
	 */
slave_cpu:
	wfe
	ldr	x1, =CPU_RELEASE_ADDR
	ldr	x0, [x1]
	cbz	x0, slave_cpu
	br	x0			/* branch to the given address */
#endif /* CONFIG_ARMV8_MULTIENTRY */
master_cpu:
	bl	_main

```

1. 如果定义了CONFIG_ARMV8_SPIN_TABLE（即自旋启动），并且当前不处于SPL时（换言之，spl时不会启动从核的），会进入自选启动流程；branch_if_master定义于marco.h中；如果定义了CONFIG_ARMV8_MULTIENTRY，那么从核才有可能进入自旋启动流程

   ```assembly
   .macro	branch_if_master, xreg1, xreg2, master_label
   #ifdef CONFIG_ARMV8_MULTIENTRY
   	/* NOTE: MPIDR handling will be erroneous on multi-cluster machines */
   	mrs	\xreg1, mpidr_el1
   	lsr	\xreg2, \xreg1, #32
   	lsl	\xreg2, \xreg2, #32
   	lsl	\xreg1, \xreg1, #40
   	lsr	\xreg1, \xreg1, #40
   	orr	\xreg1, \xreg1, \xreg2
   	cbz	\xreg1, \master_label
   #else
   	b 	\master_label
   #endif
   .endm
   
   ```

2. 此时，如果目前处于主核的状态下，那么会直接跳转到_main；但是如果当前不是主核，而是从核，则会跳转到spin_table_secondary_jump，这个方法定义位于"arch/arm/cpu/armv8/spin_table_v8.5"

   ```assembly
   #include <linux/linkage.h>
   
   ENTRY(spin_table_secondary_jump)
   .globl spin_table_reserve_begin
   spin_table_reserve_begin:
   0:	wfe
   	ldr	x0, spin_table_cpu_release_addr
   	cbz	x0, 0b
   	br	x0
   .globl spin_table_cpu_release_addr
   	.align	3
   spin_table_cpu_release_addr:
   	.quad	0
   .globl spin_table_reserve_end
   spin_table_reserve_end:
   ENDPROC(spin_table_secondary_jump)
   ```

   首先，从核会进入WFE状态（wait for event）；如果有事件发生，则会回到这里执行；一旦被唤醒，程序会读取spin_table_cpu_release_addr的值，如果这个值是0，那么说明还没有进入到linux，那么从核心会继续进入wfe状态等待；如果不是0，那么说明，linux已经被唤醒了，从核心会直接跳转到spin_table_cpu_release_addr指定的位置；如果进入linux，那么在linux进行初始化的时候，spin_table_cpu_release_addr将由linux完成装填；

3. 但是如果没有使用自旋启动，那么则会有一个CPU_RELEASE_ADDR地址，当需要启动从核心的时候给CPU_RELEASE_ADDR这个地址填装需要转跳到的地址，并且手动转跳；

# 实际使用DEMO



## uboot点灯

uboot点灯需要一点点关于arm的汇编的知识；涉及到的东西这里我会进行简单的学习

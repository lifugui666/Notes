## MDK风格伪指令（不用看，粗略了解即可）

伪指令的本质，是多条指令集合而成的一段代码；

写代码的时候难免用会经常用到一些固定的功能，比如if else之类的；如果单纯的使用汇编指令，每次都要先比较然后再根据CPSR的内容进行BL；这样就很繁复；

所以伪指令应运而生，它从形式上来看像是宏定义；从功能上而言，是帮助我们简化某些固定操作的指令；

**GNU有一套伪指令，MDK也有一套伪指令；这两台套伪指令相似，这里我还是学习MDK伪指令**

**注意：伪指令要遵循所谓的ADS Style；**

**ADS风格：顶行写 或者使用tab缩进**

**什么时候顶行？诸如EQU，SET这类 使用时第一个字段不是伪指令，一定要顶行写**



### AREA

````assembly
AREA 段名称 数据/代码段 读写模式

/*例如*/
AREA test CODE READONLY@表示定义了一块叫做test的 代码段 ，这个段是只读的

AREA test2 DATA READWRITE@表示定义了一块叫test2的 数据段 ， 这个数据段允许读写
````


### CODE32/CODE16

````assembly
CODE32 @表示后续的代码要被翻译成ARM指令

CODE16 @表示后表面的代码要被翻译成Thumb指令
/*但是这里要注意一下，CODE16仅仅是告诉汇编器，后面的指令要被翻译成Thumb指令，而不会让处理器在运行的时候进入Thumb指令模式；处理器想要进入Thumb指令模式，需要设置CPSR的T标志*/
````

### ENTRY

表示程序的入口点；就好像C语言中的main函数

### END

表示结尾

### EQU

````assembly
/*用于定义变量*/
LIFUGUI EQU 0x00000001@定义了一个叫做 LIFUGUI 的变量，这个变量的值被赋成了 0x00000001
/*注意，这个指令必须顶头写；否则有可能会导致编译器将LIFUGUI这个变量视作指令，而触发非法指令的错误*/
````



### EXPORT与IMPORT与EXTERN

EXPORT：将标号声明为全局标号，本质上和.global功能一样

IMPORT：是静态引用，告知编译器，会用到其他源文件中的定义；通过这个指令可以实现混合编程（例如可以引入C语言的函数）；同时**静态引用**代表着只要使用IMPORT声明引入，无论后续是否调用，被引入的定义均会被加入符号表中；

EXTERN：是动态引用，如果声名了EXTERN但是后续没有引用，那么编译器就不会把引入的标签加入符号表；

### GET

相当于include

```assembly
/*例如*/
GET "a.S" @就可将文件 a.S 引入进来
```



### RN

为寄存器定义别名

````assembly
name RN Rn@ 将寄存器Rn取名为name
/*同时要注意，类似于EQU，这个命令也应当顶头写*/
````



### -------分割线-------

为了让汇编用起来更加方便，汇编也提供了类似于高级语言的定义，条件分支等伪指令

### 定义变量，赋值

汇编中使用伪指令可以定义：数字变量，逻辑变量，字符串变量；

也可以使用伪指令对变量进行赋值

````assembly
/*全局变量声明,GBL是global的缩写*/
GBLA test1@ 设置全局数字变量test1
GBLL test2@ 设置全局逻辑变量
GBLS test3@ 设置全局字符串变量

/*局部变量声明，LCL是local的缩写*/
LCLA test1@ 局部
LCLL test2@ 同上
LCLS test3@ 同上

/*变量的赋值*/
test1 SETA 0xaa@ 对数字变量test1赋值0xaa，这里着重强调，是 0xaa 而不是 #0xaa，后者是立即数寻址！
test2 SETL 0x01@ 类似
test3 SETS 0xaa@ 类似

/**使用实例**/
	GBLA test1
test1 SETA 0x01

	GBLL test2
test2 SETL {TRUE}

	GBLS test3
test3 SETS "hello"
````

那么，局部和全局，他们的生效范围具体是什么？这两类变量存在哪里？

全局：全局变量的默认范围是整个.S文件，不过可以用EXPORT（或者.global）将其扩展到整个项目

局部：局部变量的生效范围是在一个宏定义内；

无论是局部变量还是全局变量，他们都是存在内存中的，并不是存在寄存器里；

全局变量存在数据段中；局部变量存在代码段中；（这一点和C语言是一样的）

### 为寄存器列表定义别名RLIST

````assembly
LIFUGUI RLIST {R0, R1, R2}@ 这条指令代表后续只要提到LIFUGUI，指的就是R0， R1，R2这三个寄存器
/*只要定义了寄存器列表别名，就可以利用LDM或者STM进行大规模操作*/
````

### $符号

$符号 的用法类似于 SHELL中的$符号 用法

````assembly
LCLS str1
str1 SETS "world"
LCLS str2
str2 SETS "hello $str1"
/*str2的值是 hello world*/
````

### 运算符伪指令

````assembly
+	@加法
- 	@减法
* 	@乘法
/ 	@触发
= 	@等于
> 	@大于
< 	@小于
>= 	@大于等于
<= 	@小于等于
/= 	@不等于
<>	@不等于

ROL	@循环左移
ROR	@循环右移
SHL	@左移
SHR	@右移

AND	@按位与
OR	@按位或
NOT	@按位非
EOR	@按位异或

LAND	@逻辑与
LOR		@逻辑或
LNOT	@逻辑非
LEOR	@逻辑异或
````



### 寄存器伪指令

#### LDR：load date to register

````assembly
LDR R0, =0x12	@大范围寻址到寄存器；但注意，有一条同名的标准指令；
/*上述LDR的操作是：将0x12写入R0中；所以LDR伪指令可以取代MOV或者MNV*/

/*LDR使用举例*/
	LCLA num
num SETA 0x12
	LDR R0, =num	@执行后R0中的值是0x12

````

#### ADR：

````assembly
ADR	R0， =test1	@小范围寻址到寄存器（+-255）
/*如果test1是一个变量，那么ADR将会把 变量 所在的 地址的值存入 R0；因此ADR常用于我们想要知道一个变量的地址时使用*/

/*ADR使用举例*/
_start:
	ADR R0, =_start	@执行后就可以知道_start的地址了
````

#### ADRL：

```assembly
ADRL	@中范围寻址到寄存器
```

#### DCB：data control bytes

DCB可以用"="替代

```assembly
/*DCB会分配一块连续的内存地址，并且按照Byte为单位进行初始化*/
name DCB number, number, number, ...... 

/*使用实例*/
led_control_byte DCB 0x01, 0x02, 0x03 @同样，这个指令必须顶头 
	ADR R0, =led_control_byte		@取到分配的连续内存的地址

/**注：DCB有一个很重要的用法，它可以用来分配字符串**/
str1 DCB "hello"
/*要注意的是上述的str1的长度是6个byte，除了hello之外还有一个 '\0' */

/*DCB可以用=替代*/
str1 = "hello" @ 这样也是可以的

```

#### DCW：data control **half word**（**注意：以半字为单位**）

```assembly
/*DCW会分配一块连续的内存地址，并且按照半字为单位进行初始化*/
name DCW number, number, number, ...... 

/*使用实例*/
led_control_hword DCB 0x0001, 0x0002, 0x0003 @同样，这个指令必须顶头 
	ADR R0, =led_control_hword		@取到分配的连续内存的地址
```

#### DCD：**以字为单位**

````assembly
/*DCD会分配一块连续的内存地址，并且按照字为单位进行初始化*/
name DCD number, number, number, ...... 

/*使用实例*/
led_control_word DCB 0x00000001, 0x00000002, 0x00000003 @同样，这个指令必须顶头 
	ADR R0, =led_control_word		@取到分配的连续内存的地址
````

#### SPACE

````assembly
/*以Byte为单位，分配连续的内存空间，且用0填充*/
test1 SPACE 100	@ 分配100个byte的连续内存空间，用0初始化
````



#### MAP与FIELD

这两个指令可以用于定义结构体

MAP用于定义一张结构化内存表的首地址（MAP可以用 "^" 替代）

FIELD用于定义结构化的内存表的数据域（FIELD可以用 "#" 替代)

````assembly
MAP Addr @ MAP可以用于定义一个结构化的内存表的首地址
name FILED length @用于定义一个范围

/*例如*/
MAP 0x100 @ 表示0x100是一张 结构化内存表的首地址
A FIELD 16@ 定义16个byte，从0x100到0x110是名字为A的一片区域
B FIELD 32@	继续定义32个byte，从0x110到0x130是名字weiB的一篇区域
````



### 控制语句IF ELSE

```assembly
/*举例*/
	GBLA age
age SETA 0x20
	IF age > 0x18
		/*进行某些操作*/
	ELSE
		/*进行某些操作*/
```



### 循环语句WHILE WEND

````assembly
	WHILE 条件
    /*代码块*/
    WEND
````




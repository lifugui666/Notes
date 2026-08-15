# Python的包引用机制



## 前言

在C语言中，我们经常写这样一句：

```c
#include <stdio.h>
//....
```

这句代码引入了一个名为"stdio.h"的头函数，引入这个函数之后，我们就可以使用一些标准输入输出函数，例如printf()；可以认为在C语言中，printf()这个函数，是stdio.h这个头文件提供的功能；

python中同样有类似于“头函数”的东西，我们称之为“模块”，模块也可以被组织成更复杂结构，我们称之为包；



## 模块

在介绍包之前，先介绍一下模块，模块就是一个python文件，例如：

```python
# 这个文件叫做 my_module.py

variable_in_my_module = 1

def my_func_in_my_module():
    print("调用了my_module中的方法")
```

```python
# 这个文件叫做 main.py

import my_module

print("当前正在执行main.py")
my_module.my_func_in_my_module()
print(my_module.variable_in_my_module)
```

```shell
#执行结果如下
lifugui@LAPTOP-55A4PF8J:/tmp$ python3 ./main.py
当前正在执行main.py
调用了my_module中的方法
1
```

在上面这个例子中，我们在一个叫做main.py的文件中，调用了另一个叫做my_module.py的文件中的函数和变量；

如果不想引入整个模块，也可以仅引入模块中的一部分： 	

```python
# 对main.py文件进行一些修改
from my_module import my_func_in_my_module
# from my_module import *就可以把my_module中全部的内容引用过来

print("当前正在执行main.py")
my_func_in_my_module() # 此时无需再使用 模块.方法 这种模式去引用方法，直接用方法名调用即可
print(variable_in_my_module)
```

```shell
# 执行结果如下
lifugui@LAPTOP-55A4PF8J:/tmp$ python3 ./main.py
当前正在执行main.py
调用了my_module中的方法 # 可见my_func_in_my_module确实被引入了main，在main中可以调用
Traceback (most recent call last): # 但是variable_in_my_module没有被引入main中
  File "./main.py", line 6, in <module>
    print(variable_in_my_module)
NameError: name 'variable_in_my_module' is not defined
```

利用form xxx import xxx的语法，我们可以仅引入模块中的一部分；



除此之外还可以对引入的模块进行重命名，例如：

```python
# 对main.py文件再进行一些修改
import my_module as mm

print("当前正在执行main.py")
mm.my_func_in_my_module()
print(mm.variable_in_my_module)
```



利用上述的这些机制，我们可以将一个项目分成好几个文件写，就像C语言中所谓的模块化编程一样；这样对代码的易读性和对编码人员的分工都有很多的好处；



## 包

包是一种模块的组织方式，接下来我会构建一个简单的包，命名为my_pack：

这个包的结构如下：

```shell
lifugui@LAPTOP-55A4PF8J:/tmp/my_pack$ tree
.
├── __init__.py # __init__.py是一个文件
├── a # a是一个文件夹
│   └── a.py # a.py是一个文件（模块）
└── b # b是一个文件夹
    └── b.py # b.py是一个文件（模块）
```

根据我对包的理解，一个包可以被分成两个部分，一个部分是各种模块，另一个部分是\_\_init\_\_.py文件

### 第一部分：包中的模块

其中文件a.py的内容如下

```python
# a.py
def fun_in_a():
    print("调用了a.py中的函数")
```

文件b.py的内容如下

```python
# b.py
def fun_in_b():
    print("调用了b.py中的函数")
```



很明显，包里的模块是提供具体功能的，并且你可以根据自己的想法自由的组织模块的结构：可以放在根目录下面，也可以创建一个文件夹把模块放在文件夹里，这些操作都是被允许的；

在构筑包的时候应当尽量的把模块按照规则组织，这样之后在调用包的时候会减少很多痛苦....

### 第二部分：\_\_init\_\_.py文件

如果一个文件夹下存在\_\_init\_\_.py，那么python解释器会把这个文件夹当作包处理；

\_\_init\_\_.py中描述了模块的组织模式，没有这个文件的话引用包是一个很痛苦的事情，举一个例子：

例：如果my_pack的\_\_init\_\_.py中是空的，那么我将无法通过如下的代码调用my_pack中的函数:

```python
# test.py
import my_pack

my_pack.a.fun_in_a()
```

执行结果如下：

```shell
lifugui@LAPTOP-55A4PF8J:/tmp/my_pack$ python3 ../test.py
Traceback (most recent call last):
  File "../test.py", line 3, in <module>
    my_pack.a.fun_in_a()
AttributeError: module 'my_pack' has no attribute 'a'
```

我们明明在my_pack下面创建了文件夹a，但解释器认为my_pack下面没有一个叫做a的东西；

也许你会好奇，如果我直接手动从my_pack中引入a，是不是就能调用a中的内容了？对不起，还是不行..

```python
# test.py
from my_pack import a

a.fun_in_a()
```

```shell
lifugui@LAPTOP-55A4PF8J:/tmp$ python3 test.py
Traceback (most recent call last):
  File "test.py", line 4, in <module>
    a.fun_in_a()
AttributeError: module 'my_pack.a' has no attribute 'fun_in_a'
```

from my_pack import a只是从my_pack文件夹中引入了文件夹a，而解释器**还是不知道**文件夹a下面还有一个叫做a.py的模块...

在没有\_\_init\_\_.py正确定义的情况下，想要从my_pack中引用到a.py，正确的写法如下：

```python
# test.py
from my_pack.a import a

a.fun_in_a()
```



如果包中的内容需要这样去引用的话那就太弱智了，包根本都没有存在的价值了，引用一个包里的内容比直接引用模块还繁琐，我还要包做什么？

不过幸运的是python提供了\_\_init\_\_.py；我们可以在这个文件中告诉解释器，这个包下面到底都有哪些资源，是以什么方式组织起来的:

```python
# __init__.py
from .a import a
from .b import b
```

这两行代码实际上是在描述my_pack中的模块的路径，之后，我们只需要引用my_pack就可以按照my_pack中的路径去引用方法了

```python
# test.py
import my_pack

my_pack.a.fun_in_a()
# 现在这个文件变回了我们最初没有写__init__.py时举的那个例子
```

执行结果：

```shell
lifugui@LAPTOP-55A4PF8J:/tmp$ python3 test.py
调用了a.py中的函数
```

这次是可以调用到的



## import xxx 和 from xxx import xxx的区别

1. 如果使用`import module`，这是引入了一个模块，要调用模块中的内容，需要通过模块名去调用`module_name.func()`
2. 如果使用`from module_name import func`，这是引入了module_name中的一部分，使用的时候直接调用`func()`即可	

这里还是要以“一切都是对象”的理念理解，`import module`之后，我们引入了一个`module`对象，要引用`module`对象中包含的成员，自然要以`module.func`这种方式引用；

而`from module import func`则是直接从`module`对象中引入了一个`func`对象，所以使用这种引用方法，在后续的代码中直接调用`func`即可；



## python导入包的方式

内容来源https://zhuanlan.zhihu.com/p/432503792

### 1.  关于路径问题

python会在三个地方搜索你想要引入的包：

1. 当前执行的.py脚本所在的目录
2. 环境变量PYTHONPATH所指出的目录
3. 使用sys.path.append所添加的路径



### 2. 相对导入 和 绝对导入

相对导入和绝对导入**都有路径参照物**

#### 2.1 绝对导入：

**绝对导入的路径参照物是脚本**，所谓绝对导入其实就是从最顶层开始写

例如：

```python3
└── D:\workplace\python\import_test
    ├──main.py
    ├── pack1
    │   ├── module1.py

# main.py
from pack1 import module1
```

此时是可以正常运行的

如果将main移动到pack1下面：

```python3
└── D:\workplace\python\import_test
    ├── pack1
    │   ├── module1.py
    │   ├── main.py

# main.py
from pack1 import module1
```

 此时不能执行，因为站在main.py的角度上，当前路径下没有一个叫做`pack1`的包



#### 2.2 相对引入

相对导入的参照物是当前的模块所在的位置

例如：

```python3
# 文件结构
└── D:\workplace\python\import_test
    ├──main.py
    ├── pack1
    │   ├── module1.py
    │   ├── module2.py

# module1.py
import pack1.module2 # 绝对导入
import  module2 # 隐式相对导入 #!!! 由于隐式相对导入容易和显示绝对导入混淆，因此在PEP328之后取消了隐式相对导入，自此之后import只能用于绝对导入	
from . import module2 # 显式相对导入 #从本文件所在的路径下引入模块module2

# main.py
from pack1 import module1 # 绝对导入
```



## 当存在复杂的相互引用时，应如何组织包的结构？



问题：

```shell
PS D:\Thz related\THZ试验台代码\continue_scan\just_cnc> tree /f
│  client_main.py
│  readme.md
│  server_main.py
│  test_speed.py
│  __init__.py
│
├─client
│  │  client.py
│  │  __init__.py
│
├─command
│      command_check.py
│      __init__.py
│
├─config
│  │  my_config.py
│  │  __init__.py
│
├─server
│      ctrl_CNC.py
│      server.py
│      __init__.py
```

`client文件夹`中的`client.py`引用了`config文件夹`中的`my_config.py`,代码如下

```python
from socket import *
from config.my_config import cnc_config
import json
import logging

#...
```

这样写，在使用client_main.py调用的时候是没有问题的，因为在client_main.py的视角下，确实有一个叫做config的包，这个包里确实有my_config模块，而my_config模块里确实有cnc_config对象；

但如果将just_cnc作为一个包调用，就会出现问题，因为此时，文件的层级结构如下:

```shell
PS D:\Thz related\THZ试验台代码\continue_scan> tree
├─.vscode
├─main.py # 这是程序的入口
├─continue_scan
│  ├─command
│  ├─config
│  │  └─__pycache__
│  ├─datas
│  ├─interactive
│  └─test
├─just_cnc
│  ├─client
│  │  └─__pycache__
│  ├─command
│  ├─config
│  │  └─__pycache__
│  ├─server
│  └─__pycache__
└─just_radar
    ├─config
    │  └─__pycache__
    ├─datas
    ├─Exceptions
    │  └─__pycache__
    ├─logs
    ├─test
    │  └─dll_demo
    └─__pycache__
```

站在程序的入口再看，我们已经无法找到config这个包了...


























# Python的包引用机制



## 前言

在C语言中，我们经常写这样一句：

```c
#include <stdio.h>
//....
```

这句代码引入了一个名为"stdio.h"的头函数，引入这个函数之后，我们就可以使用一些标准输入输出函数，例如printf()；可以认为在C语言中，printf()这个函数，是stdio.h这个头文件提供的功能；

python中同样有类似于“头函数”的东西，我们称之为“包和模块”

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

在上面这个例子中，我们在一个叫做main.py的文件中，调用了另一个叫做my_module.py的文件中的函数和变量；

通过“模块”，我们可以将一个程序分成若干个模块去编写，实现所谓的“模块化”编程



## 包




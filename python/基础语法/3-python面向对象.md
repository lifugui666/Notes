# Python的面向对象



## 面向对象简述

我不想讨论面向对象和面向过程到底有什么区别，也不想讨论python到底是不是一门面向对象语言...这些讨论没什么意义；python提供了类，继承，重写...等一系列功能，让我们能够抽象出类，实例化对象，这就够了；



## 类和对象

### 如何创建一个类

```python
class staff_class:
    '这是一个员工类'
	num_of_staff = 0
    
    def __init__(self,name,salary):
        self.name = name
        self.salary = salary
        staff_class.num_of_staff += 1
        
    
    
    
```


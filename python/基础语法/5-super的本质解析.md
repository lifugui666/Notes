# Python中的super



## 函数bound和描述器

首先解释一下什么是描述器，描述器和函数有什么关系？

```python
# 函数本身是一个对象，函数就是一个实现了__call__的对象

# 函数同时还是一个描述器
# 在python中，如果实现了__get__ __set__ __delete__ 中的一个或多个，那么就是一个描述器
# 很明显，python中的函数是一个描述器

# 这里要强调一下，使用 类 调用描述器和使用 对象 调用 描述器，同一个描述器是会做出不同的反应的；
```



观察如下代码

```python
class A:
    def my_func(self):
        pass
   

a = A()
A.my_func() # 1
a.my_func() # 2

#请问1和2有啥子不同？
# 实际上，1和2都可以视作是在调用描述器的__get__方法；
# 但是1返回的是描述器本身（也就是函数本身）;
# 但是2返回的是一个bound method
# 二者的区别在于
# A.my_func(a)等价于a.my_func()
# 可以理解为 a.my_func()返回的是一个与对象a绑定在一起的函数对象
# 而A.my_func()是一个没有与任何对象绑定的函数对象
```



## super的本质

ok，在很多人的眼中，super是一个用来调用父类方法的关键字；

这个理解不到位：

1. super本身不是一个关键字，他是一个类，当你使用super的时候，实际上会创建一个super的对象
2. super本质上也并不是用来调用父类的

```python
class A:
    def test(self):
        print("A")
class B:
    def test(self):
        print("B")
        super().test()
        # 在python2.x版本中，这里的super必须写成下面的形式
        # super(B,self).test()
class C(B,A):
    def test(self):
        print("C");
        super().test()
        
c = C()
c.test()

# result
# C
# B
# A
```

上述代码中，首先输出C可以理解，随后输出B也可理解，但是为什么最后会输出一个A？A并不是B的父类，为什么会被调用到？

实际上这涉及到super的本质，super并不是给你用来调父类用的；

在上面这个例子中，class C实际上是由多个类组成的有序集合（mro），可以使用\_\_mro\_\_查看这个类的mro

```python
print(C.__mro__)
# (<class '__main__.C'>, <class '__main__.B'>, <class '__main__.A'>, <class 'object'>)
# 可见，C的mro是C B A object
# mro才是super调用的根据
# 每一次调用super，会在mro中向前一步进行调用
```

为了清楚的说明白super的工作原理，我们使用`super(B,self).test()`这个版本说明：

1. 第一个参数 B ，明确了当前正在调用super的类是B
2. 第二个参数self，表明，mro要从self上获取，同时函数也要bound到self上

这里着重解释self，实际上在c.test()回溯的时候，调用到B中的super时，self是c；因此这个参数表明，mro是C的mro，同时第一个参数是B，那么就表示在(C B A object)中要从B向前一个类，也就是A；因此会调用到A中的test；

那么，在我们写class B的时候，super还不知道B后面是A，更不晓得A里有没有一个test()，这个代码是怎么通过解释器检查的？

实际上调用到B的时候会向后查找，查找A中有没有test()，如果没有就继续向后查找；

如果A中有test()，那么就调用\_\_get\_\_获取这个描述器，此时还不能直接调用这个test()，因为此描述器还未和对象bound；

随后，这个test()会和self（注：self在这个例子中始终是c）绑定，生成一个bound method，最后调用的实际上是这个bound method






























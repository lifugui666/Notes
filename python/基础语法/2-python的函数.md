# python的函数



## 基本定义

```python
def fun_name():
    # 函数体
```

对于python的函数，最基础的就是要注意**缩进格式**；缩进格式真的很重要，**要么用四个空格，要么用tab，千万不要混用！！！**

除此之外python的函数定义和其他的编程语言十分相似，不过python的函数仍有一些特殊的特性



## 注意事项

### 1. 先定义再使用

在调用一个函数之前，我们必须保证这个函数在上文中被定义过；如果调用一个没有被定义过的函数，解释器会因为找不到这个函数而报错；

```python
def my_func():
    print("this is a function")
    
my_func() # 合法调用
```

```python
my_func() # 非法调用，my_func()尚未定义

def my_func():
    print("this is a function")
```



### 2.避免空定义

不同于C语言，python不允许空定义，例如：

```python
def my_func():	# 这样是非法的
```

如果处于某些原因，真的需要写一个函数又不实现，可以用pass：

```python
def my_func():
    pass	# 这样是合法的
```

### 3.python的函数可以返回多个返回值

不同于c语言一个函数最多只能返回一个值，python可以返回多个不同的返回值：

```python
def my_func():
	return 1,2,3

x,y,z = my_func()
# x=1，y=2，z=3
```

### 4. 使用kwargs传递参数

```python
# python支持使用键值对传递参数，python文档将这种方式称为kwargs（即key word args）
def my_function(name, age):
    print("my name is %s",name) # 这里用了格式控制 
	print("i am %d years old",age) # 同上

my_function(name = "lifugui", age = 26)
```

### 5.传递任意参数

python允许我们在定义函数的时候
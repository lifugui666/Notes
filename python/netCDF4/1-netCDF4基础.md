# 1 netCDF4基础

author ：lifugui



## 详细文档

https://unidata.github.io/netcdf4-python/



## 介绍

首先python使用的netCDF4库是一个基于C语言的库

### 使用向导

#### 创建/打开/关闭一个netCDF4文件

只需调用Dataset构造器，就可以创建一个netCDF4文件；这个方法也被用于打开一个已经存在的netCDF文件；如果这个文件以可写模式打开('w','r+','a')，那么你就可以向文件中添加新的 dimensions group variables attributes；（后面的意思是netCDF有好几个版本，你可以在创建文件的时候指定特定的文件格式版本，默认是NETCDF4格式）；使用Dataset.close()就可以关闭文件；

```python
>>> from netCDF4 import Dataset
>>> rootgrp = Dataset("test.nc", "w", format="NETCDF4")
>>> print(rootgrp.data_model)
NETCDF4
>>> rootgrp.close()
```



#### netCDF文件中的group

netCDF的第4个version提供了以层级组 组织数据的支持；这种方式就像文件系统中的目录；groups可以包含 variables, dimensions 和 attributes，也可以包含其他的groups；netcdf4会创建一个特殊的group被称为root group，就像文件系统的根目录那样；

你可以使用`Dataset.createGroup()`创建group实例；也可以使用一个group实例调用`createGroup()`函数以创建一个groups;

不过要注意的是group仅仅在netCDF4中可以使用

```python
>>> rootgrp = Dataset("test.nc", "a")
>>> fcstgrp = rootgrp.createGroup("forecasts")
>>> analgrp = rootgrp.createGroup("analyses")
```

你甚至可以使用路径的方式去创建goups

```python
>>> fcstgrp1 = rootgrp.createGroup("/forecasts/model1")
>>> fcstgrp2 = rootgrp.createGroup("/forecasts/model2")
```

如果路径描述的group不存在，那么这个group将被自动创建



#### netCDF中的Dimensions

netCDF从dimensions定义variables的尺寸，因此在创建任何variables之前，必须要创建被用到的dimensions；

可以使用Dataset或者group的实例以`createDimension()`创建，这个函数有两个参数：

1. 一个字符串，用于给该Dimension命名
2. 一个int，用于指定该Dimension的size

第二个参数可以为None，以此来创建一个size为无限的Dimension；

```python
>>> level = rootgrp.createDimension("level", None)
>>> time = rootgrp.createDimension("time", None)
>>> lat = rootgrp.createDimension("lat", 73)
>>> lon = rootgrp.createDimension("lon", 144)
```

使用python的len函数就可以获取Dimension的size；



#### netCDF中的variables

netCDF中的variable很像是numpy中的多维数组对象，但是不同于多维数组的是在netCDF中variables可以沿着一个或者多个无限长度的维度进行append操作；

对一个Dataset或者Groups的实例使用createVariable()就可以创建数组；这个方法需要两个不可或缺的参数

1. 需要一个string，以命名该variables
2. 需要一个variable的数据类型

variable的dimension由一个包含了dimension名称的元组给出；

variable的基础数据类型，和numpy数组的attribute的dtype是对应的；你可以直接使用numpy的dtype对象来指定datatype，或者任何可以转换为dtype对象的对象；有效的datatype指定符包括:

1. 'f4':32-bit 浮点型
2. 'f8':64-bit 浮点型
3. 'i1':8-bit 整型
4. 'i2':16-bit 整型
5. 'i4':32-bit 整型
6. 'i8':64-bit 整型
7. 'u1':8-bit 无符号整型
8. 'u2':16-bit无符号整型
9. 'u4':32-bit无符号整型
10. 'u8':64-bit无符号整型
11. 'S1':string

有一套旧的指定符与上述的11个描述符一一对应，目前旧版的指定符仍旧可以使用，但是我在这里不介绍他们了；

很多dimensions自身也会被定义为variables，这些家伙被称为coordinate variables；`Dataset.createVariable()`方法会返回一个`Variable`类的实例，这个类的方法可以被用于设置和访问variable data和attributes

```python
>>> times = rootgrp.createVariable("time","f8",("time",))
>>> levels = rootgrp.createVariable("level","i4",("level",))
>>> latitudes = rootgrp.createVariable("lat","f4",("lat",))
>>> longitudes = rootgrp.createVariable("lon","f4",("lon",))
>>> # two dimensions unlimited
>>> temp = rootgrp.createVariable("temp","f4",("time","level","lat","lon",))
>>> temp.units = "K"
```



#### netCDF的Attributes

在netCDF中，有两类attributes，全局和可变；

全局attribute提供关于group或者整个dataset的信息；

可变attribute提供关于一个group中的一个variables的信息；

全局attribute通过Dataset或者Group的实例设置

可变attribute通过variable实例设置；

attribute可以是字符串，数字，或者序列

```python
>>> import time
>>> rootgrp.description = "bogus example script"
>>> rootgrp.history = "Created " + time.ctime(time.time())
>>> rootgrp.source = "netCDF4 python module tutorial"
>>> latitudes.units = "degrees north"
>>> longitudes.units = "degrees east"
>>> levels.units = "hPa"
>>> temp.units = "K"
>>> times.units = "hours since 0001-01-01 00:00:00.0"
>>> times.calendar = "gregorian"
```





#### 实际使用&个人理解

##### 个人理解

从个人的理解上来看，netCDF的结构像是

$f(dimension1,dimension2,...) = variable$

variable是实际的物理数据

dimension对应着自变量

attribute起着一些注释的作用，比如变量的单位，当然对于netCDF来说attribute的重要性比variable和dimension要低很多就是了



##### 实际使用

这是摘自xyz轴数据采集设备的代码

```python
def configure_file(self):
    try:
        ### Initialize netCDF file
        self.ds = nc.Dataset(self.full_path, 'w', format='NETCDF4')
        # ds.setncattr('description','')
        self.ds.history = 'Created: ' + tm.ctime(tm.time())
        self.ds.sample = self.file_name
        self.ds.dt = self.Sensor.dt
        Qframe = self.Sensor.get_Raw_Data()
        tsweep = len(Qframe)
        # create dimensions
        sweepTime = self.ds.createDimension('sweepTime', tsweep)#创建了一个叫做sweepTime的维度，长度是一次扫频采样次数
        xx = self.ds.createDimension('xx', None)# 创建一个叫做xx的维度，长度无限
        yy = self.ds.createDimension('yy', None)# 创建一个叫做yy的维度，长度无限
        Start_freq = self.ds.createDimension('Start_freq', self.Sensor.Start_Freq )# 维度 Start_freq,长度为起始频率
        End_freq = self.ds.createDimension('End_freq', self.Sensor.End_Freq)# 同上
        # create variables
        sweepTimes = self.ds.createVariable('sweepTime', 'f4', ('sweepTime'))
        sweepTimes.units = 'us' # 这是一个attribute，是sweepTimes的单位，us
        sweepTimes[:] = np.linspace(0,tsweep-1,num=tsweep)
        #print(np.linspace(0,tsweep-1,num=tsweep))
        self.x_axis = self.ds.createVariable('xx', 'f4', ('xx'))
        self.x_axis.units = 'mm'

        self.y_axis = self.ds.createVariable('yy', 'f4', ('yy'))
        self.y_axis.units = 'mm'

        self.data = self.ds.createVariable('data', 'f4', ('sweepTime', 'xx', 'yy'))
        self.data.units = 'V'

        Start_freq = self.ds.createVariable('Start_freq', 'int', ('Start_freq'))
        Start_freq.units = 'GHz'
        End_freq = self.ds.createVariable('End_freq', 'int', ('End_freq'))
        End_freq.units = 'GHz'
    except Exception as e:
        print(e)
        # return False
        
        
  ### 在另一个函数中
    Qframe = self.Sensor.get_Raw_Data()                                                   
    self.x_axis[x_Counter] = x
    self.y_axis[Y_Counter] = y
    self.data[:,x_Counter,Y_Counter] = Qframe
    ## 这是数据的来源，在config_file()中，我们声明了self.data是一个netCDF的variable对象
    ## 这个函数中，我们只需要针对这个self.data赋值，就可以将数据存在文件中
```

netCDF有一个省心的地方在于，作为用户，我们并不需要控制数据向文件中的写入；我们只需要控制好variable变量中的内容就可以了；


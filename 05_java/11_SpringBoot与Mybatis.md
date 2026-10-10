# MVC架构

MVC架构，从逻辑上把整个程序分成：**视图--分派请求--处理请求** 3个部分，分别对应View--Controller--Model

1. Model层
    DAO/Mapper层（持久化层）：操作数据库
    Service：业务逻辑/事务控制
2. Controller层
    数据流转/界面切换
3. View层
    前端技术（Vue、React）--> HTML + CSS

Java的SSM（或者说SpringBoot + Mybatis）就是一个实现MVC架构的框架，这套框架减少了程序员所需手动编写的代码量；

## View层

用户看到的网页

view层负责收集、展示数据；不负责处理业务逻辑



## Controller层

控制层负责拦截URL，把不同的URL请求分配给对应的函数；

当这些函数处理完请求后，再把数据或者结果反馈给View层；

Controller层不会直接操作数据库，也不负责处理复杂的业务逻辑



## Model层

Model层负责具体的业务处理，一般还可以再细分为Service层和DAO层(持久化层)

DAO层（持久化）的函数负责操作数据库，在SpringBoot + Mybatis框架中，Mybatis框架替代了手写的DAO层，其提供了一种代码量更少的数据库操作方法；

Service层中的函数则会组合多个DAO层的函数构成“事务”

```shell
# 举个例子
# Service层里，有一个“转账”事务，在代码中就表现为，Service层里有一个转账函数
# 转账事务需要进行两个SQL操作：A给B转，涉及到A账号扣钱，B账号加钱
# 	扣钱的SQL操作在DAO中对应一个函数
# 	加钱的SQL操作在DAO中也对应一个函数
# 则转账这个Service层函数，要调用两个DAO层的SQL操作函数，并且保证这两个SQL要么都执行成功，如果有一个
# 执行失败，成功的那个也要回滚
```



# 注解是怎么工作的？

注解是Java的语法，并不是SpringBoot或Mybatis带来的新功能；

原生的Java本身就支持诸如@Override、@Deprecated等注解

注解本身有三种保留级别：

1. SOURCE级别，只在源码中保留，编译后就会被抛弃，@Override就属于这一级别
2. CLASS级别，编译后保留在clss文件中，但是运行时不可见（默认的级别）
3. RUNTIME级别，运行时仍旧保留，可以通过 反射机制 读取注解（框架的注解大多属于这一类）

注解是可以自定义的

```java
/*************************************************
* 如何自定义一个注解，并通过反射获取注解
*************************************************/

// 定义注解
import java.lang.annotation.*;

@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.METHOD)
public @interface MyAnnotation {
    String value() default "default";
}

// 使用注解
public class Demo {
    @MyAnnotation("hello")
    public void test() {}
}

// 读取注解
Method method = Demo.class.getMethod("test");
MyAnnotation anno = method.getAnnotation(MyAnnotation.class);
System.out.println(anno.value()); // hello

```

不难想到，框架也是通过这种方法，读取了类和方法上写的注解，并且根据不同的注解进行了不同的操作，以实现功能；

# SpringBoot 与 Mybatis

SpringBoot脱胎于Spring框架与SpringMVC
原始的Spring框架有大量的配置文件需要人工写，SpringBoot进一步精简了配置文件

Mybatis则主要用于简化DAO层，不用再手写那么多代码；

## SpringBoot

SpringBoot有两个核心概念，IOC和AOP

IOC解决Controller和Service耦合  以及  Service和DAO耦合 的问题；

AOP解决Service层中的函数大多流程一致，不同的只是一两行关键代码 造成的重复；



### IOC 控制反转

在没有IOC之前，代码的结构是正向依赖的

**正向依赖：**

Service中使用了DAO，那么Service中需要有一个DAO的对象，此时Service就和DAO产生了耦合：

```java
public class Service
{
    public DAO dao = new DAO();
    // 此时Service？高度依赖DAO
    // 如果没有DAO，那么代码中会报两个错误
    // 1. DAO dao
    // 2. new DAO()
}
```
每次在使用Service之前，要先声明并new一个DAO对象，两者存在耦合关系

同样的问题在Controller和Service之间也存在；

在正向依赖模式中，Controller-->Service-->DAO构成了一个依赖链条；

为了把他们之间的关系剥离开（解耦合），提出控制反转

**控制反转：**

控制反转，最重要的作用是：解耦，让Controller-->Service-->DAO这个依赖链条中的三者，不再依赖；

控制反转的实现：

1. **使用接口**
2. **依赖注入**

例：以Controller-->SerVice-->持久层 为例，学习SpringBoot + Mybatis的控制反转写法；

```java
/***************************************************
* 持久层
***************************************************/
// 这个例子里使用了Mybatis
@Mapper
public interface StudentMapper {
	@Select("SELECT * FROM students WHERE stuno = #{stuno}")
	public StudentPO getStudentByID(Integer stuno);
    
	@Insert("INSERT INTO students VALUES(#{stuno}, #{sanme})")
	public Integer insertNewStudent(StudentPO po);
	//@Update  //Delete
}


/***************************************************
* Service层
***************************************************/
// com.neusoft.service 包下的 StudentService.java
// 这是一个interface
public interface StudentService {
	public StudentVO getStudentByID(Integer stuno);	//根据stuno查询学生对象
	public void updateStudentByID(StudentVO vo);	//根据vo中stuno更新学生对象
	public void addStudent(StudentVO vo);			//将vo中的数据新增
	public void deleteStudentByID(Integer stuno);	//根据stuno删除学生对现象
}

// com.neusoft.service.impl 包下的 StudentServiceImpl.java
// 这是 StudentService 的实现类
// 注解说明：
// @Service 表明这是一个Service
// @RequiredArgsConstructor 增加这个注解后，SpringBoot 会在项目启动时
//		会自动创建本类下所有使用final标记的成员
// 		添加了RequiredArgsConstructor注解之后
//		private final StudentMapper mapper; 就会自动生成，不用手动初始化
//   	通过这个注解可以实现自动注入
@Service 
@RequiredArgsConstructor 
public class StudentServiceImpl implements StudentService {
	private final StudentMapper mapper;
	@Override
	public StudentVO getStudentByID(Integer stuno) {
		StudentPO po = mapper.getStudentByID(stuno);
		if(po == null){
			return null;
		}
		//po -> vo
		StudentVO vo = new StudentVO();
		vo.setStuno(po.getStuno());
		vo.setSname(po.getSname());
		return vo;
	}
	@Override
	public void updateStudentByID(StudentVO vo) {
	}
	@Override
	public void addStudent(StudentVO vo) {
	}
	@Override
	public void deleteStudentByID(Integer stuno) {
	}
}


/**************************************************
* Controller层
**************************************************/
@RestController
@RequiredArgsConstructor // 这个注解和Service中用到的那个注解一样，是用来实现自动注入的
public class StudentController {
	private final StudentService service;

	@GetMapping("/student/{stuno}")
	public ResponseResult findStudent(@PathVariable Integer stuno){
		//根据学号查询到了对应的对象
		StudentVO vo = service.getStudentByID(stuno);
		if(vo != null){
			return ResponseResult.isOK(vo);
		}else{
			return ResponseResult.isFail("没有学号是："+stuno+"的数据");
		}
	}

	@PostMapping("/student/{stuno}")
	public ResponseResult updateStudent(@PathVariable Integer stuno, @RequestBody StudentVO vo){
		return ResponseResult.isOK();
	}

	@PutMapping("/student/{stuno}")
	public ResponseResult addStudent(@PathVariable Integer stuno, @RequestBody StudentVO vo){
		return ResponseResult.isOK();
	}

	@DeleteMapping("/student/{stuno}")
	public ResponseResult deleteStudent(@PathVariable Integer stuno){
		return ResponseResult.isOK();
	}
}


```

#### 依赖注入的三种写法

上一小节的演示中，使用了RequiredArgsConstructor进行依赖注入，除了这个注解外，还有两种依赖注入方法

##### 方法1：使用Autowire

```java
@RestController
public class StudentController {
	//依赖注入
	//方式1： 利用@Autowired自动注入（旧版本项目）
	@Autowired    //@Autowired注解有要求：StudentService（被注入接口）必须有且只有唯一一个实现类（StudentServiceImpl）
	private final StudentService service;
    
    //......
}
```

##### 方法2：使用构造方法注入

```java
@RestController
public class StudentController {
	private final StudentService service;
	//方式2： 利用构造方法自动注入
	//要求：唯一的构造方法（不允许重载）
	public StudentController(StudentService service){
		this.service = service;
	}
	
    //...
}
```

##### 方法3：使用RequiredArgsConstructor注入

```java
@RestController
@RequiredArgsConstructor // 这个注解和Service中用到的那个注解一样，是用来实现自动注入的
public class StudentController {
	private final StudentService service;
    //......
}
```

当然，实际情况中，可能存在StudentService这个接口有多个实现类的情况（比如：StudentServiceImpl1、StudentServiceImpl2、StudentServiceImpl3....）；SpringBoot并不会自作主张帮你选一个实现类进行初始化，这时候需要程序员手动指定，使用哪个类进行初始化

```java
@RestController
@RequiredArgsConstructor // 这个注解和Service中用到的那个注解一样，是用来实现自动注入的
public class StudentController {
     @Qualifier("paymentWechatImpl2") // 选择 paymentWechatImpl2 作为实例化service的类
	private final StudentService service;
    //......
}
```



### AOP 面向切面

使用动态代理模式实现



# 创建SpringBoot项目

1. 官网 https://start.spring.io/

2. 根据需求勾选
    2.1 注意1：Package name很重要，未来的项目中，只有在Package name中写的代码才能使用SpringBoot特性
    2.2 注意2：打包方式，一般情况下开发使用jar包即可，war包一般用于真实部署

3. 根据需要添加插件

4. 点击生成，此时会下载一个压缩包，其本质是一个maven项目

5. 修改IDEA的Maven配置

    ![](./imgs/IDEA配置Maven.png)

6. 使用IDEA打开第4步中下载的压缩包里的pom.xml

## Controller层

首先建立一个controller包：

![](./imgs/创建controller.png)

编写代码:

```java
package com.neusoft.demo.controller;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import java.util.Date;

@RestController // 注解，表明类TestController是一个controller
public class TestController {

    @RequestMapping("/time.do") // 注解，使用time.do请求，会触发getSystemTime函数
    public Date getSystemTime()
    {
        return new Date();
    }

}
```

### 请求方式 RESTful风格

RESTful风格：使用同一个URL，根据不同的请求方式，决定对数据的处理

1. GET 查询数据
2. POST 修改数据
3. PUT 新增数据
4. DELETE 删除数据

相关注解：

RequestMapping：支持GET、POST、put、delete

GetMapping：支持GET

PostMapping：支持POST

PutMapping：支持PUT

DeleteMapping：支持DELETE

```java
// RequestMapping较为特殊，它可以手动指定接受哪几种请求
// 这样写，time.do只会接受get和post请求 
@RequestMapping(value = "/time.do", method = {RequestMethod.GET, RequestMethod.POST})
```



### 数据提交

前端的数据如何交给后端？（前端如何传参？）

#### GET的提交方式

GET请求比较特殊，GET通过URL提交数据

```http
http://localhost:8080/info.do?account=123&passwd=456
这里可见密码被明文传输了
```

服务端通过account和passwd形参获取参数值

```java
@RestController
public class Test2Controller {
	@GetMapping("/submitData.do")
	public String getData1(String account, String password){
		return "OK:"+account+":"+password;
	}
}
```



由于GET请求会把所有信息附加在URL里提交，因此要避免使用GET提交敏感数据（比如密码），此外，URL有长度限制，因此也不能使用get方法提交文件

#### POST、PUT、DELETE 的提交方式

##### 通过URL

前端：和GET一样，把参数明文放在URL里；

服务端：通过 同名参数 获取参数值



##### 通过Form URL encoded

前端：利用报文体（body）传递数据

服务端：直接在方法上设置同名参数  （少用）



##### 通过Multpart Form

前端：利用报文体(body)传递数据，允许上传文件

服务端：直接在方法上设置同名参数（文件需要另外处理）



##### 通过JSON （常用）

前端：通过JSON提交数据，利用报文体（body）

服务端：需要通过一个对象或者Map集合接受数据对象或map需要通过注解@RequestBody修饰

```java
// 声明一个VO
// VO 映射视图层（View）的数据对象
@Setter
@Getter
@AllArgsConstructor
@NoArgsConstructor
public class LoginVO {

	private String account;
	private String password;

}

// 通过LoginVO对象 或 通过Map集合
// 均可以获取json中的内容
@RestController
public class Test2Controller {
	@PutMapping("/submitData.do")
	public String getData3(@RequestBody LoginVO vo){
		return vo+":"+vo.getAccount()+":"+vo.getPassword();
	}
    
	@DeleteMapping("/submitData.do")
	public String getData4(@RequestBody Map<String, Object> map){
		return map+":"+map.get("account")+":"+map.get("password");
	}
}
```



##### URL参数化（常用）

前端：将参数作为URL的一部分

服务端：通过注解@PathVariable绑定URL参数部分

这样做的好处是，可以实现动态的请求

```java
@RestController
public class Test2Controller {
	@PostMapping("/info/{empid}")
	public String getData5(@PathVariable Integer empid){
		return "处理："+empid+"数据";
	}
}
```

针对这个例子：可以使用/info/11111请求，也可以使用/info/2222请求，empid会接住



## Model层

### Service层





### Mybatis--持久化层

#### 为项目引入Mybatis

使用Maven引入下列组件

1. JDBC依赖
2. Mybatis依赖
3. 数据库驱动依赖
4. 连接池






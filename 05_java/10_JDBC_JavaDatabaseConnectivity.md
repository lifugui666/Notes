# JDBC

jdbc -- java直连数据库

通过驱动，让java可以直接连接对应的数据库进行操作；

这篇笔记从最原始的jdbc操作进行介绍；

## Maven

场景：

项目1依赖：abc.jar、spring.jar、log.jar 

项目2依赖：spring.jar、log.jar

两个项目需要的依赖不同，且有部分重合；

-------------------------------------

传统方式：手动下载依赖包，手动配置依赖包；

Maven：项目下不再放jar，而是有一个pom.xml配置文件，描述依赖关系；maven拥有一个本地仓库，如果本地仓库没有，maven就会去远端下载；（类似linux的包管理工具）

### 配置

1. 下载maven并解压

2. 在根目录下创建一个文件夹\resp

3. 复制\resp的绝对路径

4. 打开conf\settings.xml

5. 找到被注释的<LocalRepository>，然后把自己创建的路径写进去

   <**localRepository**>D:\neu\apache-maven-3.9.14-bin\apache-maven-3.9.14\resp</**localRepository**>

6. 将/bin写入系统变量中

### 项目结构

```shell
src
 |--main
 |   |--java      # 放源码
 |   |--resource  # 放不需要编译的内容
 |--test
 |   |--java      # 放源码
 |   |--resource  # 放资源
 |----pom.xml # 重要
```

### 使用Maven

在pom.xml里写好项目所所需要的库

```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>

    <groupId>com.neusoft</groupId>
    <artifactId>proj0922</artifactId>
    <version>1.0-SNAPSHOT</version>

    <properties>
        <maven.compiler.source>21</maven.compiler.source>
        <maven.compiler.target>21</maven.compiler.target>
        <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
    </properties>
    <dependencies>
        <dependency> <!--在dependency里写明项目所需的依赖-->
            <groupId>org.postgresql</groupId>
            <artifactId>postgresql</artifactId>
            <version>42.7.13</version>
        </dependency>
    </dependencies>
</project>
```

在pom.xml所在的路径下执行

```shell
mvn clean install
```



## 数据库操作

**数据库查询 和 数据库增删改 用的不是一个类，但用法高度一致，步骤如下**

1. 编写一个String，该String是你要执行的SQL语句
2. 使用步骤1里的String，创建一个PreparedStatement（预编译语句）；
3. （如果步骤1中的String语句中，带有'?'的话，将 问号 替换为 真正的数据）
4. 执行 预编译语句，这一步也是 查询、增删改之间的有差异的地方：查询使用的方法是executeQuery()；增删改使用的方法是executeUpdate()；

### 数据库查询

```java
 //1. 加载数据库驱动（postgres驱动）（不同数据库不同的驱动类）
Class.forName("org.postgresql.Driver"); // 这里使用了反射
//2. 定义连接字符串（不同数据库不同写法）
String url = "jdbc:postgresql://localhost:5432/HR_DB";// url，不同的数据库格式有所不同
String user = "postgres"; // 用户名
String pass = "passwd";   // 密码
//3.创建数据库的连接
Connection conn = DriverManager.getConnection(url, user, pass);
System.out.println(conn);

//4.声明要执行的SQL语句
String sql = "SELECT * FROM dept";

//5.创建一个Statement用于加载SQL
PreparedStatement pst = conn.prepareStatement(sql);
//6.声明结果集对象获取SQL语句的执行结果
ResultSet rs = pst.executeQuery();
//7.迭代遍历数据
while (rs.next()) {
    //取数据操作
    int deptno = rs.getInt("deptno"); //结果集名字是“deptno”列
    String dname = rs.getString("dname");  //结果集的第2列
    int locid = rs.getInt("locid");

    //Date hiredate = rs.getDate("hiredate");
    System.out.println(deptno + "\t" + dname + "\t" + locid);
}
//8.依次关闭ResultSet，PreparedStatement，Connection
rs.close();
pst.close();
conn.close();
```

### 数据库增删改

```java
//1. 加载数据库驱动（postgres驱动）（不同数据库不同的驱动类）
Class.forName("org.postgresql.Driver");

//2. 定义连接字符串（不同数据库不同写法）
String url = "jdbc:postgresql://localhost:5432/HR_DB";
String user = "postgres";
String pass = "passwd";

//3.创建数据库的连接
Connection conn = DriverManager.getConnection(url, user, pass);

//4.声明要执行的SQL语句
String sql = "INSERT INTO dept VALUES(?, ?, ?)";

//5.声明Statement加载SQL
PreparedStatement pst = conn.prepareStatement(sql);
//6.为？依次绑定数据
int deptno = 50;
String dname = "INFO";
int locid = 100;

pst.setInt(1, deptno); //将deptno的值绑定给SQL中的第一个？
pst.setString(2, dname);
pst.setInt(3, locid);

//pst.setDate(4, new java.sql.Date(System.currentTimeMillis()));
//7.执行DML操作
int x = pst.executeUpdate(); //返回的影响了数据库中的多少条数据
System.out.println("本次操作，影响了"+x+"条数据");

pst.close();
conn.close();
```



### 动态查询

实际使用中会出现，给定参数，然后使用参数构建SQL语句的需求；如果参数是null，那么通常代表条件不存在

这种需求对sql语句的建立带来了一些麻烦，如果条件不存在，那么使用“?”做占位符，然后再通过PreparedStatement替换的做法也行不通，替换通常用来替换参数，而很难消去一个条件；

```java
StringBuilder sql = new StringBuilder("SELECT * FROM users WHERE 1=1");
List<Object> params = new ArrayList<>();

if (name != null && !name.isEmpty()) {
    sql.append(" AND name = ?");
    params.add(name);
}
if (age > 0) {
    sql.append(" AND age >= ?");
    params.add(age);
}

PreparedStatement ps = conn.prepareStatement(sql.toString());
for (int i = 0; i < params.size(); i++) {
    ps.setObject(i + 1, params.get(i));
}
ResultSet rs = ps.executeQuery();
```

思想是，先写where 1=1 条件，然后再根据参数的情况，逐条添加条件语句



## JDBC封装

JDBC操作中，有一些操作明显是可以被封装的：

1. 建立JDBC连接这种标准写法，明显可以封装为一个方法；
2. 关闭查询结果、关闭PreparedStatement、关闭数据库连接，三者明显可以通过重写close封装

因此，考虑建立一个工具类，用于封装JDBC，减少代码重复；

**一般情况下，以util命名工具类**

```java
/* 这个类干了什么？
* 1. 使用 常量 记录url、用户名、密码；并使用静态代码块加载驱动、读取配置文件，以初始化url、用户名、密码
* 2. 编写了静态方法getConnection，用于创建一个连接并返回
* 3. 以重载的形式，编写了4个close静态方法，用于实现各种close需求
**/
public class DBUtil {

	private static final String url;   //硬编码问题
	private static final String user;
	private static final String pass;

	static{
		//1.加载驱动
		try {
			Class.forName("org.postgresql.Driver");
		} catch (ClassNotFoundException e) {
			System.out.println("PostgreSQL的数据库驱动加载失败");
		}
		//2.读取配置文件
		Properties p = new Properties();
		//加载DBUtil这个类所在目录中的DBConfig.properties文件
		try {
			p.load(DBUtil.class.getResourceAsStream("DBConfig.properties"));
		} catch (IOException e) {
			throw new RuntimeException(e);
		}
		String host = p.getProperty("host");
		String port = p.getProperty("port");
		String db = p.getProperty("database");

		url = "jdbc:postgresql://"+host+":"+port+"/"+db;
		user = p.getProperty("user");
		pass = p.getProperty("pass");

	}
	
    // 用于获取一个连接
	public static Connection getConnection(){
		Connection conn = null;
		try {
			conn = DriverManager.getConnection(url, user, pass);
		} catch (SQLException e) {
			System.out.println("创建数据库连接失败");
			e.printStackTrace();
		}
		return conn;
	}

    // 用于关闭一个连接
	public static void close(Connection conn){
		if(conn != null){
			try {
				conn.close();
			} catch (SQLException e) {
				throw new RuntimeException(e);
			}
		}
	}

    // 用于关闭一个 PreparedStatement
	public static void close(PreparedStatement pst){
		if(pst != null){
			try {
				pst.close();
			} catch (SQLException e) {

			}
		}
	}
    
    // 同时关闭预编译语句与连接
	public static void close(PreparedStatement pst, Connection conn){
		close(null, pst, conn);
	}

    // 同时关闭 查询结果、 预编译语句、 连接
	public static void close(ResultSet rs, PreparedStatement pst, Connection conn){
		if(rs != null){
			try {
				rs.close();
			} catch (SQLException e) {

			}
		}
		if(pst != null){
			try {
				pst.close();
			} catch (SQLException e) {

			}
		}
		if(conn != null){
			try {
				conn.close();
			} catch (SQLException e) {
				throw new RuntimeException(e);
			}
		}
	}

}
```

### properties文件的使用

java中可以使用properties文件很方便的保存配置信息

```java
// DBConfig.properties 文件
host=localhost
port=5432
database=hr
user=hr
pass=hr

// java中读取的代码
Properties p = new Properties();
try {
    p.load(DBUtil.class.getResourceAsStream("DBConfig.properties"));
} catch (IOException e) {
    throw new RuntimeException(e);
}
String host = p.getProperty("host");
String port = p.getProperty("port");
String db = p.getProperty("database");
```

**class.getResourceAsStream("xxx")方法，是从target下取文件，并不是从src下取文件**





## 代码分层Model层（Service\DAO）

**Service和DAO之间的关系：依赖，Service依赖于DAO**

Service描述的是：事务

DAO描述的是：SQL语句

```shell
# 以转账举例

# 转账本身是个事务
# 但转账本身由两个SQL操作组成：A扣钱、B加钱

# 事务最起码要保证原子性
# 即：A向B转账过程，A扣钱、B加钱，这两个事要么一起成功要么一起失败
# 对外而言，“转账”这个事儿，就是一个服务，一个Service

# 转账这个Service中，A扣钱、B加钱明显需要两个SQL操作实现
# 这两个SQL语句，可以被抽象成两个方法，写在DAO里
```

**DAO负责执行SQL操作，Service负责保证事务的原子性**



### DAO

**注意：专门搞了一个包com.xxx.dao来放各种DAO**

```java
public class BankDAO {
    
	public void add(Connection conn, String bname, int num) throws SQLException {
		String sql = "UPDATE banks SET money = money + ? WHERE bname = ?";
		PreparedStatement pst = null;

		try {
			pst = conn.prepareStatement(sql);
			pst.setInt(1, num);
			pst.setString(2, bname);
			pst.executeUpdate();
		} catch (SQLException e) {
			throw e;  //先抓再放
		} finally {
			DBUtil.close(pst); // !!! 最后只关闭pst，conn不归DAO管理
		}
	}

	public void substract(Connection conn, String bname, int num) throws SQLException {
		String sql = "UPDATE banks SET money = money - ? WHERE bname = ?";
		PreparedStatement pst = null;

		try {
			pst = conn.prepareStatement(sql);
			pst.setInt(1, num);
			pst.setString(2, bname);
			pst.executeUpdate();
		} catch (SQLException e) {
			throw e;  //先抓再放
		} finally {
			DBUtil.close(pst); // !!! 同上
		}
	}
    
}
```





### Service

**注意：专门搞了一个包com.xxx.Service来放各种Service**

service需要负责：

1. 创建connection，并且负责在最后释放这个conn
2. 关闭自动提交（重要！只有这样才能保证原子性）
3. 调用DAO的方法完成事务
4. 一旦DAO执行失败，要执行回滚
5. 如果DAO全部执行成功，执行commit

```java
public class BankService {

	private BankDAO dao = new BankDAO();

	/**
	 * 带有事务控制的service - dao方法的编写
	 * @param from
	 * @param to
	 * @param num
	 */
	public void zhuanzhang(String from, String to, int num){
		Connection conn = DBUtil.getConnection();
		try 
        {
			conn.setAutoCommit(false); //关闭自动提交
			dao.add(conn, to, num);
			dao.substract(conn, from, num);
			conn.commit(); //事务提交
		} 
        catch (SQLException e) 
        {
			try 
             {
				conn.rollback();  //事务回滚
		    } 
             catch (SQLException ex) 
             {
                 //？ 这里做了什么呢？
			}
		} 
        finally 
        {
			DBUtil.close(conn);
		}
	}
}
```



### 异常处理

当DAO中的SQL操作出现异常时，先catch，再在catch中向上throw掉这个异常，然后进入finally，关闭pst；

**注意，DAO中不会关闭数据库链接，数据库连接并非DAO创建的，不归DAO管理**
































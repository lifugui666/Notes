# 语法规则

在一个vue文件里，存在三块内容

```vue
<script setup lang="ts">
    //.... 写逻辑
</script>

<template>
	<!--.... 写页面 -->
</template>

<style lang="css" scoped>
    /*.... 美化页面*/
</style>
```



## 1. HTML   =========================

html中的标签，类似于其他语言中的关键字，每一个标签对应一种页面里的样式，不过大部分标签都可以被划分到<div>和<span>这两类下；

### \<div\>和\<span\>（块 和 行内）

div是典型的块，一个div一定会占据一整行

span是典型的行内，一个span会根据自身内容的长度决定占据的位置

**一行只能放下一个块，却可能放得下很多 行内**

### \<h1\> 标题 (块)

h1~h6，分别对应不同大小的标题

```html
<h1>容器标记</h1>
<h2>标题字体2</h2>
<h6>标题字体6</h6>
```

![](D:\Notes\05_java\imgs\01-h1.png)



### div 块 （块）

```html
<div>这是一个块元素</div>
```



### span 行内 (行内)

```html
<span>这是一个行内元素</span>
```



### \<b\> \<i\> \<u\> \<sub\> \<sup\>（行内）

```html
<b>加粗字体</b>
<i>倾斜字体</i>
<u>下划线字体</u>
<div>水的分子式是：H<sub>2</sub>O</div>
<div>2<sup>10</sup> == 1024</div>
```

![](D:\Notes\05_java\imgs\02-b.png)



### \<ul\> \<li\> \<a\> 列表 (块)

无序列表，其中`<ul>`是列表，`<li>`是列表项，`<a>`是超链接

```html
  <ul>
    <li class="list">
      <a href="https://www.baidu.com">百度</a>
    </li>
    <li class="list">
      <a href="#">第二项</a> <!--"#"是空锚点，锚定当前页面的顶端-->
    </li>
    <li class="list">
      <a href="#">第三项</a>
    </li>
    <li class="list">
      <a href="#">第四项</a>
    </li>
  </ul>
```

![](D:\Notes\05_java\imgs\03-ul.png)



### \<table\> \<thread\> \<tr\> \<td\> \<tbody\> 

`<table>` `<thread>` `<tr>` `<tbody>`是 块

`<td>`是 行内

```html
<table> <!--表-->
    <thead>  <!--表头-->
      <tr>  <!-- 一行，同时请注意表头内只允许包含-->
        <th>部门编号</th> <!--单元格-->
        <th>部门名称</th>
        <th>地点ID</th>
      </tr>
    </thead>
    <tbody> <!--表格体-->
      <tr>
        <td>10</td>
        <td>总裁办</td>
        <td>101</td>
      </tr>
      <tr>
        <td>20</td>
        <td>人力资源部</td>
        <td>101</td>
      </tr>
      <tr>
        <td>30</td>
        <td>第一研发中心</td>
        <td>102</td>
      </tr>
    </tbody>
  </table>
```

![](D:\Notes\05_java\imgs\04-table.png)



### \<form\> （块）

`<form>`是 HTML 中用于收集用户输入并提交数据的容器标签，主要作用包括：

* 数据采集：包裹各种输入控件（如文本框、复选框、下拉菜单、按钮等），统一管理用户填写的信息。
* 数据提交：通过 action 属性指定数据发送到的服务器地址，通过 method 属性指定 HTTP 请求方式（GET 或 POST）。
* 表单验证：配合 HTML5 内置验证属性（如 required、pattern、minlength 等），在提交前对用户输入进行初步校验。
* 编码与传输：通过 enctype 属性控制数据的编码方式（如上传文件时必须设为 multipart/form-data）。
* 重置与提交：提供默认的提交按钮（type="submit"）和重置按钮（type="reset"），方便用户操作。



### \<input\> （行内）

通过设置type，这个标签可以作为：

1. 输入框          `type="text"`
2. 密码框          `type="password"`
3. 日期框          `type="date"`
4. 时间框          `type="time"`
5. 数字框          `type="number"`
6. 滑块              `type="range"`
7. 单选组          `type="radio"`
8. 多选组         `type="checkbox"`
9. 颜色选择框  `type="color"`
10. 文件选择框  `type="file"`
11. 隐藏的框     `type="hidden"`
12. 按钮            `type="button"`

```html
<div>
    文本框：<input type="text" value="haha" readonly>
</div>
<div>
    密码框：<input type="password" placeholder="请输入密码">
</div>
<div>
    日期框：<input type="date" value="1997-10-19" >
</div>
<div>
    时间框：<input type="time" value="15:27">
</div>
<div>
    数字框：<input type="number" value="10" max="100" min="0" step="10">
</div>
<div>
    滑块：<input type="range" value="0" max="100" min="0" step="10">
</div>
<div>
    单选组（通过name约束“组”）：
      <input type="radio" name="sex" value="1">男
      <input type="radio" name="sex" value="2">女
      <input type="radio" name="sex" value="3">保密
</div>
<div>
    多选组（通过name约束“组”）：
      <input type="checkbox" name="fav" value="1">吃
      <input type="checkbox" name="fav" value="2">喝
      <input type="checkbox" name="fav" value="3">玩
</div>
<div>
    颜色：<input type="color">
</div>
<div>
    文件：<input type="file">
</div>
<div>
    隐藏：<input type="hidden">  <!-- 看不见的text -->
</div>
<div>
    按钮：<input type="button" value="提交">
</div>
```

![](D:\Notes\05_java\imgs\05-input.png)



### \<button\> 按钮 (行内)

另一种实现按钮的方法

```html
<div>
    按钮：<button type="button">提交</button>
</div>
```



### \<select\> \<option\> 下拉表 (行内)

```html
 <div>
    下拉列表：
      <select>
        <option value="1">沈阳</option>
        <option value="2">大连</option>
        <option value="3">鞍山</option>
        <option value="4">抚顺</option>
      </select>
 </div>
```



### \<textarea\> 文本框（行内）

```html
<div>
    文本区域：<textarea cols="20" rows="5">111aaaaa</textarea>
</div>
```



## 2. CSS =========================

如果说html决定了“页面上有什么”

CSS则决定“页面上的东西长什么样”

### 2.1 CSS引入方式

#### 1. 内联样式

内联样式就是直接写在html标签里写样式

```vue
<div style="color:read">红色</div>
<!--没有单独写css，通过style直接在div里写了样式-->
```



#### 2. 嵌入样式

将样式以选择器的样式，编写在`<style>`块中

```vue
<script setup lang="ts">
</script>

<template>
	<!--在template中写html-->
</template>

<style>
    /*在style中写CSS*/
</style>
```



#### 3. 外联样式（推荐）

传统网页通过`<link>` 引入外部css文件

vue通过import导入外部css文件

```typescript
// main.ts中的内容
import { createApp } from 'vue'
import './style.css'  // 通过import
import App from './App.vue'

createApp(App).mount('#app')
```





### 2.2 CSS的选择器

#### 1. 标记选择器

直接标记名进行样式适配

```css
div{color:bule;} 
/*所有div都会变成这样*/
```

#### 2. ID选择器

根据锚点（id）值进行样式适配，不同的锚点不能重复

```html
<div>这是<span id="sp1">一个</span>块元素</div>
<div id="div1">演示“传统盒子模式”</div>
```

```css
#div1{  			/*要使用 # + id */
    padding: 10px;   /*内间距：内容和边框的距离 */
    padding-top: 50px;
    border: 3px solid #FF0000; /* 边框 */
    margin: 8px;   /*外边距：边框距离外部其他内容的距离 */
    width: 500px;
    height: 100px;
    box-sizing: border-box;  /*基于边框border设置宽高，默认基于内容设置宽高 */
}
#sp1{
    color: aqua;   /* 文字颜色 */
    font-weight: bold;  /* 文字加粗 */
    font-size: 24px;  /* 文字的字号  控制文本大小 */
}
```



#### 3. 类选择器

预先定义一个样式（称之为类），然后等待 HTML “调用” 这个样式（类）；

```css
/* 定义myfont mysize两个类 */
.myfont{font-family:宋体}
.mysize{font-size:18px}

/* html中 */
<div class="myfont" > 字体设置为宋体 </div>
<div class="mysize" > 字体设置为18px </div>

/* 同时引入2个样式 使用空格分隔 */
<div class="myfont mysize"> 同时设置宋体 18px </div>
 
```



#### 4. 选择器组合使用

```css
div p{color:blue;}
/*对所有 div标记 中的 p标记 生效*/
```



#### 5. 选择器并列关系

多个选择器间使用逗号分隔

```css
div,p{color: blue;} 
/*对所有的<div>和<p>标记生效*/
```



#### 6. 交集选择器

```css
div.aside{color: blue;}  
/* 使用了aside样式的div */
/*适配 <div class="aside">*/
```



#### 7. 属性选择器

````css
input[type="text"]{...}  /* 适配type为text的<input>标记 */
div[id]{...} /* 适配有id的<div> */
input[id][type="password"]{...} /* 有id属性的密码框 */
````



#### 8. 伪类选择器

```css
否定:         input:not([type='text']) /* 选择type不是text的input */
偶数序列：    #table1 tr:nth-child(even)   2,4,6...
奇数序列:     #table1 tr:nth-child(odd)    1,3,5,7...
具体序列:     #table1 tr:nth-child(2)   （第2个）
```



### 2.3 样式就近原则(CSS优先级)

由于CSS拥有多种引入方式，并且有多种选择器，而且这些选择器还能组合使用

那么，如果一个标记使用了多种方式设置了他的样式，那么哪个会生效？

生效的顺序：

**内联(style="...") >> ID >> 标记选择器 >> 类 **

有个特殊用法：!important

````css
/* 元素选择器 */
p { font-size: 16px !important; }

/* ID 选择器 */
#header { background: black !important; }

/* 属性选择器 */
input[type="submit"] { color: white !important; }

/* 伪类选择器 */
a:hover { text-decoration: none !important; }

/* 内联样式（HTML 中） */
<div style="color: red !important;">文本</div>
````

只要加了!important，那么这条样式的优先级就会被拉到最高，如果大家都加了，那还是按照之前的生效顺序来



### 2.4 CSS常用样式

#### 1. 文本

```css
font-family:宋体,楷体 /*字体*/
font-size:18px  /*字体大小*/
text-align:left | center | right /*对其方式*/
font-style:normal | italic /*倾斜*/
font-weight:noraml | bold /*加粗*/
font-decoration: none | line-through | underline /*无划线、贯穿线、下划线*/
color:red  /*文本颜色*/
```



#### 2. 背景

```css
background-color:单词|#hex|RGB /*背景颜色*/
background-image:url /*图片链接*/
background-repeat: repeat|no-repeat|repeat-x|repeat-y /*平铺 不平铺 水平平铺 处置平铺*/
background-position:px px 或 % % /*决定的哪一块*/
```



#### 3. 尺寸

```css
width:100%
height:auto

/* 宽高以百分比等形式设置为动态宽高时，可以通过 */
max-width
min-width   
max-height
min-height
/* 约束其最大和最小的宽度和最大最小高度 */

/* 当使用一个小框子包含更大的框子时 */
<div>   ---  尺寸小
      <div></div>    --- 尺寸大
</div>
在容器上设置：overflow: hidden | scroll | auto;
hidden：溢出部分隐藏
scroll：溢出部分滚动条显示（始终显示滚动条）
auto： 不溢出不显示滚动条，溢出显示滚动条
```



#### 4. 盒子模式（旧）

```css
padding: /*内容和边框之间的间距*/
border:  /*边框*/
margin:  margin-left|margin-right /*边框与其默认位置的偏移*/

box-sizing:content-box | border-box
/* 其中context-box时，width和height设置的是内容和尺寸
   border-box时，width和height设置的是boder的尺寸*/
```



#### 5. 盒子模式（新）--flex布局（非常重要）

```css
/* 通过如下设置，开启flex，容器内启用flex方式布局 */
display: flex;
```

主轴和侧轴：可以指定水平方向或垂直方向为主轴，一旦指定了主轴，另一个就是侧轴

```css
/* 设置主轴方向 */
flex-direction: row | row-reverse | column | column-reverse
/* 上述四个值分别对应： 从左到右 从右到左 垂直从上到下 垂直从下到上*/
```

是否换行： 如果选择不换行，那么item们就会挤在一行里面

```css
flex-wrap: nowrap | wrap | warp-reverse
/* 上述三个值对应 不换行 换行(新的一行在旧的一行的下面) 换行(新的一行在旧的一行上面)*/
```

排布方式：如何安排内容的布局

```css
justify-content:
flex-start /*起端对齐*/
flex-end /*末端对其*/
center /*居中*/
space-between /*两端对齐，项目之间等距*/
space-around /*每个项目两侧间距相等*/
space-evenly /*项目之间和两端间距都相等*/
```



常见用法：居中 等分 三栏(中间一栏自适应)

```css
/*居中*/
.parent {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 300px;
}


/*等分*/
.parent {
  display: flex;
}
.child {
  flex: 1;   /* 每个子元素均分宽度 */
}


/*圣杯*/
.container {
  display: flex;
}
.left, .right {
  width: 200px;
  flex-shrink: 0;
}
.middle {
  flex: 1;
}

```





## 3. TypeScript =========================

### 3.1 变量

注意：ts中`Number`和`number`不是一个东西，小写的`number`是基本类型，`Number`是其对应的包装类型

在**开发过程中应当尽量使用小写**

```vue
<script setup lang="ts">
    /*
     * 1. let和const：let声明的变量可以被修改；const声明的变量不能被修改，
     *                且必须在声明的时候初始化
     * 2. ref：使用ref声明的数据会变成 响应式数据
     *         只要这个数据被改变，绑定了这个数据的前端显示就会自动刷新
	 */
    
	import { ref, type Ref, computed, watch, onMounted } from 'vue';
    // number 整数、浮点数
    // string 字符串
    // boolean 布尔
    // object 对象类型：Array Date 自定义的类
    // function
    // null
    // undefined
    let account:Ref<string> = ref("张三"); // Ref<string>显式的指明了account的类型
    let input_type = ref("password"); // 也可以自动推断类型
    let css_style = {
        "backgroundColor": "hotpink",
        "color": "blue"
    }
    let css_class = {
        "myfont": true,
        "mysize": true
    }
</script>
```



### 3.2 事件

```vue
<script setup lang="ts">
    import { ref, type Ref, computed, watch, onMounted } from 'vue';
    /*
      常见事件
      click   鼠标左键单击事件
      input   输入控件内容改变事件（文本框外观）
      change  <select>中选中项改变事件
      focus   某个控件获得焦点事件
      blur    某个控件失去焦点事件
      mouseover / mouseenter  鼠标光标悬停事件
      mouseout  / mouseleave  鼠标光标离开事件
      mousemove   鼠标光标移动
      事件绑定的一定是一个function
    */
    let button_text = ref("显示")
    const showOrHide = function(){
       if(button_text.value == "显示"){
          button_text.value = "隐藏"
          input_type.value = "text";
       }else{
          button_text.value = "显示"
          input_type.value = "password";
       }
    }
</script>

<template>
    <div>密码：
      <input :type="input_type" value="123456">
      <button @click="showOrHide">{{ button_text }}</button>
    </div>
</template>
```





### 3.3 watch

执行逻辑：

mynum变化 --> 执行function修改tooltip的值-->由于tooltip是ref，因此UI上的值会自动改变

```vue
<script setup lang="ts">
    import { ref, type Ref, computed, watch, onMounted } from 'vue';
    
    let mynum = ref(50);
    let tooltip = ref('');
    const changeMyNum = function (){
        let x = Math.random()*100;  //[0,100)随机浮点数
        mynum.value = Math.floor(x);  //[0,100)随机整数
    }
    
	//监控mynum的变化
    watch(mynum, function(new_num, old_num){
        //alert(`旧值:${old_num}, 新值:${new_num}`);
        if(new_num > old_num){
            tooltip.value = "数据变大了";
        }else if(new_num < old_num){
            tooltip.value = "数据变小了";
        }else{
            tooltip.value = "数据没有变化";
        }
    });
</script>

<template>
    <div>
        <div>{{ mynum }} - {{ tooltip }}</div> <!-- 30 - 数据变大了 -->
        <div>
            <button @click="changeMyNum">随机</button>
        </div>
    </div>
</template>
```



### 3.4 计时器

```vue
<script setup lang="ts">
	//某些程序，需要页面加载时自动执行
    //  () => {}   非使用this场景下，等同于 function (){}
    /*
      setTimeOut(函数, 整数ms)    延迟整数ms后，执行函数
        setTimeOut(function (){ ... }, 2000)    2s后执行function

      setInterval(函数, 整数ms)    延迟整数ms后，执行函数，反复上述步骤
    */
    let timer = ref(0);
    onMounted(() => {
        setInterval(() => {
            timer.value++
        }, 1000);
    });
</script>    
```





### 3.5 路由

**解决什么问题？**

我不可能把所有的页面都写在`App.vue`这一个文件里，路由可以把vue文件和url对应起来；

在页面上，有`<routerView>`或`<router-view>`，他们是**路由窗体**

路由的切换是在路由窗体中完成的，下图所示的红框框就是路由窗体

![image-20261022132337369](D:\Notes\05_java\imgs\vue-路由窗体.png)

使用路由前，需要先安装`vue-router`

路由涉及到的概念：

1. router 路由的管理器，管理整个路由
2. routes 路由配置中的关键属性，配置路由映射（把某个vue文件和url映射起来）
3. route 单个路由

#### 1. 安装vue-router

```shell
npm install vue-router
# 执行就完事了
```



#### 2. 配置文件 index.ts

根据如下结构创建路径、文件

```shell
src
 |--router  # 需要新建
 |    |---index.ts # 写路由配置
 |
 |--views
      |-- login.vue # 提供真正的内容页
      |-- system.vue # 提供真正的内容页
App.vue # 只提供路由窗体（里面放路由窗口）
main.ts # 需要把我们写好的index.ts引入到main.ts中
```



**index.ts**

routers[] --> router --> export

```ts
import {createRouter, createWebHistroy} from 'vue-router'

const routers:any[] = [
    {
        path: "/",
        redirect: "/login" // 重定向
    },
    {
        path:"/login", // url的path
        component:import("../views/login.vue") // 对应的文件的位置
    },
    {
        path: "/system",
        component: import("../views/system.vue"),
        children: [
            {
                path: "",
                redirect: "/system/home" // /system被重定向到 /system/home
            },
            {
                path: "home",   //   /system/home
                component: import("../views/home.vue")
            },
            {
                path: "users",   //   /system/users
                component: import("../views/users.vue")
            },
            {
                path: "depts",   //   /system/depts
                component: import("../views/departments.vue")
            }
        ]
    }
];

const router= createRouter({
	routes: routes,
	history: createWebHistory
})

export default router; // 只要引用这个文件，就能获取router
```



#### 3. 页面跳转 router.push

以login页面跳转到system页面为例：

```vue
<script setup lang="ts">
import router from "../router"
    
const loginForm = {
    account:''
    password:''
}
cosnt doSubmit = function(){
    if(loginForm.accout == '' || loginForm.password==''){
        console.log("账号和密码不能为空")
    }
    else{
        // 通过axios把loginForm以Json格式发送给服务器
        // 如果登录成功，切换页面
        router.push("/system");
    }
}
    
</script>
```



### 3.6 父子组件

**解决什么问题?**

以贴吧回复框为例：

一条回复信息包含，回复人、回复内容、点赞数量、回复时间等信息；同时，一个帖子会有多条回复信息；很明显，不能通过一个页面实现这个需求，因为事前 前端 并不知道有多少条回复，通过一个页面实现，只能写死回复数量；

父子组件可以实现这个需求；

#### 1. 父组件调用子组件（父组件给子组件传值）

父组件拥有数据，此时需要把父组件持有的数据传递给子组件，让页面能够显示带有数据的多个子组件；实现步骤如下：

1. 子组件打包所需要的数据（比如`interface CardInfo` --指明子组件所需要的数据有哪些）
2. 子组件需要设置InputInfo，用于接收父组件传进来的值
3. 子组件使用`defineProps`暴露接口（`const props = defineProps<InputInfo>();`接受来自父的传值）
4. 父组件使用`<Card ...  :cardinfo=""  :index="">`向子组件传值
5. 子组件通过`props`调用父组件传入的值

##### 子组件

```vue
<script setup lang="ts">
    import { defineProps, defineEmits } from 'vue';
    import { ref } from 'vue';

    interface CardInfo{
        author:String,
        time:String,
        content:String,
        likes:Number
    }

    interface InputInfo{
        cardinfo: CardInfo,
        index: Number
    }
    const props = defineProps<InputInfo>(); // ！！！使用defineProps定义暴露出的接口
    let like_num:any = ref(props.cardinfo.likes);
    
    const addLike = function (){ // 点赞+1
        like_num.value++;
    }
}
</script>

<template>
    <div class="card">
        <div>{{ props.cardinfo.author }}({{ props.cardinfo.time }})</div>
        <div>{{ props.cardinfo.content }}</div>
        <div>赞数:{{ like_num }}
            <button @click="addLike">赞</button>
        </div>
    </div>
</template>

<style lang="css" scoped>
    .card{
        width: 500px;
        height: 80px;
        border: 1px solid #000;
        border-radius: 2px;
    }
</style>
```

##### 父组件

```vue
<script setup lang="ts">
    import Card from '../components/card.vue'; // 引入子组件的文件
    import { ref, onMounted } from 'vue';
    //通过axios请求了一些数据
    let datas = [
        {
            author: "赵四",
            time: "2026-10-22 14:03:42",
            content: "这次考试太难了",
            likes: 30
        },
        {
            author: "赵四",
            time: "2026-10-22 14:04:42",
            content: "但是我考通过了",
            likes: 10
        },
        {
            author: "刘能",
            time: "2026-10-22 14:05:11",
            content: "老四你太招人烦了",
            likes: 1000
        }
    ];
    }	
    let total = ref(0);

    onMounted(function (){ // 计算总点赞数量
        //for-each
        for(let o of datas){
            total.value += o.likes;
        }
    });
</script>

<template>
    <Card v-for="(k, i) in datas" :cardinfo="k"></Card>
    <div>总点赞数:{{ total }}</div>
</template>
```



#### 3. 子组件调用父组件

案例：用户点击卡片中的“点赞”按钮，父组件中的“总点赞数”需要同步变化

步骤

0. 把props中的likes提成let（const中的likes无法被修改）

1. 注册了一个like的虚拟事件，like事件会携带点赞数和index(哪个Card)作为参数

2. 在子组件中触发like虚拟事件

3. 父组件中

   ```css
   /*@like 会接受 子组件emit的like事件，like事件携带了点赞数、index*/
   /*subAddLike是负责处理like的方法*/
   <Card v-for="(k, i) in datas" :index="i" :cardinfo="k" @like="subAddLike"></Card>
   ```

4. 父组件中

   ```typescript
   const subAddLike = function (new_likenum:number, index:any){
       datas[index].likes = new_likenum;
       total.value = 0;
       for(let o of datas){
           total.value += o.likes;
       }
   }
   ```

   



##### 子组件

```vue
<script setup lang="ts">
    import { defineProps, defineEmits } from 'vue';
    import { ref } from 'vue';
    interface CardInfo{
        author:String,
        time:String,
        content:String,
        likes:Number
    }
    interface InputInfo{
        cardinfo: CardInfo,
        index: Number
    }
    const props = defineProps<InputInfo>();
    let like_num:any = ref(props.cardinfo.likes);// 把const的props中的数据提成一个let

    const emit = defineEmits(['like']);  //1. 注册了like的虚拟事件

    const addLike = function (){
        like_num.value++;
        emit('like', like_num.value, props.index); //2. 触发like虚拟事件，将like_num作为回写的数据
    }
</script>

<template>
    <div class="card">
        <div>{{ props.cardinfo.author }}({{ props.cardinfo.time }})</div>
        <div>{{ props.cardinfo.content }}</div>
        <div>赞数:{{ like_num }}
            <button @click="addLike">赞</button>
        </div>
    </div>
</template>

<style lang="css" scoped>
    .card{
        width: 500px;
        height: 80px;
        border: 1px solid #000;
        border-radius: 2px;}
</style>
```



##### 父组件

```vue
<script setup lang="ts">
    import Card from '../components/card.vue';
    import { ref, onMounted } from 'vue';
    //通过axios请求了一些数据
    let datas = [
        {
            author: "赵四",
            time: "2026-10-22 14:03:42",
            content: "这次考试太难了",
            likes: 30
        },
        {
            author: "赵四",
            time: "2026-10-22 14:04:42",
            content: "但是我考通过了",
            likes: 10
        },
        {
            author: "刘能",
            time: "2026-10-22 14:05:11",
            content: "老四你太招人烦了",
            likes: 1000
        }
    ];

    let total = ref(0);

    onMounted(function (){
        for(let o of datas){
            total.value += o.likes;
        }
    });

    //4. function的参数要与子组件emit提供的参数对应
    const subAddLike = function (new_likenum:number, index:any){
        datas[index].likes = new_likenum;
        total.value = 0;
        for(let o of datas){
            total.value += o.likes;
        }
    }
</script>

<template>
    <!-- 3. 父组件为虚拟事件绑定操作函数 -->
    <Card v-for="(k, i) in datas" :index="i" :cardinfo="k" @like="subAddLike"></Card>
    <div>总点赞数:{{ total }}</div>
</template>

```














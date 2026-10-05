linux内核的双向链表

要点：

list结构体仅保存向前，向后的指针

```c
struct list_head {
    struct list_head *next, *prev;
};
// ！ 注意 C语言不能直接给结构体成员赋初始值
```

list作为数据struct的一部分

```c
struct data
{
    int ele;
    struct list_head list;
}
```

通过offset和container_of宏，从list_head

```c
// (TYPE *)0， 将地址 0 转化为TYPE类型的指针
// ((TYPE *)0)->MEMBER 拿到 假指针的 MEMBER
// 再通过&取地址
// 最后通过(size_t)强转为size_t类型
#define offsetof(TYPE, MEMBER) ((size_t)&((TYPE *)0)->MEMBER)

// 注意：这里使用了({...})写法，这个写法是GCC的方言，标准C不支持
//      该写法可以将{}中的代码块中，最后一句话的值返回，就像一个函数一样
// 第一句 类型检查，检查ptr到底是不是list_head类型的
// 第二句 将ptr转换为char*，然后再-offset，获取结构体的首地址
#define container_of(ptr, type, member) ({\
    const typeof( ((type *)0)->member ) *__mptr = (ptr);\
    (type *)( (char *)__mptr - offsetof(type,member) );})
```

使用

```c
struct list_head* list_ptr;
struct data current_data = container_of(list_ptr, struct data, list);
// list_ptr 是 节点
// struct data 是 要取出的结构体类型
// list 是 struct data中 list_head 的名字
```








# Git的三种对象

Git有三种重要的对象，分别是 blob  tree  commit

## blob对象

新建一个文件test-1.txt，文件内容为

```txt
111111
```

使用

```shell
git add test-1.txt
```

此时查看.git文件夹，发现objects文件下多了一个 90/d295...的文件 

```shell
...
├─objects
│  ├─90
│  │      d2950097fa1850b6f692ab1095ec9cdd3f7fae # git add test-1.txt之前是没有这个东西的
│  │
│  ├─info
│  └─pack
└─refs
    ├─heads
    └─tags
```

文件90d2950097fa1850b6f692ab1095ec9cdd3f7fae是“test-1.txt”的快照，而这个文件名，是根据文件test-1.txt的内容生成的哈希码

```shell
# 通过-t查看文件90d2的类型，可以看到90d2的类型是blob对象
PS D:\test\.git> git cat-file -t 90d2
blob

# 通过-p查看文件90d2的内容，可以看到90d2的内容就是test-1.txt的内容
PS D:\test\.git> git cat-file -p 90d2
111111
```

通过内容也可以看出，所谓“blob”或者“快照”就是把当前这个文件的内容复制了一份副本。

（那么，如果有一个10M的文件且该文件已经有一个大小为10M的blob了，只改动了一行，git也会再生成一个新的、大小为10M的blob？

答案是：对的，git确实会这样干，所以git的各种使用教程也会告诉你不要用git追踪编译产生的文件，因为这些文件经常会变动且其历史文件几乎没有价值，如果追踪，就会产生大量无用blob文件）

## tree对象

使用commit进行一次提交

```shell
git commit -m "first commit"
```

此时，objects文件夹下会多出两个文件

```shell
├─objects
│  ├─32
│  │      95d788eddf768d4cc4b51d45777bbf2cb8b736
│  │
│  ├─90
│  │      d2950097fa1850b6f692ab1095ec9cdd3f7fae
│  │
│  ├─e1
│  │      0e504a04f62a7689181d00f5585be51b6756e8
│  │
│  ├─info
│  └─pack
└─refs
    ├─heads
    │      master
    │
    └─tags
```

使用git cat-file查看e10e的类型和内容

```shell
PS D:\test\.git> git cat-file -t e10e
tree # 类型为tree
# 查看内容
PS D:\test\.git> git cat-file -p e10e
100644 blob 90d2950097fa1850b6f692ab1095ec9cdd3f7fae    test-1.txt

```

可见，tree对象本质上是一个文件夹，这个hash code为e10e的tree对象，对应的就是根目录文件夹，它记录了根目录下有一个叫做test-1.txt的文件，这个txt文件对应的blob对象是90d2950097fa1850b6f692ab1095ec9cdd3f7fae

## commit对象

查看82d6的类型和类容

```shell
# 查看3295的类型
first commit
PS D:\test\.git> git cat-file -t 3295
commit
# 查看3295的内容
PS D:\test\.git> git cat-file -p 3295
tree e10e504a04f62a7689181d00f5585be51b6756e8
author lfg <1040734443@qq.com> 1785241814 +0800
committer lfg <1040734443@qq.com> 1785241814 +0800
```

可见，commit对象有一个指针指向了tree对象，并且记录了本次提交者的信息

此时，blob-tree-commit三者的关系为：

```shell
commit
    |
    |--> tree 
           |
           |--> blob
# commit保存了一个指向tree的指针
# tree保存了一系列指向其他tree与blob的指针
# blob指针保存了文件的快照
```

凭借这个引用关系，只要有某个版本的commit，就可以顺藤摸瓜

再创建一个文件夹“test-dir”然后在test-dir下创建文件“test-2.txt”，内容为222222，然后进行commit，操作流程如下所示：

```shell
PS D:\test> ls
    目录: D:\test
Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
-a----         2026/7/28     20:29              8 test-1.txt


PS D:\test> mkdir test-dir
    目录: D:\test
Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
d-----         2026/7/28     21:48                test-dir

PS D:\test> nvim .\test-dir\test-2.txt
PS D:\test> git add *
PS D:\test> git commit -m "2th commit"
[master ca80c9a] 2th commit
 1 file changed, 1 insertion(+)
 create mode 100644 test-dir/test-2.txt
PS D:\test>
```

此时再看objects文件夹下，第二个commit对象的内容：

```shell
PS D:\test\.git> git cat-file -p ca80
tree 978e0cdf253a267b9b2481a97a4e9d921e9a2645
parent 3295d788eddf768d4cc4b51d45777bbf2cb8b736 #与first commit不同的是，此次commit有parent
author lfg <1040734443@qq.com> 1785246513 +0800
committer lfg <1040734443@qq.com> 1785246513 +0800

2th commit
```

这就是一个更常见的commit的状态，此时只有2个commit的git的结构如下所示：

```shell
commit # first commit
 ^  |
 |  |--> tree #  e10e 根目录tree对象
 | 	       |
 |         |--> blob # 90d2 test-1.txt blob对象
commit # 2th commit
    |
    |--> tree # 978e 也是根目录tree对象
           |
           |--> blob # 90d2 test-1.txt blob对象
           |--> tree # 9f53 test-dir对应的tree对象
                  |
                  |--> blob # 9f53 test-2.txt blob对象
```

因此，给定任何一个commit对象，都可以通过其中的指针找到该版本的文件的快照，也能通过parent回溯找到之前的版本。

# Git的分支

## HEAD

.git下有一个HEAD文件

```shell
PS D:\test> cat .\.git\HEAD
ref: refs/heads/master
```

可见HEAD指向的是refs文件夹里的master

```shell
└─refs
    ├─heads
    │      master # 目前HEAD指向这个文件
    │
    └─tags
```

查看.git文件夹下的refs/heads文件夹下的master

```shell
PS D:\test\.git> cat .\refs\heads\master
ca80c9ab6fb24d3d68afae73c2facce16af8aa09 # 可见master此时记录的是一个hash code

# 通过git log可以看到，master中的hash code正是当前最后一个commit的hash code
PS D:\test\.git> git log
commit ca80c9ab6fb24d3d68afae73c2facce16af8aa09 (HEAD -> master)
Author: lfg <1040734443@qq.com>
Date:   Tue Jul 28 21:48:33 2026 +0800

    2th commit

commit 3295d788eddf768d4cc4b51d45777bbf2cb8b736
Author: lfg <1040734443@qq.com>
Date:   Tue Jul 28 20:30:14 2026 +0800

    first commit
```

如果建立一个dev分支，并且进行一次提交

```shell
PS D:\test> git switch -c  dev # 使用switch -c创建分支
Switched to a new branch 'dev'

PS D:\test> git status # 可以看到现在已经在dev分支下了
On branch dev 
nothing to commit, working tree clean

PS D:\test> nvim test-3.txt # 创建一个新文件
PS D:\test> git add * # add
PS D:\test> git commit -m "dev commit" # commit
[dev 5f82fd0] dev commit
 1 file changed, 1 insertion(+)
 create mode 100644 test-3.txt
```

再看refs文件夹

```shell
└─refs
    ├─heads
    │      dev # 多了一个dev
    │      master
    │
    └─tags
```

此时再看HEAD，发现其已经改变了

```shell
PS D:\test> git switch dev
Switched to branch 'dev'
PS D:\test> cat .\.git\HEAD
ref: refs/heads/dev # 毫无疑问，这个dev中的内容是dev commit的hash code
```



## Git的分支

git的分支如图所示：

当用户切换到dev分支时

```shell
                        
                        master
commit1 --> commit2 --> commit3					 HEAD
                               |				 dev
                               |--> commit5 --> commit6
```

当用户切换到master分支时

```shell
                        
                        HEAD
                        master
commit1 --> commit2 --> commit3
                              |                 dev
                              |--> commit5 --> commit6
```

分支的切换本质上是HEAD这个文件选择了refs下不同的分支



## 分支的合并

以下的例子中，都包含了master分支领先dev分支的情况。即我们创建dev分支之后，有人在master分支上进行和提交或合并，导致master分支中的有些改动在dev中并不存在。

### merge操作

对

```shell
                                    
                                    master
commit1 --> commit2 --> commit3 --> commit7 # 注意，commit7是一个master上的新commit  
                               |                 HEAD
                               |                 dev
                               |--> commit5 --> commit6
```

进行合并，将dev分支合并入master分支

```shell
git switch master # 切换到master分支
git merge dev # 执行合并
```

如果master没有和dev产生冲突，那么合并结果如图所示：

```shell
                                                              
                                                             HEAD
                                                             master
commit1 --> commit2 --> commit3 --> commit7	--------------->commit8				 
                               |						   ^
                               |                 dev       |
                               |--> commit5 --> commit6 ---|
```

可见，此次合并产生了一个新的commit，这个commit中既包含commit7的修改，也包含commit5和commit6的修改，且commit6和commit7都是commit8的parent

这也是merge的一个问题，他会在commit链条上产生一个分叉，也就是dev分叉，分叉少了还好，分叉多的话会严重影响到对master分支的查看

所以有时需要rebase

### rebase操作

同样对

```shell
                                    
                                    master
commit1 --> commit2 --> commit3 --> commit7      HEAD
                               |                 dev
                               |--> commit5 --> commit6
```

进行合并，本次使用rebase命令，在dev分支下执行：

```shell
git rebase master
```

如果没有冲突，dev的分支会变成：

```shell
                                                               
                                                               HEAD
                         master	                               dev
commit1 --> commit2 --> commit3 --> commit7 --> commit5' --> commit6'
```

进行rebase后，原本dev分叉上的commit5和commit6会变成继commit7之后的两个新提交，此时再合并，就不会出现dev分叉的情况了，master仍能保持一条直线；

一般dev分支向远程提交之前，用一次rebase，然后再在远程merge，这样master分支就能保持一条线，也就是：

1. 如果master分支上存在比dev更新的提交时，对dev使用rebase master
2. 如果要将dev合并到master，对master使用merge dev




























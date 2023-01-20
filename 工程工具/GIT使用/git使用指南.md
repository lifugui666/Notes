## 安装git

在linux上安装就很简单了...不会的话自己去百度一下

## 创建一个repository

在需要被git管理的路径下，使用命令

```bash
git init
```

即可创建一个本地仓库，这个路径下的内容就可以被git管理了

## 将文件添加到repository中

如果仅仅执行了git init操作，此时repository还是空的，如果不做add操作，执行一下git status命令，git会告诉你当前路径下有哪些文件是没有被追踪（trace）的；

```bash
lfg@PS2020MEJAZGGP:~/test$ git init
Initialized empty Git repository in /home/lfg/test/.git/
lfg@PS2020MEJAZGGP:~/test$ git status
On branch master

No commits yet

Untracked files:
  (use "git add <file>..." to include in what will be committed)

        test

nothing added to commit but untracked files present (use "git add" to track)
```

就像上面这样，git会明确的告诉你，test文件没有被追踪（untracked）

此时需要将路径下的文件添加到repository中；

```bash
git add 需要添加的内容
```

如果需要将路径下全部内容添加到repository中

```bash
git add ./*
```

如果只需要将某个文件添加到repository中，指定文件名即可；

## 使用git add将修改提交到暂存区（stage）

在创建了一个 空的repository 之后，第一次使用add，会把文件提交到stage中，同时，git也会对被提交的文件做追踪，如果之后再对这些文件做修改，然后使用git status命令，git就会告诉你，那些文件被做了修改，这些修改可以使用git add 添加到暂存区中；

## 使用git commit将修改写入分支

使用这个命令之后，stage中的内容会被清空，stage中原先的内容会被写入到分支里面；此时再使用git commit会发现没有任何提示，除非被追踪的文件又被修改了；



## ---------------------------------------



## 创建远程仓库

使用github或者gitee或者gitlab都可以，创建一个远程仓库；然后将该远程仓库和本地的仓库关联

```bash
git remote add origin xxxxxxxx(远程仓库的地址)
```

这里的origin是远程仓库的名字，可以换成其他的；



## 将本地库的内容推送到远程库

使用命令

```bash
git push -u origin master
```

添加了-u参数之后，以后就可以使用git push命令替代git push origin master命令；-u的本质是指定了一个默认主机，当本地分支拥有多个远程主机上的远程分支时，使用-u指定一个主机作为其默认主机，之后如果没有特殊说明将会默认使用这个主机；

git push的格式如下

git push <远程主机名> <本地分支名> <远程分支名>，如果省略了第三个参数，表示将本地分支推送到与本地分支存在关联的远程分支上；通常这两个分支是同名的；

```bash
git push origin master
#master是本地分支，origin是远程主机名
```

其实如果本地分支和远程分支 存在追踪关系，本地分支名也可以省略

```bash
git push origin
#指定远程主机名即可
```

如果当前本地分支只有一个远程分支，甚至连主机名都可以省略

```bash
git push
```

## 从远程仓库上克隆内容到本地

使用命令

```bash
git clone xxxx(地址，一般git服务器会告诉你地址是什么)
```

使用克隆命令，有两种协议可选：ssh和https，ssh速度比较快





## 分支的创建&切换

使用命令：

```
git branch //这个命令会列出本地存在的分支，并且当前的分支会有*标记
```

使用命令：

```bash
git branch 分支名 //创建分支
```

使用命令：

```bash
git checkout 分支名 //切换分支
```

可以在checkout命令中添加一个参数-b，同时完成创建&切换的工作

```bash
git checkout -b 分支名
```

## 分支的合并

如果想要合并分支A到分支B中，首先要进入分支B；然后指定合并分支A

```bash
git checkout 分支B
#如果已经在分支b中，这步骤可以省略
git merge 分支A
#代表将分支A和分支B合并
```

合并之后即使删除分支A也不会有什么影响；

## 新的分支操作关键字：switch

由于checkout命令同时具有撤销修改和改动分支的功能...因此现在git推出了一个新的命令：switch进行分支的操作；从字面意义上讲switch作为分支切换命令明显要合理许多了；

```bash
git switch 分支名
#切换分支
git switch -c 分支名
#创建并且切换分支
```

## 合并的4中方式：

### 快速合并，fast-forward

要理解git的合并方式，需要首先理解git的存储逻辑；git的存储时基于commit的，每一次commit就会产生一个新的节点，所谓分支并不总是真的形成了树状结构（当然树状结构也是存在的）；假设在创建了分支，并且之后的所有改动都是基于分支的时候，git的存储逻辑如下：

![img](https://cdn.nlark.com/yuque/0/2020/jpeg/594209/1607309913044-f77c4a8b-8755-4e58-8cbb-d953b27aa61e.jpeg)

如图所示，确实存在两个分支，但是commit链还是一个链表，此时如果合并，会发生快速合并；

1. 将head指向master
2. 将master指向commit3

此时，branch1和master都指向了commit3，虽然说是合并，但是其实只是移动了一下指针位置，此时删除branch1分支，也只是删除了一个指针而已 ；

使用命令

```bash
git merge 目标分支
```

即可；

### 非快速合并，--no-ff

非快速合并会做一个新的commit，并移动指针

![img](https://cdn.nlark.com/yuque/0/2020/jpeg/594209/1607311083129-1cf5cba7-b4e4-487e-af39-e78fbad25a6d.jpeg)

这样进行提交 ，会保留分支中的commit历史，同时，在merge的时候进行了commit（做了一次提交），因此该合并时可以在历史中查看到的；同时，使用非快速合并，还可以看到被合并的分支的commit历史；

使用命令：

```bash
git merge --no-ff 分支名
```

### squash合并

squash合并和no-ff合并很相似，squash单词含义为：压缩；

squash合并同样会进行一次 提交，因此在master分支，仍旧时能够看到合并历史的；但是由于squash并没有链接之前的分支，因此，master分支也只是知道进行了一次合并，但是看不到分支提交的历史；

![img](https://cdn.nlark.com/yuque/0/2020/jpeg/594209/1607311526328-810a762f-b071-4976-9d29-137273600062.jpeg)

使用命令

```bash
git merge --squash 分支名
```

### rebase

如果使用merge合并命令，产生冲突是很常见的，如果在你使用分支进行开发的时间里，主分支发生了改动，那么此时你再去合并，很大概率会出现冲突，这时候你需要把新的master拉到本地，然后再进行提交（merge），这时候，对于主分支来说，commit历史会变成这样：

![img](https://cdn.nlark.com/yuque/0/2020/jpeg/594209/1607313861316-114cd2a8-2e15-4e6e-87e2-5c2397d551e6.jpeg)

产生了一个分叉...其实不影响功能，但是看起来不好看，这时候可以使用git rebase进行提交；让git log变成一条直线；

## ---------------------------------------



patch既补丁；



例如

某次git的提交内容如下

```c
//伪代码
例如有一个文档叫做a.txt
原本其中的内容为
hello world

修改这个文档内容为
fuck world

提交这个改动，那么会在git log中留下如下记录：

对文件a.txt进行了修改
- hello world
+ fuck world
```

我们就可以吧这条git log打成补丁，如果使用文档编辑器打开这个补丁，会看到这个补丁的内容其实和git log中显示的一样



此时如果在某个a.txt仍旧为hello world的分支中使用这个补丁，那么a.txt中的内容将被修改为fuck world



## patch的生成

假设：当前git log中包含如下记录

```git
commit 3333
		第三次改动
commit 2222
		第二次改动
commit 1111
		第一次改动
```

如果我想要生成这三个改动的补丁

git format-patch 1111

如此，会把第一次改动之后的改动都生成为补丁



当然，有些时候我们只想单独生成某次commit的patch，此时可以使用如下命令

git format-patch -1 2222

这样就会生成commit 2222的补丁



## 应用patch

假设：commit 2222生成的补丁文件名称为 2222.patch

要应用2222.patch，流程如下

```git
第一步：检查patch文件
git apply --stat 2222.patch

第二部：检查该patch文件是否能被成功应用
git appli --check 2222.patch

第三步：应用该patch文件
git am -s < 222.patch
注：应用patch文件还有另一个命令，后文介绍
```

## 

## 如果冲突了怎么办？

使用git不得不时时刻刻处理令人难过的冲突问题...打patch同样有可能遇到冲突

如果真的冲突了，有两种解决方案

### 1. 修改patch文件

**冲突的本质是：当前分支和想要被应用的改动，对同一行进行了改动，也就是说，对某一行而言，git改动中记录的原始内容和当前实际环境中的内容不一样了**

所以只要修改patch中的记录，将起冲突的改动的patch记录中记录的旧版本改成当前环境里的样子就可以了



### 2. 修改本地文件

这种方式其实和第一种方式在原理上一样，因为 **冲突的本质是：当前分支和想要被应用的改动，对同一行进行了改动，也就是说，对某一行而言，git改动中记录的原始内容和当前实际环境中的内容不一样了** 

这样在应用改动（例如pull 或者 patch）的时候，git会告知你，并且需要你去决断要不要保留你自己的改动；



## 解决冲突的另一种方式

当然是有的....

patch -p1 < **2222.patch**





## 一些奇奇怪怪的问题

###  server certificate verification failed. CAfile: none CRLfile: none

解决方案：

```
git config --global http.sslverify false
git config --global https.sslverify false
```


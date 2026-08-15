# Git常见工作场景与对应指令

## 1 初始化仓库

```shell
git init
```

## 2 从远端克隆

```shell
git clone <远程仓库地址>
```

一旦完成这个操作之后，git会自动将远程仓库的地址取一个别名---**origin**

## 3 创建分支

```shell
git switch -c <feature>
```

## 4 下载远端的新对象

 ```shell
 git fetch origin
 
 # 如果远程存在更新的提交
 # fetch之前
                                                    master
 远程master分支 commit2 --> commit3 --> commit4 --> commit5
 
                                    origin/master
                                       master
 本地master分支 commit2 --> commit3 --> commit4
 
 # fetch之后
                                                   master
 远程master分支 commit2 --> commit3 --> commit4 --> commit5
 
                                       master   origin/master
 本地master分支 commit2 --> commit3 --> commit4 --> commit5
 ```

fetch会从远程下载更新的提交，更新远程追踪，但是并**不会改变本地master指针**，也不会改变工作区文件。

<div style="page-break-after: always;"></div>

## 5 使用rebase将feature合入master

```shell
git switch feature
git rebase master # 使用rebase，消除分支，更新本地master指针
```

## 6 推送到远程

```shell
# git的标准推送语法
git push <远程仓库> <本地分支>:<远程分支>

# 一般而言，第一次推送
git push -u origin feature 
## -u建立本地feature和origin/feature之间的联系
## 如果远程没有feature，这条指令会在远程创建feature
## -u建立的联系只有在分支feature下生效

# 之后的推送feature只需要
git push
## 如果切换到了其他的分支，比如feature1分支，而没有执行过-u，则还是会报错

```

## 7 需要用到stash的场景

如果某个feature开发到一半，需要切换到其他分支修复bug或是进行其他操作，可以使用stash

```shell
git stash save "开发进度描述"
git switch <其他分支>
# ... 完成改动 ...
git switch <原本在开发的分支>
git stash pop # 弹出之前的stash的内容
```

stash相关操作

```shell
git stash                    # 直接入栈
git stash save <desp>        # 入栈 可以加注释

git stash pop                # 出栈
git stash apply              # 不出栈 但还原文件改动

git stash drop <stash id>    # 从栈里删除
git stash clear              # 清空整个栈

git stash list               # 列出栈
git stash show <stash id>    # 展示某个改动
```

<div style="page-break-after: always;"></div>

## 8 放弃某个改动的场景

这里分多种情况：

```shell
#########################  没有add过  ##########################
git restore <文件名>  # 放弃工作区改动

########################  进行了add 但是没commit ###############
# 只是进行过add，且add后没有再改动文件
git restore --staged <文件名> # 改动回退到工作区，如果想要彻底放弃改动，再执行一次restroe

# 进行过add 之后又对该文件进行了改动
## 撤销add的部分（改动回退到工作区里）
git restore --staged <文件名>
## 撤销没有add的部分
git restore <文件名>

########################  进行了commit   ########################
## 1. soft
git reset --soft <commit编号> # 移动HEAD指针，暂存区和工作区都不变（add过的和没add过的都保持原状）
## 2. mix （这也是git reset的默认行为）
git reset --mix <commit编号>  # 移动HEAD指针，清空暂存区，工作区不变
## 3. hard
git reset --hard <commit编号> # 硬回滚，工作区和暂存区都清空，目标commit编号后的操作会全部丢失
```


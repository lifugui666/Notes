# 1. Node

1. 安装node

2. 在node的根目录下建立两个文件夹`node_global` `node_cache`

3. 执行命令

   ```shell
   npm config set prefix "C:\Program Files\nodejs\node_global"
   npm config set cache "C:\Program Files\nodejs\node_cache"
   ```

4. 配置环境变量

   ```shell
   # 加入
   C:\Program Files\nodejs\node_global  # 这个是自己建的文件夹
   C:\Program Files\nodejs # nodejs
   ```

5. 在powershell里输入`Set-ExecutionPolicy RemoteSigned -Scope CurrentUser`(否则powershell不能用npm)

   ```shell
   Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```

   

# 2. 搭建&启动VUE3

## 2.1 构建一个VUE项目

执行

```shell
npm create vite@latest
```

根据提示完成即可

```shell
PS D:\03-java\proj_10_19> npm create vite@latest
Need to install the following packages:
create-vite@9.2.1
Ok to proceed? (y) y
> npx
> create-vite
│
◇  Project name:
│  proj_1019
│
◇  Select a framework:
│  Vue
│
◇  Select a variant:
│  TypeScript
│
◇  Install with npm and start now?
│  Yes
│
◇  Scaffolding project in D:\neu\03-java\proj_10_19\proj_1019...
│
◇  Installing dependencies with npm...

added 48 packages, and audited 49 packages in 2m

9 packages are looking for funding
  run `npm fund` for details

found 0 vulnerabilities
│
◇  Starting dev server...

> proj_1019@0.0.0 dev
> vite


  VITE v8.3.4  ready in 358 ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
  ➜  press h + enter to show help
```

完成之后，vue会自动开始运行，此时就可以通过浏览器浏览这个页面

关闭之后，再次需要启动时：

1. 进入项目目录

2. 执行

   ```shell
   npm run dev
   ```




## 2.2 可能会遇到的问题

Q: 无法将vite识别为cmdlet

```shell
# 确认环境没问题
node -v
npm -v
npx vite --version # 这里可能会让你下载一些东西，下载即可

# 检查是否安装了vite
npm list -g vite
# 如果没有安装则执行
npm install -g vite

# 执行npm run dev时候出现ERR_MODULE_NOT_FOUND
npm i # 再次安装node_modules
```



## 2.3 VUE的项目目录结构

```shell

```










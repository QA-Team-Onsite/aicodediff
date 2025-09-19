# 项目部署与代码管理说明

### 1. 本地环境提交代码
- 不要把虚拟环境文件提交到 Git 仓库，虚拟环境最好建立在项目外侧。
- 提交代码命令：
  ```bash
  git add . && git commit -m "commit message" && git push origin master
  ```

### 2. 部署之前拉一下代码
- 拉取最新代码：
  ```bash
  git pull origin master
  ```

- 终极方法：删除aicodediff项目并重新克隆：
  ```bash
  git clone http://gitlab.jrdaimao.com/qa/aicodediff.git
  ```

### 3. 如果引入了新包
- 如果引入新的包，需要重新生成 `requirements.txt`：
  ```bash
  pip freeze > requirements.txt
  ```

### 4. Python 虚拟环境目录
- 虚拟环境目录路径：
  ```bash
  /home/codediff-ai/pycodediff_venv
  ```

### 5. 激活虚拟环境
- 激活虚拟环境命令：
  ```bash
  source /home/codediff-ai/pycodediff_venv/bin/activate
  ```

### 6. 安装新包
- 如果有新的包引入，先安装所需的包：
  ```bash
  pip install -r requirements.txt
  ```
- 如果没有新包引入，则跳过此步骤。

### 7. 项目根目录
- 项目根目录路径：
  ```bash
  /home/codediff-ai/aicodediff/py-codediff
  ```

### 8. 项目部署命令
- 在项目根目录 `/home/codediff-ai/aicodediff/py-codediff` 执行以下命令进行部署：
  ```bash
  nohup bash -c "cd /home/codediff-ai/aicodediff/py-codediff && uvicorn controller.api:app --reload --host 0.0.0.0 --port 8025" > /home/codediff-ai/log/py_uvicorn.log 2>&1 &
  ```
```

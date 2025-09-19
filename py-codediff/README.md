# ��Ŀ������������˵��

### 1. ���ػ����ύ����
- ��Ҫ�����⻷���ļ��ύ�� Git �ֿ⣬���⻷����ý�������Ŀ��ࡣ
- �ύ�������
  ```bash
  git add . && git commit -m "commit message" && git push origin master
  ```

### 2. ����֮ǰ��һ�´���
- ��ȡ���´��룺
  ```bash
  git pull origin master
  ```

- �ռ�������ɾ��aicodediff��Ŀ�����¿�¡��
  ```bash
  git clone http://gitlab.jrdaimao.com/qa/aicodediff.git
  ```

### 3. ����������°�
- ��������µİ�����Ҫ�������� `requirements.txt`��
  ```bash
  pip freeze > requirements.txt
  ```

### 4. Python ���⻷��Ŀ¼
- ���⻷��Ŀ¼·����
  ```bash
  /home/codediff-ai/pycodediff_venv
  ```

### 5. �������⻷��
- �������⻷�����
  ```bash
  source /home/codediff-ai/pycodediff_venv/bin/activate
  ```

### 6. ��װ�°�
- ������µİ����룬�Ȱ�װ����İ���
  ```bash
  pip install -r requirements.txt
  ```
- ���û���°����룬�������˲��衣

### 7. ��Ŀ��Ŀ¼
- ��Ŀ��Ŀ¼·����
  ```bash
  /home/codediff-ai/aicodediff/py-codediff
  ```

### 8. ��Ŀ��������
- ����Ŀ��Ŀ¼ `/home/codediff-ai/aicodediff/py-codediff` ִ������������в���
  ```bash
  nohup bash -c "cd /home/codediff-ai/aicodediff/py-codediff && uvicorn controller.api:app --reload --host 0.0.0.0 --port 8025" > /home/codediff-ai/log/py_uvicorn.log 2>&1 &
  ```
```

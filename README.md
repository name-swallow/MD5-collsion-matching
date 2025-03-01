# MD5-collsion-matching
MD5 Cracker - Modern GUI application for hash decryption using dictionary attacks, featuring intelligent password management and multi-threaded acceleration for rapid hash matching.

# 🔑 MD5碰撞爆破小工具

这是一个带图形界面的**MD5密码破解/生成工具**，特别适合刚学Python的小伙伴研究使用！所有功能都做成按钮了，点点鼠标就能玩～


## 🌟 功能一览

### 1️⃣ 主界面长这样
![image](https://github.com/user-attachments/assets/872108d5-95a1-421f-b38c-0c7a09dfe912)
![image](https://github.com/user-attachments/assets/40b5a4bf-35bb-40af-a6ad-6ae59e3b25e5)


### 2️⃣ 核心功能
**🔍 MD5破解器**  
👉 怎么用：  
1. 把MD5值粘贴进去

2. 
2.选择你想使用的密码字典
3. ![image](https://github.com/user-attachments/assets/71d34aa3-32bb-4bff-aad4-80e7833f9f85)
4. 点"开始破解"坐等结果！
5. ![image](https://github.com/user-attachments/assets/f00f72be-3ced-44d2-9bbb-6575ab659609)

**✨ 小亮点：**  
- 进度条会动！还能显示剩余时间⏳
- 超大文件也不怕（自动分块读取）
  
### 3️⃣ 字典管家
 <!-- 字典管理界面截图 -->
- **添加字典**：选择txt文件进来就行
- **编辑字典**：在字典
- **永久保存**：字典退出后也不会丢记录。

### 4️⃣ 侧边小工具
- **🔨 MD5生成器**：输入文字秒变MD5
- **🔎 正则搜索**：用高级语法找密码（比如 `^abc\d{3}`）,找寻你想出现的md5值是怎样的。
- 
- **📊 实时进度**：显示正在尝试的密码片段

---

## 🚀 快速上车指南

### 第一步：装环境
```bash
pip install PyQt5  # 只要装这个就够了！
```

### 第二步：运行程序
```bash
python main.py  # 双击这个文件也可以哦
```

### 第三步：快乐玩耍
按界面按钮操作就行。

---

## 🧩 文件说明
三个文件各司其职：
1. `main.py` - 程序入口（只管运行这个！）
2. `Function_pro.py` - 破解核心逻辑
3. `Style.py` - 图形界面GUI

---

## ❓ 为什么做这个项目？
- 实现md5快速匹配，破解密码
-开发GUI，更好便于新手操作 

---

## 🚧 待完善功能
- [ ] 增加多个hash种类破解
- [ ] 优化多线程加速

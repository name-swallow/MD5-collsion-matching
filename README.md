### MD5-collsion-matching
MD5 Cracker - A modern GUI application for hash decryption using dictionary attacks. It features intelligent password management and multi-threaded acceleration to achieve rapid hash matching.

### 🌟 Features Overview

#### 1️⃣ Main Interface
The main interface looks like this:
![image](https://github.com/user-attachments/assets/872108d5-95a1-421f-b38c-0c7a09dfe912)
![image](https://github.com/user-attachments/assets/40b5a4bf-35bb-40af-a6ad-6ae59e3b25e5)

#### 2️⃣ Core Function
**🔍 MD5 Cracker**
👉 How to use:
1. Paste the MD5 value into the input field.
2. Select the password dictionary you want to use.
3. ![image](https://github.com/user-attachments/assets/71d34aa3-32bb-4bff-aad4-80e7833f9f85)
4. Click the "Start Cracking" button and wait for the result!
5. ![image](https://github.com/user-attachments/assets/f00f72be-3ced-44d2-9bbb-6575ab659609)

**✨ Highlights**:
- The progress bar is animated! It can also display the estimated remaining time ⏳.
- It can handle large files without any issues (automatically reads files in chunks).

#### 3️⃣ Dictionary Manager
<!-- Screenshot of the dictionary management interface -->
- **Add Dictionary**: Just select a text file.
- **Edit Dictionary**: You can edit the dictionary content.
- **Permanent Storage**: The dictionary records will be saved even after you exit the program.

#### 4️⃣ Side Tools
- **🔨 MD5 Generator**: Input text and instantly get its MD5 hash.
- **🔎 Regular Expression Search**: Use advanced syntax (e.g., `^abc\d{3}`) to search for passwords and find out what the corresponding MD5 values look like.
- **📊 Real-time Progress**: Displays the password fragment that is currently being attempted.

### 🚀 Quick Start Guide

#### Step 1: Install the Environment
```bash
pip install PyQt5  # This is the only package you need to install!
```

#### Step 2: Run the Program
```bash
python main.py  # You can also double-click this file.
```

#### Step 3: Have Fun
Just operate according to the buttons on the interface.

### 🧩 File Explanation
Each of the three files has its own responsibility:
1. `main.py` - The entry point of the program (just run this one!).
2. `Function_pro.py` - The core logic for cracking.
3. `Style.py` - The graphical user interface (GUI).

### ❓ Why Create This Project?
- To achieve fast MD5 matching and crack passwords.
- To develop a GUI for easier operation by beginners.

### 🚧 Features to be Improved
- [ ] Add support for cracking multiple hash types.
- [ ] Optimize multi-threaded acceleration.

import os
import weakref
import html
from PyQt5.QtCore import QThread, pyqtSignal, QTimer, QMutex, Qt, QElapsedTimer
from PyQt5.QtWidgets import QMessageBox, QApplication
from PyQt5.QtCore import QMutexLocker
import hashlib
from concurrent.futures import ThreadPoolExecutor, as_completed
import re
import logging
from datetime import timedelta

# 日志配置
logging.basicConfig(
    filename='error.log',
    level=logging.ERROR,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def check_log_size():
    """检查日志文件大小，超过1MB则删除并重建"""
    log_file = 'error.log'
    try:
        if os.path.exists(log_file) and os.path.getsize(log_file) > 1 * 1024 * 1024:  # 1MB
            os.remove(log_file)
            logging.info("Log file exceeded 1MB and was deleted.")
    except Exception as e:
        logging.error(f"检查日志大小时出错: {str(e)}")

class StyleManager:
    def __init__(self, design_config):
        self.design_config = design_config

    def get_style_sheet(self):
        """Generate a detailed stylesheet for a modern GUI appearance."""
        colors = self.design_config["colors"]
        style = f"""
        /* General Widget Styling */
        QWidget {{
            background: {colors["background"]};
            color: {colors["text"]};
            font-family: 'Segoe UI';
            font-size: 14px;
        }}

        /* Main Title */
        #mainTitle {{
            font: bold 24px 'Roboto';
            color: {colors["primary"]};
            padding: 16px;
            qproperty-alignment: AlignCenter;
        }}

        /* Group Boxes */
        QGroupBox {{
            border: 1px solid {colors["surface"]};
            border-radius: 8px;
            margin-top: 16px;
            padding: 12px;
            background: {colors["background"]};
        }}
        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 12px;
            color: {colors["primary"]};
            background: {colors["background"]};
            padding: 2px 6px;
        }}

        /* Text Edits */
        QTextEdit {{
            background: {colors["surface"]};
            border: 1px solid {colors["surface"]};
            border-radius: 6px;
            padding: 10px;
            selection-background-color: {colors["primary"]};
            color: {colors["text"]};
        }}
        QTextEdit:focus {{
            border: 1px solid {colors["primary"]};
        }}
        QTextEdit::placeholder {{
            color: {colors["text"]}80;  /* 50% opacity */
        }}

        /* Buttons */
        QPushButton {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 {colors["surface"]},
                stop:1 {colors["background"]});
            border: none;
            border-radius: 6px;
            padding: 10px;
            min-width: 100px;
            color: {colors["text"]};
        }}
        QPushButton:hover {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 {colors["primary"]}40,
                stop:1 {colors["primary"]}60);
        }}
        QPushButton:pressed {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 {colors["primary"]}60,
                stop:1 {colors["primary"]}80);
        }}

        /* Icon Buttons */
        QPushButton[iconButton="true"] {{
            background: transparent;
            border: none;
            padding: 4px;
            min-width: 0px;
        }}
        QPushButton[iconButton="true"]:hover {{
            background: {colors["primary"]}20;
            border-radius: 4px;
        }}

        /* Combo Boxes */
        QComboBox {{
            background: {colors["surface"]};
            border: 1px solid {colors["surface"]};
            border-radius: 6px;
            padding: 8px;
            color: {colors["text"]};
        }}
        QComboBox:hover {{
            border: 1px solid {colors["primary"]}50;
        }}
        QComboBox::drop-down {{
            subcontrol-origin: padding;
            subcontrol-position: top right;
            width: 24px;
            border-left: 1px solid {colors["surface"]};
        }}
        QComboBox::down-arrow {{
            width: 10px;
            height: 10px;
            image: url(:/icons/down_arrow.png);  /* Optional: Add icon resource */
        }}
        QComboBox QAbstractItemView {{
            background: {colors["surface"]};
            border: 1px solid {colors["primary"]};
            selection-background-color: {colors["primary"]};
            color: {colors["text"]};
        }}

        /* Progress Bar */
        QProgressBar {{
            border: 1px solid {colors["surface"]};
            border-radius: 6px;
            background: {colors["background"]};
            text-align: center;
            color: {colors["text"]};
        }}
        QProgressBar::chunk {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 {colors["secondary"]},
                stop:1 {colors["primary"]});
            border-radius: 6px;
        }}

        /* Splitter */
        QSplitter::handle {{
            background: {colors["surface"]};
        }}
        QSplitter::handle:hover {{
            background: {colors["primary"]}50;
        }}

        /* Frame (Sidebar) */
        #sidebar {{
            background: {colors["background"]};
            border-left: 1px solid {colors["surface"]};
        }}

        /* Scroll Bars */
        QScrollBar:vertical {{
            background: {colors["surface"]};
            width: 10px;
            margin: 0;
        }}
        QScrollBar::handle:vertical {{
            background: {colors["primary"]};
            min-height: 20px;
            border-radius: 5px;
        }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0px;
        }}
        """
        return style

class OptimizedCrackThread(QThread):
    progress_updated = pyqtSignal(int, str)
    result_found = pyqtSignal(str)
    crack_completed = pyqtSignal()
    error_occurred = pyqtSignal(str)
    time_updated = pyqtSignal(str)

    def __init__(self, target_hash, wordlist):
        super().__init__()
        self.target_hash = target_hash.strip().lower()
        self.wordlist = wordlist
        self.total_words = len(wordlist)
        self.mutex = QMutex()
        self._is_active = True
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.found = False
        self.start_time = QElapsedTimer()
        self.processed_words = 0

    def run(self):
        try:
            check_log_size()
            self.start_time.start()
            if not self._validate_hash():
                self.error_occurred.emit("无效的MD5哈希值")
                return

            futures = []
            batch_size = min(1000, max(1, self.total_words // 100))
            for i in range(0, self.total_words, batch_size):
                if not self._safe_check() or self.found:
                    break
                batch = self.wordlist[i:i + batch_size]
                future = self.executor.submit(self._process_batch, batch, i)
                futures.append(future)

            total_processed = 0
            for future in as_completed(futures):
                if self.found or not self._safe_check():
                    break
                result, count = future.result()
                total_processed += count
                self.processed_words = total_processed
                self._update_progress(total_processed)
                if result:
                    self.result_found.emit(result)
                    self._safe_stop()
                    return

            if self._safe_check():
                self.crack_completed.emit()

        except Exception as e:
            logging.error(f"运行时错误: {str(e)}")
            self.error_occurred.emit(f"运行时错误: {str(e)}")
        finally:
            self._safe_cleanup()

    def _process_batch(self, batch, start_index):
        count = 0
        for idx, word in enumerate(batch):
            if not self._safe_check() or self.found:
                break
            try:
                word = word.strip()
                current_hash = hashlib.md5(word.encode('utf-8', 'ignore')).hexdigest()
                if current_hash == self.target_hash:
                    return word, len(batch) - idx
            except Exception as e:
                logging.error(f"批处理错误: {str(e)}")
            finally:
                count += 1
        return None, count

    def _validate_hash(self):
        return re.match(r'^[a-f0-9]{32}$', self.target_hash) is not None

    def _safe_check(self):
        with QMutexLocker(self.mutex):
            return self._is_active

    def _update_progress(self, processed):
        progress = min(100, int(processed / self.total_words * 100))
        current_word = self.wordlist[min(processed, self.total_words - 1)][:20]
        self.progress_updated.emit(progress, current_word)
        self._update_time_estimate()

    def _update_time_estimate(self):
        elapsed = self.start_time.elapsed() / 1000
        if elapsed > 0 and self.processed_words > 0:
            words_per_sec = self.processed_words / elapsed
            remaining = (self.total_words - self.processed_words) / words_per_sec
            time_str = str(timedelta(seconds=int(remaining))).split('.')[0]
            self.time_updated.emit(f"预计剩余时间: {time_str}")

    def _safe_stop(self):
        with QMutexLocker(self.mutex):
            self._is_active = False
            self.found = True

    def _safe_cleanup(self):
        self.executor.shutdown(wait=False)
        if self.isRunning():
            self.wait(1000)

class RegexCrackThread(QThread):
    progress_updated = pyqtSignal(int, str)
    result_found = pyqtSignal(str)
    crack_completed = pyqtSignal()
    error_occurred = pyqtSignal(str)

    def __init__(self, pattern, wordlist):
        super().__init__()
        self.pattern = pattern
        self.wordlist = wordlist
        self.total_words = len(wordlist)
        self.mutex = QMutex()
        self._is_active = True
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.start_time = QElapsedTimer()

    def run(self):
        try:
            check_log_size()
            self.start_time.start()
            if not self._validate_pattern():
                self.error_occurred.emit("无效的正则表达式")
                return

            futures = []
            batch_size = min(1000, max(1, self.total_words // 100))
            for i in range(0, self.total_words, batch_size):
                if not self._safe_check():
                    break
                batch = self.wordlist[i:i + batch_size]
                future = self.executor.submit(self._process_batch, batch, i)
                futures.append(future)

            total_processed = 0
            matches = []
            for future in as_completed(futures):
                if not self._safe_check():
                    break
                batch_matches, count = future.result()
                total_processed += count
                matches.extend(batch_matches)
                self._update_progress(total_processed)
                for match in batch_matches:
                    self.result_found.emit(match)

            if self._safe_check():
                self.crack_completed.emit() if matches else self.error_occurred.emit("未找到匹配的密码")

        except Exception as e:
            logging.error(f"正则匹配运行时错误: {str(e)}")
            self.error_occurred.emit(f"运行时错误: {str(e)}")
        finally:
            self._safe_cleanup()

    def _process_batch(self, batch, start_index):
        count = 0
        matches = []
        try:
            regex = re.compile(self.pattern)
            for word in batch:
                if not self._safe_check():
                    break
                try:
                    word = word.strip()
                    md5_hash = hashlib.md5(word.encode('utf-8', 'ignore')).hexdigest()
                    if regex.match(md5_hash):
                        matches.append(word)
                except Exception as e:
                    logging.error(f"正则批处理错误: {str(e)}")
                finally:
                    count += 1
            return matches, count
        except re.error as e:
            logging.error(f"正则表达式编译错误: {str(e)}")
            return [], count

    def _validate_pattern(self):
        try:
            re.compile(self.pattern)
            return True
        except re.error as e:
            logging.error(f"正则表达式验证失败: {str(e)}")
            return False

    def _safe_check(self):
        with QMutexLocker(self.mutex):
            return self._is_active

    def _update_progress(self, processed):
        progress = min(100, int(processed / self.total_words * 100))
        current_word = self.wordlist[min(processed - 1, self.total_words - 1)][:20]
        self.progress_updated.emit(progress, current_word)

    def _safe_stop(self):
        with QMutexLocker(self.mutex):
            self._is_active = False

    def _safe_cleanup(self):
        self.executor.shutdown(wait=False)
        if self.isRunning():
            self.wait(1000)

class Function:
    def __init__(self, ui):
        self.ui = ui
        self.active_thread = None
        self.regex_thread = None
        self.last_progress = 0
        self.mutex = QMutex()

    def init_progress_bar(self):
        self.ui.progress_bar.setRange(0, 100)
        self.ui.progress_bar.setTextVisible(True)
        self.ui.progress_bar.setFormat("准备就绪")

    def start_cracking(self):
        try:
            check_log_size()
            if self.active_thread:
                self._cleanup_thread()
            if self.regex_thread:
                self._cleanup_regex_thread()

            target_hash = self.ui.hash_input.toPlainText().strip()
            if not self._validate_hash(target_hash):
                QMessageBox.warning(self.ui, "输入错误", "MD5哈希格式无效")
                return

            select_dict = self.ui.dict_combo.currentText()
            file_path = self.ui.current_files.get(select_dict)
            if not self._validate_wordlist(select_dict, file_path):
                return

            wordlist = self._load_wordlist(file_path)
            if not wordlist:
                return

            self.active_thread = OptimizedCrackThread(target_hash, wordlist)
            self._connect_thread_signals()
            self._reset_ui_state()
            self._start_watchdog()
            self.active_thread.start()

        except Exception as e:
            logging.error(f"启动爆破失败: {str(e)}")
            self._handle_critical_error("启动失败", str(e))

    def test_regex(self):
        try:
            check_log_size()
            if self.active_thread:
                self._cleanup_thread()
            if self.regex_thread:
                self._cleanup_regex_thread()

            pattern = self.ui.regex_input.toPlainText().strip()
            if not pattern:
                QMessageBox.warning(self.ui, "输入错误", "请输入正则表达式")
                return

            if not self._validate_regex_pattern(pattern):
                return

            select_dict = self.ui.dict_combo.currentText()
            file_path = self.ui.current_files.get(select_dict)
            if not self._validate_wordlist(select_dict, file_path):
                return

            wordlist = self._load_wordlist(file_path)
            if not wordlist:
                return

            self.regex_thread = RegexCrackThread(pattern, wordlist)
            self._connect_regex_thread_signals()
            self._reset_ui_state()
            self._start_watchdog()
            self.regex_thread.start()

        except Exception as e:
            logging.error(f"正则测试失败: {str(e)}")
            QMessageBox.critical(self.ui, "运行错误", f"正则测试失败: {str(e)}")

    def _validate_regex_pattern(self, pattern):
        try:
            re.compile(pattern)
            return True
        except re.error as e:
            self.ui.regex_output.setPlainText(f"正则表达式错误:\n位置: {e.pos}\n原因: {e.msg}")
            logging.error(f"正则表达式无效: {str(e)}")
            return False

    def _reset_ui_state(self):
        with QMutexLocker(self.mutex):
            self.last_progress = 0
            self.ui.progress_bar.reset()
            self.ui.result_display.clear()
            self.ui.regex_output.clear()
            self.ui.progress_bar.setFormat("启动中...")
            self.ui.start_btn.setEnabled(False)
            self.ui.stop_btn.setEnabled(True)

    def _validate_hash(self, hash_str):
        if not re.match(r'^[a-fA-F0-9]{32}$', hash_str):
            self.ui.hash_input.setStyleSheet("border: 2px solid #ff0000;")
            return False
        self.ui.hash_input.setStyleSheet("")
        return True

    def _validate_wordlist(self, select_dict, file_path):
        if not select_dict:
            QMessageBox.warning(self.ui, "选择错误", "请先选择字典文件")
            return False
        if not os.path.isfile(file_path):
            QMessageBox.critical(self.ui, "路径错误", f"文件不存在: {select_dict}")
            return False
        return True

    def _load_wordlist(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return [line.strip() for line in f if line.strip()]
        except Exception as e:
            logging.error(f"字典读取失败: {str(e)}")
            self._handle_error(f"字典读取失败: {str(e)}")
            return None

    def _connect_thread_signals(self):
        weak_self = weakref.ref(self)
        connections = [
            (self.active_thread.progress_updated, lambda p, w: weak_self()._update_progress_safe(p, w)),
            (self.active_thread.result_found, lambda r: weak_self()._handle_match_found(r)),
            (self.active_thread.crack_completed, lambda: weak_self()._handle_complete()),
            (self.active_thread.error_occurred, lambda m: weak_self()._handle_error(m)),
            (self.active_thread.time_updated, lambda t: weak_self()._update_time_remaining(t))
        ]
        for signal, slot in connections:
            signal.connect(slot, Qt.QueuedConnection)

    def _connect_regex_thread_signals(self):
        weak_self = weakref.ref(self)
        connections = [
            (self.regex_thread.progress_updated, lambda p, w: weak_self()._update_progress_safe(p, w)),
            (self.regex_thread.result_found, lambda r: weak_self()._handle_regex_match_found(r)),
            (self.regex_thread.crack_completed, lambda: weak_self()._handle_regex_complete()),
            (self.regex_thread.error_occurred, lambda m: weak_self()._handle_error(m))
        ]
        for signal, slot in connections:
            signal.connect(slot, Qt.QueuedConnection)

    def _update_progress_safe(self, progress, current_word):
        try:
            if not self.ui:
                return
            with QMutexLocker(self.mutex):
                progress = max(self.last_progress, min(progress, 100))
                if progress - self.last_progress < 1 and progress < 99:
                    return
                self.ui.progress_bar.setValue(progress)
                self.ui.progress_bar.setFormat(f"处理中: {current_word[:20]}" if progress < 100 else "最终校验")
                self.ui.progress_label.setText(f"{progress}%")
                self.last_progress = progress
        except RuntimeError as e:
            if "wrapped C/C++ object" not in str(e):
                logging.error(f"更新进度错误: {str(e)}")

    def _update_time_remaining(self, time_str):
        self.ui.time_remaining.setText(time_str)

    def _handle_match_found(self, result):
        self.ui.result_display.setHtml(f'<div style="color:#4CAF50; font-weight:600;">✅ 成功匹配: <code>{html.escape(result)}</code></div>')
        self._finalize_process("破解成功", 100)

    def _handle_complete(self):
        if not self.ui.result_display.toPlainText():
            self.ui.result_display.setHtml('<div style="color:#FF5722;">⚠️ 未找到匹配结果</div>')
        self._finalize_process("扫描完成", 100)

    def _handle_regex_match_found(self, result):
        current_text = self.ui.regex_output.toPlainText()
        self.ui.regex_output.setPlainText(current_text + '\n' + result if current_text else result)

    def _handle_regex_complete(self):
        if not self.ui.regex_output.toPlainText():
            self.ui.regex_output.setPlainText("未找到匹配的密码")
        self._finalize_process("正则匹配完成", 100)

    def _handle_error(self, message):
        logging.error(message)
        QMessageBox.critical(self.ui, "运行错误", message)
        self._finalize_process("错误终止", 0)

    def _finalize_process(self, status, progress):
        try:
            if self.ui:
                self.ui.progress_bar.setValue(progress)
                self.ui.progress_bar.setFormat(status)
                self.ui.start_btn.setEnabled(True)
                self.ui.stop_btn.setEnabled(False)
        finally:
            self._cleanup_thread()
            self._cleanup_regex_thread()

    def _cleanup_thread(self):
        if self.active_thread:
            try:
                signals = [
                    self.active_thread.progress_updated,
                    self.active_thread.result_found,
                    self.active_thread.crack_completed,
                    self.active_thread.error_occurred,
                    self.active_thread.time_updated
                ]
                for signal in signals:
                    try:
                        signal.disconnect()
                    except TypeError:
                        pass
                if self.active_thread.isRunning():
                    self.active_thread._safe_stop()
                    self.active_thread.wait(2000)
                    if self.active_thread.isRunning():
                        self.active_thread.terminate()
                self.active_thread.deleteLater()
            except RuntimeError as e:
                if "wrapped C/C++ object" not in str(e):
                    logging.error(f"清理线程错误: {str(e)}")
            finally:
                self.active_thread = None

    def _cleanup_regex_thread(self):
        if self.regex_thread:
            try:
                signals = [
                    self.regex_thread.progress_updated,
                    self.regex_thread.result_found,
                    self.regex_thread.crack_completed,
                    self.regex_thread.error_occurred
                ]
                for signal in signals:
                    try:
                        signal.disconnect()
                    except TypeError:
                        pass
                if self.regex_thread.isRunning():
                    self.regex_thread._safe_stop()
                    self.regex_thread.wait(2000)
                    if self.regex_thread.isRunning():
                        self.regex_thread.terminate()
                self.regex_thread.deleteLater()
            except RuntimeError as e:
                if "wrapped C/C++ object" not in str(e):
                    logging.error(f"清理正则线程错误: {str(e)}")
            finally:
                self.regex_thread = None

    def stop_crack(self):
        if self.active_thread or self.regex_thread:
            self.ui.progress_bar.setFormat("正在停止...")
            QApplication.processEvents()
            self._cleanup_thread()
            self._cleanup_regex_thread()
            self.ui.progress_bar.setValue(0)
            self.ui.progress_bar.setFormat("操作已中止")
            self.ui.result_display.setHtml('<div style="color:#FF5722;">⚠️ 已停止操作</div>')
            self.ui.regex_output.clear()
            self.ui.progress_label.setText("0%")
            self.ui.time_remaining.setText("预计剩余时间: --:--:--")
            self.ui.start_btn.setEnabled(True)
            self.ui.stop_btn.setEnabled(False)

    def _start_watchdog(self):
        self.watchdog = QTimer()
        self.watchdog.timeout.connect(self._check_thread_state)
        self.watchdog.start(3000)

    def _check_thread_state(self):
        if (self.active_thread and not self.active_thread.isRunning()) or \
           (self.regex_thread and not self.regex_thread.isRunning()):
            self._handle_error("线程意外终止")
            self._cleanup_thread()
            self._cleanup_regex_thread()

    def _handle_critical_error(self, title, message):
        logging.critical(f"{title}: {message}")
        QMessageBox.critical(self.ui, title, message)
        self._cleanup_thread()
        self._cleanup_regex_thread()
        if self.ui:
            self.ui.progress_bar.setValue(0)
            self.ui.progress_bar.setFormat("准备就绪")

    def generate_md5(self):
        try:
            check_log_size()
            input_str = self.ui.md5_input.toPlainText().strip()
            if not input_str:
                QMessageBox.warning(self.ui, "输入错误", "请输入要加密的内容")
                return
            try:
                encoded_str = input_str.encode('utf-8')
            except UnicodeEncodeError as e:
                logging.error(f"编码错误: {str(e)}")
                QMessageBox.critical(self.ui, "编码错误", f"不支持的字符: {str(e)}")
                return
            md5_hash = hashlib.md5(encoded_str).hexdigest()
            self.ui.md5_output.setPlainText(md5_hash)
        except Exception as e:
            logging.error(f"MD5生成失败: {str(e)}")
            QMessageBox.critical(self.ui, "生成错误", f"MD5生成失败: {str(e)}")

    def on_save_click(self):
        try:
            check_log_size()
            selected_name = self.ui.dict_combo.currentText()
            if not selected_name:
                QMessageBox.warning(self.ui, "未选择字典", "请先从下拉框选择一个字典文件")
                return
            file_path = self.ui.current_files.get(selected_name)
            if not file_path or not os.path.exists(file_path):
                QMessageBox.critical(self.ui, "路径错误", f"字典文件不存在或已被移动: {selected_name}")
                return
            password = self.ui.dict_editor.toPlainText().strip('\n')
            if not password:
                QMessageBox.warning(self.ui, "内容为空", "请输入要追加的密码内容")
                return
            with open(file_path, 'a+', encoding='utf-8') as f:
                f.seek(0)
                lines = f.readlines()
                if lines and not lines[-1].endswith('\n'):
                    f.write('\n')
                f.write(password + '\n')
            QMessageBox.information(self.ui, "追加成功", f"已追加内容到字典: {selected_name}", QMessageBox.Ok)
        except PermissionError:
            logging.error("权限不足，无法写入文件")
            QMessageBox.critical(self.ui, "权限不足", "无法写入文件，请检查文件权限")
        except Exception as e:
            logging.error(f"追加字典失败: {str(e)}")
            QMessageBox.critical(self.ui, "操作失败", f"追加字典时发生意外错误: {str(e)}")

    def validate_hash(self, hash_str):
        self.ui.hash_input.setToolTip("")
        if len(hash_str) != 32:
            self.ui.hash_input.setToolTip("MD5长度必须为32位")
            return False
        return re.match(r'^[a-fA-F0-9]{32}$', hash_str) is not None

    def clear_content(self):
        self.ui.result_display.clear()
        self.ui.regex_output.clear()
        self.ui.progress_bar.setValue(0)
        self.ui.progress_bar.setFormat("准备就绪")
        self.ui.time_remaining.setText("预计剩余时间: --:--:--")
        self.ui.progress_label.setText("0%")
        self.ui.md5_output.clear()
        self.ui.md5_input.clear()



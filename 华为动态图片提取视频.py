import os
import sys
import threading
from tkinter import *
from tkinter import filedialog, messagebox, ttk
from extract_moving_picture import extract  # 原始提取函数


class ExtractGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("华为动态图片提取器 - 版权所有 @赵一鸣")
        self.root.geometry("650x450")
        self.root.resizable(False, False)

        # 初始化变量
        self.input_path = StringVar()
        self.output_path = StringVar()
        self.current_file = StringVar(value="等待开始...")
        self.progress = 0

        # 创建界面
        self.create_widgets()

    def create_widgets(self):
        # 顶部输入区域
        input_frame = ttk.Frame(self.root, padding="10")
        input_frame.pack(fill=X)

        ttk.Label(input_frame, text="输入路径:").pack(side=LEFT)
        ttk.Entry(input_frame, textvariable=self.input_path, width=40).pack(side=LEFT, padx=5)
        ttk.Button(input_frame, text="浏览", command=self.select_input_folder).pack(side=LEFT)

        # 中部输出区域
        output_frame = ttk.Frame(self.root, padding="10")
        output_frame.pack(fill=X)

        ttk.Label(output_frame, text="输出路径:").pack(side=LEFT)
        ttk.Entry(output_frame, textvariable=self.output_path, width=40).pack(side=LEFT, padx=5)
        ttk.Button(output_frame, text="选择", command=self.select_output_folder).pack(side=LEFT)

        # 中间控制区域
        control_frame = ttk.Frame(self.root, padding="10")
        control_frame.pack(fill=X)

        self.start_btn = ttk.Button(control_frame, text="开始提取",
                                    command=self.start_extraction, width=15)
        self.start_btn.pack(side=LEFT, padx=5)

        ttk.Button(control_frame, text="打开输出文件夹",
                   command=self.open_output_folder, width=15).pack(side=LEFT)

        # 进度条区域
        progress_frame = ttk.Frame(self.root, padding="10")
        progress_frame.pack(fill=X)

        ttk.Label(progress_frame, text="当前处理:").pack(side=LEFT)
        ttk.Label(progress_frame, textvariable=self.current_file,
                  width=45, relief=SUNKEN).pack(side=LEFT, padx=5)

        # 进度条
        self.pb = ttk.Progressbar(progress_frame, orient=HORIZONTAL,
                                  length=200, mode='determinate')
        self.pb.pack(side=LEFT, padx=5)

        # 日志区域
        log_frame = ttk.Frame(self.root, padding="10")
        log_frame.pack(fill=BOTH, expand=True)

        self.log_text = Text(log_frame, height=12, wrap=WORD)
        self.log_text.pack(side=LEFT, fill=BOTH, expand=True)

        scrollbar = ttk.Scrollbar(log_frame, command=self.log_text.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.log_text.config(yscrollcommand=scrollbar.set)

    def select_input_folder(self):
        path = filedialog.askdirectory()
        if path:
            self.input_path.set(path)
            self.log(f"✅ 已选择输入路径: {path}")

    def select_output_folder(self):
        path = filedialog.askdirectory()
        if path:
            self.output_path.set(path)
            self.log(f"📁 已选择输出路径: {path}")

    def log(self, message):
        self.log_text.insert(END, message + "\n")
        self.log_text.see(END)

    def start_extraction(self):
        input_path = self.input_path.get()
        output_path = self.output_path.get()

        if not input_path or not os.path.exists(input_path):
            messagebox.showerror("❌ 错误", "请先选择有效的输入文件夹")
            return

        if not output_path:
            messagebox.showwarning("⚠️ 警告", "未选择输出路径，将使用输入路径作为输出路径")
            output_path = input_path
            self.output_path.set(output_path)

        # 自动创建输出目录
        if not os.path.exists(output_path):
            try:
                os.makedirs(output_path)
                self.log(f"🆕 自动创建输出目录: {output_path}")
            except Exception as e:
                messagebox.showerror("❌ 错误", f"无法创建输出目录: {str(e)}")
                return

        self.start_btn.config(state=DISABLED)
        self.pb['value'] = 0
        self.progress = 0
        self.current_file.set("初始化...")

        # 启动后台线程执行提取
        threading.Thread(target=self.run_extraction, args=(input_path, output_path),
                         daemon=True).start()

    def run_extraction(self, input_path, output_path):
        try:
            foldername = os.path.abspath(input_path)
            files = [f for f in os.listdir(foldername)
                     if os.path.isfile(os.path.join(foldername, f))]
            total_files = len(files)

            if total_files == 0:
                self.log("❗ 警告：目标文件夹为空")
                self.start_btn.config(state=NORMAL)
                return

            for i, file_ in enumerate(files):
                full_path = os.path.join(foldername, file_)
                self.current_file.set(f"处理文件: {file_}")

                # 修改提取函数以支持输出路径
                extract(full_path, True, output_path)  # 假设修改后的extract支持第3个参数

                # 更新进度
                self.progress = int((i + 1) / total_files * 100)
                self.root.after(10, self.update_progress, self.progress)
                self.log(f"✅ 已完成: {file_}")

            self.log("🎉 提取完成！")

        except Exception as e:
            self.log(f"❌ 错误: {str(e)}")
        finally:
            self.start_btn.config(state=NORMAL)
            self.current_file.set("等待开始...")

    def update_progress(self, value):
        self.pb['value'] = value

    def open_output_folder(self):
        path = self.output_path.get() or self.input_path.get()
        if not path:
            messagebox.showerror("❌ 错误", "路径未设置")
            return

        try:
            os.startfile(path)  # Windows
        except:
            try:
                os.system(f'open "{path}"')  # macOS
            except:
                os.system(f'xdg-open "{path}"')  # Linux


if __name__ == "__main__":
    root = Tk()
    app = ExtractGUI(root)
    root.mainloop()
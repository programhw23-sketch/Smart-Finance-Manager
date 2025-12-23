import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib

# 設定中文字型 (解決 Windows 系統 Matplotlib 中文亂碼問題)
matplotlib.rc('font', family='Microsoft JhengHei')

# === 1. 資料庫邏輯層 ===
class DBManager:
    def __init__(self):
        self.conn = sqlite3.connect('finance_pro.db')
        self.cursor = self.conn.cursor()
        self.setup_tables()

    def setup_tables(self):
        # 使用者資料表 (帳號, 密碼, 每月預算)
        self.cursor.execute('CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT, budget REAL)')
        # 收支紀錄表 (使用者, 類型, 類別, 金額, 日期)
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS records 
                              (user TEXT, type TEXT, category TEXT, amount REAL, date TEXT)''')
        self.conn.commit()

    def register_user(self, user, pw):
        try:
            self.cursor.execute("INSERT INTO users VALUES (?, ?, ?)", (user, pw, 0.0))
            self.conn.commit()
            return True
        except: return False

    def login_check(self, user, pw):
        self.cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (user, pw))
        return self.cursor.fetchone()

    def add_record(self, user, t_type, cat, amt):
        date = datetime.now().strftime("%Y-%m-%d")
        self.cursor.execute("INSERT INTO records VALUES (?, ?, ?, ?, ?)", (user, t_type, cat, amt, date))
        self.conn.commit()

    def get_all_records(self, user):
        self.cursor.execute("SELECT type, category, amount, date FROM records WHERE user=? ORDER BY date DESC", (user,))
        return self.cursor.fetchall()

    def get_summary(self, user):
        self.cursor.execute("SELECT category, SUM(amount) FROM records WHERE user=? AND type='支出' GROUP BY category", (user,))
        return self.cursor.fetchall()

    def update_budget(self, user, amt):
        self.cursor.execute("UPDATE users SET budget=? WHERE username=?", (amt, user))
        self.conn.commit()

# === 2. 主程式介面層 ===
class FinanceApp:
    def __init__(self, root):
        self.db = DBManager()
        self.root = root
        self.root.title("智能個人財務管理系統 v2.5")
        self.root.geometry("950x700")
        self.user = None
        self.budget = 0.0
        self.colors = {"bg": "#FFFFFF", "side": "#2C3E50", "text": "#ECF0F1", "accent": "#3498DB", "danger": "#E74C3C"}
        self.login_ui()

    def clear_ui(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    # --- 登入/註冊畫面 ---
    def login_ui(self):
        self.user = None
        self.clear_ui()
        self.root.configure(bg="#F5F6FA")
        
        frame = tk.Frame(self.root, bg="white", padx=50, pady=50, highlightbackground="#DCDDE1", highlightthickness=1)
        frame.place(relx=0.5, rely=0.5, anchor="center")
        
        tk.Label(frame, text="財務管理系統", font=("Microsoft JhengHei", 24, "bold"), bg="white", fg="#2F3640").grid(row=0, columnspan=2, pady=(0, 20))
        
        tk.Label(frame, text="帳號:", bg="white", font=("Microsoft JhengHei", 10)).grid(row=1, column=0, sticky="w")
        self.u_en = tk.Entry(frame, width=28, font=("Arial", 12))
        self.u_en.grid(row=2, column=0, columnspan=2, pady=(0, 15))
        
        tk.Label(frame, text="密碼:", bg="white", font=("Microsoft JhengHei", 10)).grid(row=3, column=0, sticky="w")
        self.p_en = tk.Entry(frame, width=28, font=("Arial", 12), show="*")
        self.p_en.grid(row=4, column=0, columnspan=2, pady=(0, 25))
        
        tk.Button(frame, text="立即登入", command=self.do_login, width=24, bg=self.colors["accent"], fg="white", font=("Microsoft JhengHei", 12, "bold"), relief="flat", cursor="hand2").grid(row=5, columnspan=2, pady=5)
        tk.Button(frame, text="註冊新帳號", command=self.do_register, width=24, bg="#2ECC71", fg="white", font=("Microsoft JhengHei", 12), relief="flat", cursor="hand2").grid(row=6, columnspan=2)

    def do_login(self):
        u, p = self.u_en.get().strip(), self.p_en.get().strip()
        if not u or not p:
            messagebox.showwarning("提示", "帳號或密碼不能為空白！")
            return
        
        res = self.db.login_check(u, p)
        if res:
            self.user, self.budget = res[0], res[2]
            self.main_ui()
        else:
            messagebox.showerror("失敗", "帳號或密碼錯誤")

    def do_register(self):
        u, p = self.u_en.get().strip(), self.p_en.get().strip()
        if not u or not p:
            messagebox.showwarning("提示", "請輸入完整的註冊資訊")
            return
        
        if self.db.register_user(u, p):
            messagebox.showinfo("成功", "註冊成功！現在可以使用該帳號登入。")
        else:
            messagebox.showwarning("警告", "帳號名稱已被佔用")

    # --- 主導覽介面 ---
    def main_ui(self):
        self.clear_ui()
        # 側邊選單
        side_bar = tk.Frame(self.root, width=240, bg=self.colors["side"])
        side_bar.pack(side="left", fill="y")
        
        tk.Label(side_bar, text="💰 財務主控台", font=("Microsoft JhengHei", 16, "bold"), bg=self.colors["side"], fg="white").pack(pady=40)
        
        menu = [("📝 新增收支", self.add_ui), ("📋 歷史紀錄", self.history_ui), 
                ("📊 圖表分析", self.chart_ui), ("🎯 預算設定", self.target_ui), ("💡 財務分析", self.advice_ui)]
        
        for text, cmd in menu:
            btn = tk.Button(side_bar, text=f"  {text}", command=cmd, font=("Microsoft JhengHei", 11), 
                            bg=self.colors["side"], fg="white", relief="flat", padx=25, pady=12, anchor="w", cursor="hand2")
            btn.pack(fill="x")
            btn.bind("<Enter>", lambda e, b=btn: b.configure(bg="#34495E"))
            btn.bind("<Leave>", lambda e, b=btn: b.configure(bg=self.colors["side"]))

        tk.Button(side_bar, text="🚪 登出系統", command=self.logout, bg=self.colors["danger"], fg="white", 
                  relief="flat", font=("Microsoft JhengHei", 11), pady=10, cursor="hand2").pack(side="bottom", fill="x")

        # 內容顯示區
        self.main_content = tk.Frame(self.root, bg="white", padx=40, pady=40)
        self.main_content.pack(side="right", expand=True, fill="both")
        self.history_ui()

    def logout(self):
        if messagebox.askyesno("登出", "確定要登出系統嗎？"):
            self.login_ui()

    def clear_content(self):
        for widget in self.main_content.winfo_children():
            widget.destroy()

    # --- 功能區塊 ---
    def history_ui(self):
        self.clear_content()
        tk.Label(self.main_content, text=f"📋 {self.user} 的收支清單", font=("Microsoft JhengHei", 20, "bold"), bg="white").pack(anchor="w", pady=(0, 20))
        
        cols = ("type", "cat", "amt", "date")
        tree = ttk.Treeview(self.main_content, columns=cols, show="headings")
        tree.heading("type", text="收/支"); tree.heading("cat", text="類別")
        tree.heading("amt", text="金額 (TWD)"); tree.heading("date", text="日期")
        
        for r in self.db.get_all_records(self.user):
            tree.insert("", "end", values=r)
        tree.pack(fill="both", expand=True)

    def add_ui(self):
        self.clear_content()
        tk.Label(self.main_content, text="➕ 紀錄一筆新收支", font=("Microsoft JhengHei", 20, "bold"), bg="white").pack(anchor="w", pady=(0, 20))
        
        f = tk.Frame(self.main_content, bg="#F8F9FA", padx=30, pady=30, highlightbackground="#E9ECEF", highlightthickness=1)
        f.pack(fill="x")

        tk.Label(f, text="交易類型:", bg="#F8F9FA").grid(row=0, column=0, pady=10, sticky="e")
        t_cb = ttk.Combobox(f, values=["收入", "支出"], state="readonly", font=("Arial", 11))
        t_cb.grid(row=0, column=1, padx=15); t_cb.current(1)

        tk.Label(f, text="類別項目:", bg="#F8F9FA").grid(row=1, column=0, pady=10, sticky="e")
        c_cb = ttk.Combobox(f, values=["薪資", "餐飲", "交通", "購物", "娛樂", "醫療", "居住", "其他"], state="readonly", font=("Arial", 11))
        c_cb.grid(row=1, column=1, padx=15); c_cb.current(1)

        tk.Label(f, text="金額:", bg="#F8F9FA").grid(row=2, column=0, pady=10, sticky="e")
        a_en = tk.Entry(f, font=("Arial", 12))
        a_en.grid(row=2, column=1, padx=15)

        def save():
            try:
                val = float(a_en.get())
                if val <= 0: raise ValueError
                self.db.add_record(self.user, t_cb.get(), c_cb.get(), val)
                messagebox.showinfo("成功", "已儲存紀錄")
                self.history_ui()
            except: messagebox.showerror("錯誤", "請輸入有效的正數字金額")

        tk.Button(f, text="儲存資料", command=save, bg="#27AE60", fg="white", font=("Microsoft JhengHei", 12, "bold"), width=15).grid(row=3, columnspan=2, pady=25)

    def chart_ui(self):
        self.clear_content()
        data = self.db.get_summary(self.user)
        if not data:
            tk.Label(self.main_content, text="⚠️ 尚無支出資料可供繪製圖表", font=("Microsoft JhengHei", 14), bg="white").pack(pady=100)
            return

        fig, ax = plt.subplots(figsize=(6, 5))
        ax.pie([d[1] for d in data], labels=[d[0] for d in data], autopct='%1.1f%%', startangle=90, colors=plt.cm.Set3.colors)
        ax.set_title(f"{self.user} 的每月支出分佈", pad=20)
        
        canvas = FigureCanvasTkAgg(fig, master=self.main_content)
        canvas.draw()
        canvas.get_tk_widget().pack()

    def target_ui(self):
        self.clear_content()
        tk.Label(self.main_content, text="🎯 設定每月預算上限", font=("Microsoft JhengHei", 20, "bold"), bg="white").pack(anchor="w", pady=(0, 20))
        
        v_en = tk.Entry(self.main_content, font=("Arial", 20), justify="center", width=15)
        v_en.insert(0, str(self.budget)); v_en.pack(pady=30)
        
        def update():
            try:
                nb = float(v_en.get())
                self.db.update_budget(self.user, nb)
                self.budget = nb
                messagebox.showinfo("成功", "月預算已更新")
                self.advice_ui()
            except: messagebox.showerror("錯誤", "請輸入數字")

        tk.Button(self.main_content, text="儲存預算設定", command=update, bg=self.colors["accent"], fg="white", font=("Microsoft JhengHei", 12, "bold"), padx=30).pack()

    def advice_ui(self):
        self.clear_content()
        data = self.db.get_summary(self.user)
        total_exp = sum(d[1] for d in data)
        over = total_exp > self.budget and self.budget > 0
        
        tk.Label(self.main_content, text="💡 財務健檢建議", font=("Microsoft JhengHei", 20, "bold"), bg="white").pack(anchor="w", pady=(0, 30))
        
        box = tk.Frame(self.main_content, bg="#F8F9FA", padx=30, pady=30, highlightthickness=1, highlightbackground="#E9ECEF")
        box.pack(fill="x")

        tk.Label(box, text=f"本月總支出： NT$ {total_exp:,.0f}", font=("Arial", 15), bg="#F8F9FA").pack(anchor="w")
        tk.Label(box, text=f"您的預算額： NT$ {self.budget:,.0f}", font=("Arial", 15), bg="#F8F9FA").pack(anchor="w", pady=10)
        
        status_lbl = tk.Label(box, text="狀態：" + ("⚠️ 預算超支！" if over else "✅ 掌控中"), 
                              font=("Microsoft JhengHei", 18, "bold"), fg=(self.colors["danger"] if over else "#27AE60"), bg="#F8F9FA")
        status_lbl.pack(pady=20)

        msg = f"注意：您已超過預算 {total_exp - self.budget:,.0f} 元，請節制購物。" if over else "太棒了！目前的開銷還在預算範圍內，請繼續保持優良習慣。"
        tk.Label(box, text=msg, font=("Microsoft JhengHei", 11), bg="#F8F9FA", fg="#555").pack()

if __name__ == "__main__":
    root = tk.Tk()
    app = FinanceApp(root)
    root.mainloop()
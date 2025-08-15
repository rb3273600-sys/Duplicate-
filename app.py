import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
import database
import os
import shutil
from PIL import Image, ImageTk

PROFILE_IMG_DIR = "profile_images"
DEFAULT_PROFILE_IMG = "default.png"

class ActivityLogWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Activity Logs")
        self.root.geometry("800x600")

        log_frame = ttk.Frame(self.root, padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True)

        cols = ("ID", "Timestamp", "Username", "Action")
        self.log_tree = ttk.Treeview(log_frame, columns=cols, show="headings")

        self.log_tree.heading("ID", text="ID")
        self.log_tree.column("ID", width=50, anchor=tk.CENTER)
        self.log_tree.heading("Timestamp", text="Timestamp")
        self.log_tree.column("Timestamp", width=150)
        self.log_tree.heading("Username", text="Username")
        self.log_tree.column("Username", width=120)
        self.log_tree.heading("Action", text="Action")

        scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_tree.yview)
        self.log_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.populate_logs()

    def populate_logs(self):
        for log in database.get_all_logs():
            username = log['username'] if log['username'] else "N/A (User Deleted)"
            self.log_tree.insert("", "end", values=(log['id'], log['timestamp'], username, log['action']))

class ProfileWindow:
    def __init__(self, root, current_user, update_callback):
        self.root = root
        self.current_user = current_user
        self.update_callback = update_callback
        self.root.title("Edit Profile")

        frame = ttk.Frame(self.root, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)

        self.image_label = ttk.Label(frame)
        self.image_label.pack(pady=10)
        self.load_profile_image()

        ttk.Button(frame, text="Change Profile Picture", command=self.change_picture).pack(pady=10)

    def load_profile_image(self, image_path=None):
        if image_path is None: image_path = self.current_user['profile_image_path']
        if not image_path or not os.path.exists(image_path): image_path = DEFAULT_PROFILE_IMG
        try:
            img = Image.open(image_path).resize((150, 150), Image.Resampling.LANCZOS)
            self.photo_image = ImageTk.PhotoImage(img)
            self.image_label.config(image=self.photo_image)
        except Exception as e:
            print(f"Error loading image: {e}")

    def change_picture(self):
        filepath = filedialog.askopenfilename(title="Select a Profile Picture", filetypes=[("Image Files", "*.png *.jpg *.jpeg *.gif")])
        if not filepath: return
        ext = os.path.splitext(filepath)[1]
        new_path = os.path.join(PROFILE_IMG_DIR, f"user_{self.current_user['id']}{ext}")
        try:
            shutil.copy(filepath, new_path)
            database.update_profile_picture_path(self.current_user['id'], new_path)
            database.log_activity(self.current_user['id'], "User updated profile picture")
            self.current_user['profile_image_path'] = new_path
            self.load_profile_image(new_path)
            self.update_callback()
            messagebox.showinfo("Success", "Profile picture updated!", parent=self.root)
        except Exception as e:
            messagebox.showerror("Error", f"Could not save image: {e}", parent=self.root)


class AdminWindow:
    def __init__(self, root, current_admin):
        self.root = root
        self.current_admin = current_admin
        self.root.title("Admin Panel")
        self.root.geometry("900x600")

        list_frame = ttk.LabelFrame(self.root, text="Users", padding="10")
        list_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.user_tree = ttk.Treeview(list_frame, columns=("ID", "Username", "Is Admin"), show="headings")
        self.user_tree.heading("ID", text="ID"); self.user_tree.column("ID", width=50)
        self.user_tree.heading("Username", text="Username")
        self.user_tree.heading("Is Admin", text="Is Admin"); self.user_tree.column("Is Admin", width=80)
        self.user_tree.pack(fill=tk.BOTH, expand=True)
        self.user_tree.bind("<<TreeviewSelect>>", self.on_user_select)
        ttk.Button(list_frame, text="Refresh List", command=self.populate_user_list).pack(pady=5)

        form_frame = ttk.Frame(self.root, padding="10")
        form_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        add_frame = ttk.LabelFrame(form_frame, text="Add New User", padding="10")
        add_frame.pack(fill=tk.X, pady=5)
        ttk.Label(add_frame, text="Username:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.add_username_entry = ttk.Entry(add_frame)
        self.add_username_entry.grid(row=0, column=1, padx=5, pady=5)
        ttk.Label(add_frame, text="Password:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.add_password_entry = ttk.Entry(add_frame, show="*")
        self.add_password_entry.grid(row=1, column=1, padx=5, pady=5)
        self.add_is_admin_var = tk.IntVar()
        ttk.Checkbutton(add_frame, text="Is Admin", variable=self.add_is_admin_var).grid(row=2, column=0, columnspan=2, pady=5)
        ttk.Button(add_frame, text="Add User", command=self.add_user).grid(row=3, column=0, columnspan=2, pady=10)

        self.edit_frame = ttk.LabelFrame(form_frame, text="Edit Selected User", padding="10")
        self.edit_frame.pack(fill=tk.X, pady=5)
        ttk.Label(self.edit_frame, text="Username:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.edit_username_entry = ttk.Entry(self.edit_frame)
        self.edit_username_entry.grid(row=0, column=1, padx=5, pady=5)
        ttk.Label(self.edit_frame, text="New Password:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.edit_password_entry = ttk.Entry(self.edit_frame, show="*")
        self.edit_password_entry.grid(row=1, column=1, padx=5, pady=5)
        ttk.Label(self.edit_frame, text="(leave blank to keep same)", style="TLabel.small").grid(row=2, column=1, padx=5, sticky="w")
        self.edit_is_admin_var = tk.IntVar()
        ttk.Checkbutton(self.edit_frame, text="Is Admin", variable=self.edit_is_admin_var).grid(row=3, column=0, columnspan=2, pady=5)
        ttk.Button(self.edit_frame, text="Save Changes", command=self.update_user).grid(row=4, column=0, columnspan=2, pady=10)
        ttk.Button(self.edit_frame, text="Delete Selected User", command=self.delete_user, style="Danger.TButton").grid(row=5, column=0, columnspan=2, pady=5)

        ttk.Button(form_frame, text="View Activity Logs", command=self.view_logs).pack(pady=20)
        self.selected_user_id = None
        self.populate_user_list()
        self.toggle_edit_frame(False)

    def view_logs(self): ActivityLogWindow(tk.Toplevel(self.root))
    def populate_user_list(self):
        for i in self.user_tree.get_children(): self.user_tree.delete(i)
        for user in database.get_all_users(): self.user_tree.insert("", "end", values=(user['id'], user['username'], "Yes" if user['is_admin'] else "No"))
    def on_user_select(self, event):
        items = self.user_tree.selection()
        if not items: return
        user_id = self.user_tree.item(items[0])['values'][0]
        self.selected_user_id = user_id
        user = database.get_user_by_id(user_id)
        if user:
            self.edit_username_entry.delete(0, tk.END); self.edit_username_entry.insert(0, user['username'])
            self.edit_is_admin_var.set(user['is_admin'])
            self.toggle_edit_frame(True)
    def toggle_edit_frame(self, enabled):
        for child in self.edit_frame.winfo_children(): child.configure(state=tk.NORMAL if enabled else tk.DISABLED)
    def add_user(self):
        username, password, is_admin = self.add_username_entry.get(), self.add_password_entry.get(), self.add_is_admin_var.get() == 1
        if not username or not password: messagebox.showerror("Error", "Username and password are required.", parent=self.root); return
        if database.add_user(username, password, is_admin):
            messagebox.showinfo("Success", f"User '{username}' created.", parent=self.root)
            database.log_activity(self.current_admin['id'], f"Admin created user: {username}")
            self.add_username_entry.delete(0, tk.END); self.add_password_entry.delete(0, tk.END)
            self.populate_user_list()
        else: messagebox.showerror("Error", f"Username '{username}' already exists.", parent=self.root)
    def update_user(self):
        if self.selected_user_id is None: return
        username, password, is_admin = self.edit_username_entry.get(), self.edit_password_entry.get(), self.edit_is_admin_var.get()
        if not username: messagebox.showerror("Error", "Username cannot be empty.", parent=self.root); return
        database.update_user(self.selected_user_id, username, password if password else None, is_admin)
        messagebox.showinfo("Success", "User updated.", parent=self.root)
        database.log_activity(self.current_admin['id'], f"Admin updated user ID: {self.selected_user_id}")
        self.edit_password_entry.delete(0, tk.END); self.populate_user_list()
    def delete_user(self):
        if self.selected_user_id is None: return
        if self.selected_user_id == self.current_admin['id']: messagebox.showerror("Error", "You cannot delete yourself.", parent=self.root); return
        if messagebox.askyesno("Confirm Delete", "Delete selected user? This action cannot be undone.", parent=self.root, icon='warning'):
            database.delete_user(self.selected_user_id)
            messagebox.showinfo("Success", "User deleted.", parent=self.root)
            database.log_activity(self.current_admin['id'], f"Admin deleted user ID: {self.selected_user_id}")
            self.selected_user_id = None; self.toggle_edit_frame(False); self.populate_user_list()

class MainWindow:
    def __init__(self, root, current_user, logout_callback):
        self.root = root
        self.current_user = current_user
        self.logout_callback = logout_callback
        self.root.title("Duplicate Data Finder")
        self.root.geometry("800x600")
        self.duplicates_df = None

        top_bar = ttk.Frame(self.root, padding="5 5 5 0")
        top_bar.pack(fill=tk.X, padx=10, pady=5)
        self.profile_image_label = ttk.Label(top_bar)
        self.profile_image_label.pack(side=tk.LEFT, padx=5)
        self.load_and_display_profile_image()
        ttk.Label(top_bar, text=f"Welcome, {self.current_user['username']}").pack(side=tk.LEFT)
        self.logout_button = ttk.Button(top_bar, text="Logout", command=self.logout)
        self.logout_button.pack(side=tk.RIGHT, padx=5)
        self.profile_button = ttk.Button(top_bar, text="Profile", command=self.open_profile_window)
        self.profile_button.pack(side=tk.RIGHT, padx=5)
        if self.current_user['is_admin']:
            ttk.Button(top_bar, text="Admin Panel", command=self.open_admin_panel).pack(side=tk.RIGHT, padx=5)

        controls_frame = ttk.LabelFrame(self.root, text="Controls", padding="10")
        controls_frame.pack(fill=tk.X, padx=10, pady=5)
        ttk.Button(controls_frame, text="Find Duplicates", command=self.find_duplicates).pack(side=tk.LEFT, padx=5)
        ttk.Button(controls_frame, text="Clear Results", command=self.clear_display).pack(side=tk.LEFT, padx=5)
        ttk.Button(controls_frame, text="Export Results", command=self.export_data).pack(side=tk.LEFT, padx=5)

        results_frame = ttk.LabelFrame(self.root, text="Results", padding="10")
        results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.tree_scroll_y = ttk.Scrollbar(results_frame, orient=tk.VERTICAL)
        self.tree_scroll_x = ttk.Scrollbar(results_frame, orient=tk.HORIZONTAL)
        self.tree = ttk.Treeview(results_frame, yscrollcommand=self.tree_scroll_y.set, xscrollcommand=self.tree_scroll_x.set)
        self.tree_scroll_y.config(command=self.tree.yview); self.tree_scroll_x.config(command=self.tree.xview)
        self.tree_scroll_y.pack(side=tk.RIGHT, fill=tk.Y); self.tree_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.tree.pack(fill=tk.BOTH, expand=True)

    def load_and_display_profile_image(self):
        path = self.current_user['profile_image_path']
        if not path or not os.path.exists(path): path = DEFAULT_PROFILE_IMG
        try:
            img = Image.open(path).resize((40, 40), Image.Resampling.LANCZOS)
            self.profile_photo_image = ImageTk.PhotoImage(img)
            self.profile_image_label.config(image=self.profile_photo_image)
        except Exception as e: print(f"Error loading main window profile image: {e}")
    def open_profile_window(self): ProfileWindow(tk.Toplevel(self.root), self.current_user, self.load_and_display_profile_image)
    def open_admin_panel(self): AdminWindow(tk.Toplevel(self.root), self.current_user)
    def find_duplicates(self):
        filepath = filedialog.askopenfilename(filetypes=[("Excel Files", "*.xlsx;*.xls")])
        if not filepath: return
        try:
            df = pd.read_excel(filepath)
            self.duplicates_df = df[df.duplicated(subset=None, keep=False)].sort_values(by=list(df.columns))
            if self.duplicates_df.empty: messagebox.showinfo("No Duplicates", "No duplicate rows found."); self.clear_display(); return
            self.update_treeview(self.duplicates_df)
            database.log_activity(self.current_user['id'], f"Found duplicates in: {os.path.basename(filepath)}")
        except Exception as e: messagebox.showerror("Error", f"Failed to read file: {e}")
    def update_treeview(self, df):
        self.clear_display()
        self.tree["columns"] = list(df.columns)
        self.tree["show"] = "headings"
        for col in df.columns: self.tree.heading(col, text=col); self.tree.column(col, width=100, anchor=tk.W)
        for row in df.itertuples(index=False): self.tree.insert("", "end", values=list(row))
    def clear_display(self):
        for i in self.tree.get_children(): self.tree.delete(i)
        self.tree["columns"] = (); self.duplicates_df = None
    def export_data(self):
        if self.duplicates_df is None or self.duplicates_df.empty: messagebox.showinfo("No Data", "There is no data to export."); return
        filepath = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel Files", "*.xlsx")], title="Save Duplicates As")
        if not filepath: return
        try:
            self.duplicates_df.to_excel(filepath, index=False)
            messagebox.showinfo("Success", f"Data exported to {filepath}")
            database.log_activity(self.current_user['id'], f"Exported data to: {os.path.basename(filepath)}")
        except Exception as e: messagebox.showerror("Error", f"Failed to export data: {e}")
    def logout(self):
        database.log_activity(self.current_user['id'], "User logged out")
        self.root.destroy(); self.logout_callback()

class LoginWindow:
    def __init__(self, root, login_success_callback):
        self.root = root
        self.login_success_callback = login_success_callback
        self.root.title("Login")
        self.root.resizable(False, False)
        frame = ttk.Frame(self.root, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        ttk.Label(frame, text="Username:").pack(pady=(0, 5))
        self.username_entry = ttk.Entry(frame)
        self.username_entry.pack(pady=(0, 10))
        ttk.Label(frame, text="Password:").pack(pady=(0, 5))
        self.password_entry = ttk.Entry(frame, show="*")
        self.password_entry.pack(pady=(0, 10))
        ttk.Button(frame, text="Login", command=self.login).pack(pady=10)
    def login(self):
        username, password = self.username_entry.get(), self.password_entry.get()
        user = database.get_user(username)
        if user and user['password_hash'] == database.hash_password(password):
            self.root.destroy(); database.log_activity(user['id'], "User logged in"); self.login_success_callback(user)
        else: messagebox.showerror("Login Failed", "Invalid username or password")

class App:
    def __init__(self, root):
        self.root = root
        self.current_user = None
        self.root.withdraw()
        self.show_login()
    def show_login(self): LoginWindow(tk.Toplevel(self.root), self.login_success)
    def login_success(self, user): self.current_user = user; self.show_main_window()
    def show_main_window(self):
        self.current_user = database.get_user(self.current_user['username'])
        MainWindow(tk.Toplevel(self.root), self.current_user, self.logout)
    def logout(self): self.current_user = None; self.show_login()

def main():
    if not os.path.exists(PROFILE_IMG_DIR): os.makedirs(PROFILE_IMG_DIR)
    if not os.path.exists(DEFAULT_PROFILE_IMG):
        try: Image.new('RGB', (100, 100), color='grey').save(DEFAULT_PROFILE_IMG, 'PNG')
        except Exception as e: print(f"Could not create default profile image: {e}")
    database.init_db()
    database.create_initial_admin()
    root = tk.Tk()

    style = ttk.Style(root)
    available_themes = style.theme_names()
    for theme in ["clam", "alt", "default"]:
        if theme in available_themes:
            style.theme_use(theme)
            break
    style.configure("Danger.TButton", foreground="red")
    style.configure("TLabel.small", font=("", 7))

    app = App(root)
    root.mainloop()

if __name__ == "__main__":
    main()

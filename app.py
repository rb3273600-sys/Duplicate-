import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd

class MainWindow:
    def __init__(self, root, restart_callback):
        self.root = root
        self.restart_callback = restart_callback
        self.root.title("Duplicate Data Finder")
        self.root.geometry("800x600")

        self.duplicates_df = None

        # Frame for buttons
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=10)

        self.find_button = tk.Button(button_frame, text="Find", command=self.find_duplicates)
        self.find_button.pack(side=tk.LEFT, padx=5)

        self.clear_button = tk.Button(button_frame, text="Clear", command=self.clear_display)
        self.clear_button.pack(side=tk.LEFT, padx=5)

        self.export_button = tk.Button(button_frame, text="Export", command=self.export_data)
        self.export_button.pack(side=tk.LEFT, padx=5)

        self.restart_button = tk.Button(button_frame, text="Restart", command=self.restart)
        self.restart_button.pack(side=tk.LEFT, padx=5)

        # Treeview for displaying data
        self.tree_frame = tk.Frame(self.root)
        self.tree_frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

        # Add scrollbars to the treeview
        self.tree_scroll_y = tk.Scrollbar(self.tree_frame, orient=tk.VERTICAL)
        self.tree_scroll_x = tk.Scrollbar(self.tree_frame, orient=tk.HORIZONTAL)

        self.tree = ttk.Treeview(self.tree_frame, yscrollcommand=self.tree_scroll_y.set, xscrollcommand=self.tree_scroll_x.set)

        self.tree_scroll_y.config(command=self.tree.yview)
        self.tree_scroll_x.config(command=self.tree.xview)

        self.tree_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.tree.pack(fill=tk.BOTH, expand=True)


    def find_duplicates(self):
        filepath = filedialog.askopenfilename(
            filetypes=[("Excel Files", "*.xlsx"), ("Excel Files", "*.xls")]
        )
        if not filepath:
            return

        try:
            df = pd.read_excel(filepath)
            # Find all rows that are duplicates. Sort to group them.
            self.duplicates_df = df[df.duplicated(subset=None, keep=False)].sort_values(by=list(df.columns))

            if self.duplicates_df.empty:
                messagebox.showinfo("No Duplicates", "No duplicate rows found.")
                self.clear_display()
                return

            self.update_treeview(self.duplicates_df)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to read file: {e}")

    def update_treeview(self, df):
        self.clear_display()

        self.tree["columns"] = list(df.columns)
        self.tree["show"] = "headings"

        for col in df.columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100, anchor=tk.W)

        for index, row in df.iterrows():
            self.tree.insert("", "end", values=list(row))

    def clear_display(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        self.tree["columns"] = ()
        self.duplicates_df = None

    def export_data(self):
        if self.duplicates_df is None or self.duplicates_df.empty:
            messagebox.showinfo("No Data", "There is no data to export.")
            return

        filepath = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel Files", "*.xlsx"), ("All files", "*.*")],
            title="Save Duplicates As"
        )

        if not filepath:
            return

        try:
            self.duplicates_df.to_excel(filepath, index=False)
            messagebox.showinfo("Success", f"Data exported successfully to {filepath}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export data: {e}")

    def restart(self):
        self.root.destroy()
        self.restart_callback()


class LoginWindow:
    def __init__(self, root, show_main_callback):
        self.root = root
        self.show_main_callback = show_main_callback
        self.root.title("Login")
        self.root.geometry("300x150")

        self.username_label = tk.Label(root, text="Username:")
        self.username_label.pack()
        self.username_entry = tk.Entry(root)
        self.username_entry.pack()

        self.password_label = tk.Label(root, text="Password:")
        self.password_label.pack()
        self.password_entry = tk.Entry(root, show="*")
        self.password_entry.pack()

        self.login_button = tk.Button(root, text="Login", command=self.login)
        self.login_button.pack()

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if username == "Rampratap" and password == "Ram@2001!!":
            self.root.destroy()
            self.show_main_callback()
        else:
            messagebox.showerror("Login Failed", "Invalid username or password")


class App:
    def __init__(self, root):
        self.root = root
        self.root.withdraw()  # Hide the main root window
        self.show_login()

    def show_login(self):
        self.login_window = tk.Toplevel(self.root)
        LoginWindow(self.login_window, self.show_main_window)

    def show_main_window(self):
        self.main_window = tk.Toplevel(self.root)
        MainWindow(self.main_window, self.show_login)


def main():
    root = tk.Tk()
    app = App(root)
    root.mainloop()

if __name__ == "__main__":
    main()

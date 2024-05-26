import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk
import requests
from threading import Thread
import pandas as pd

def load_file():
    filepath = filedialog.askopenfilename()
    if filepath:
        with open(filepath, 'r') as file:
            urls_text.insert(tk.END, file.read())

def save_to_excel(links, filename='results.xlsx', working=True):
    df = pd.DataFrame(links, columns=['URL'])
    status = 'Working' if working else 'Not Working'
    filepath = filedialog.asksaveasfilename(defaultextension=".xlsx", initialfile=f"{status}_{filename}")
    if filepath:
        df.to_excel(filepath, index=False)
        messagebox.showinfo("Save Successful", f"{status} links saved to Excel successfully!")

def check_links():
    urls = urls_text.get("1.0", tk.END).split()
    if not urls:
        messagebox.showinfo("No URLs", "Please enter some URLs to check.")
        return
    total_urls = len(urls)
    working_links = []
    not_working_links = []
    for idx, url in enumerate(urls, 1):
        if not url.startswith('http://') and not url.startswith('https://'):
            url = 'http://' + url  # Ensuring URL has http/https prefix
        try:
            response = requests.get(url, allow_redirects=True, timeout=10)
            if response.status_code == 200:
                working_links.append(url)
                result_text.insert(tk.END, f"Working: {url}\n", 'green')
            else:
                not_working_links.append((url, "Failed to load"))
                result_text.insert(tk.END, f"Not Working: {url}\n", 'red')
        except requests.RequestException as e:
            error_message = "Failed to load"
            not_working_links.append((url, error_message))
            result_text.insert(tk.END, f"Not Working: {url} - Error: {error_message}\n", 'red')
        progress_var.set(idx / total_urls * 100)
        progress_label.config(text=f"{idx}/{total_urls} Checked")
        count_label.config(text=f"Working: {len(working_links)}, Not Working: {len(not_working_links)}")
        root.update_idletasks()
    root.after(100, lambda: percentage_label.config(text=f"Working: {len(working_links)/total_urls*100:.2f}%, Not Working: {len(not_working_links)/total_urls*100:.2f}%"))
    root.after(100, lambda: save_working_button.config(state=tk.NORMAL if working_links else tk.DISABLED, command=lambda: save_to_excel(working_links, working=True)))
    root.after(100, lambda: save_not_working_button.config(state=tk.NORMAL if not_working_links else tk.DISABLED, command=lambda: save_to_excel(not_working_links, working=False)))

def start_check():
    Thread(target=check_links).start()

def reset_application():
    urls_text.delete('1.0', tk.END)
    result_text.delete('1.0', tk.END)
    progress_var.set(0)
    progress_label.config(text="0/0 Checked")
    percentage_label.config(text="Working: 0%, Not Working: 0%")
    count_label.config(text="Working: 0, Not Working: 0")
    save_working_button.config(state=tk.DISABLED)
    save_not_working_button.config(state=tk.DISABLED)

root = tk.Tk()
root.title("Link Checker Application")

urls_text = scrolledtext.ScrolledText(root, height=10)
urls_text.pack(pady=20)

load_button = tk.Button(root, text="Load URLs from File", command=load_file)
load_button.pack()

check_button = tk.Button(root, text="Check Links", command=start_check)
check_button.pack(pady=10)

reset_button = tk.Button(root, text="Reset", command=reset_application)
reset_button.pack(pady=10)

result_text = scrolledtext.ScrolledText(root, height=10)
result_text.tag_config('green', foreground='green')
result_text.tag_config('red', foreground='red')
result_text.pack(pady=20)

progress_var = tk.DoubleVar()
progress_bar = ttk.Progressbar(root, orient="horizontal", length=300, mode='determinate', variable=progress_var)
progress_bar.pack()

progress_label = tk.Label(root, text="0/0 Checked")
progress_label.pack()

percentage_label = tk.Label(root, text="Working: 0%, Not Working: 0%")
percentage_label.pack()

count_label = tk.Label(root, text="Working: 0, Not Working: 0")
count_label.pack()

save_working_button = tk.Button(root, text="Export Working", state=tk.DISABLED)
save_working_button.pack(side=tk.LEFT, padx=10)

save_not_working_button = tk.Button(root, text="Export Not Working", state=tk.DISABLED)
save_not_working_button.pack(side=tk.RIGHT, padx=10)

root.mainloop()

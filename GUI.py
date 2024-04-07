import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import os
import threading
import queue
from image_resizer import batch_resize
import os

# Assuming your script is running from the project root directory
PROJECT_ROOT = os.getcwd()

def select_input_dir():
    directory = filedialog.askdirectory(initialdir=PROJECT_ROOT)
    if directory:  # Check if a directory was selected
        input_dir_var.set(directory)

def select_output_dir():
    directory = filedialog.askdirectory(initialdir=PROJECT_ROOT)
    if directory:  # Check if a directory was selected
        output_dir_var.set(directory)


def start_resizing(template_size):
    input_dir = input_dir_var.get()
    output_dir = output_dir_var.get()
    if not input_dir or not output_dir:
        messagebox.showwarning("Warning", "Please select all directories.")
        return
    if isinstance(template_size, str):  # If custom size
        try:
            width, height = map(int, template_size.split(','))
        except ValueError:
            messagebox.showerror("Error", "Invalid template size format. Use width,height.")
            return
    else:
        width, height = template_size
    threading.Thread(target=lambda: batch_resize_wrapper(input_dir, output_dir, (width, height), progress_queue)).start()
    progress_bar['value'] = 0

def use_custom_size():
    custom_size = custom_size_var.get()
    start_resizing(custom_size)

def batch_resize_wrapper(input_dir, output_dir, template_size, progress_queue):
    batch_resize(input_dir, output_dir, template_size, progress_queue)
    progress_queue.put(100)  # Signal completion

def update_progress_bar():
    try:
        while True:
            progress = progress_queue.get_nowait()
            progress_bar['value'] = progress
            if progress >= 100:
                messagebox.showinfo("Info", "Resizing completed.")
                break
    except queue.Empty:
        pass
    root.after(100, update_progress_bar)

# GUI Setup
progress_queue = queue.Queue()
root = tk.Tk()
root.title("Image Resizer")

input_dir_var = tk.StringVar()
output_dir_var = tk.StringVar()
custom_size_var = tk.StringVar()


tk.Label(root, text="Input Directory:").pack()
tk.Entry(root, textvariable=input_dir_var, width=50).pack()
tk.Button(root, text="Browse", command=select_input_dir).pack()

tk.Label(root, text="Output Directory for Resized Images:").pack()
tk.Entry(root, textvariable=output_dir_var, width=50).pack()
tk.Button(root, text="Browse", command=select_output_dir).pack()


tk.Label(root, text="Predefined sizes:").pack()
# Predefined size buttons
tk.Button(root, text="1000x1000", command=lambda: start_resizing((1000, 1000))).pack()
tk.Button(root, text="1801x2600", command=lambda: start_resizing((1801, 2600))).pack()

tk.Label(root, text="Custom Size (width,height):").pack()
custom_size_entry = tk.Entry(root, textvariable=custom_size_var, width=50)
custom_size_entry.pack()


# Custom size button
tk.Button(root, text="Use Custom Size", command=use_custom_size).pack()

progress_bar = ttk.Progressbar(root, orient="horizontal", length=300, mode="determinate")
progress_bar.pack()

root.after(100, update_progress_bar)
root.mainloop()

import os
import copy
import numpy as np
import open3d as o3d
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkinterdnd2 import DND_FILES, TkinterDnD


class PLYProcessor:
    def __init__(self, root):
        self.root = root
        self.setup_ui()
        self.create_widgets()

    def setup_ui(self):
        self.root.title("PLY Converter")
        self.root.minsize(300, 200)
        self.root.lift()
        self.root.attributes("-topmost", 1)
        self.root.after_idle(root.attributes,'-topmost',False)

    def create_widgets(self):
        self.drop_label = tk.Label(self.root, text="Drag and drop .PLY files here", padx=20, pady=80)
        self.drop_label.pack()
        self.open_button = tk.Button(self.root, text="Open .PLY File", command=self.on_click)
        self.open_button.pack(padx=20, pady=10)
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(self.root, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(padx=20, pady=10)
        self.status_label = tk.Label(self.root, text="Status: Ready", padx=20, pady=10)
        self.status_label.pack()

        self.drop_label.drop_target_register(DND_FILES)
        self.drop_label.dnd_bind('<<Drop>>', self.on_drop)

    def update_status(self, message, value):
        self.udpate_progress(value)
        self.udpate_label(message)

    def udpate_progress(self, value):
        self.progress_var.set(value)

    def udpate_label(self, message):
        self.status_label.config(text="Status: " + message)

    def visualize_pointclouds(self, original_pcd, converted_pcd):
        combined_pcd = o3d.geometry.PointCloud()
        combined_pcd.points = o3d.utility.Vector3dVector(np.vstack((np.asarray(original_pcd.points), np.asarray(converted_pcd.points))))
        combined_pcd.colors = o3d.utility.Vector3dVector(np.vstack((np.tile([1.0, 0.0, 0.0], (len(original_pcd.points), 1)),
                                                                    np.tile([0.0, 0.0, 1.0], (len(converted_pcd.points), 1)))))
        self.show_intro()
        o3d.visualization.draw_geometries([combined_pcd, ],
                                            window_name="Compare Original and Converted PCD",
                                            width=1029, height=687, zoom=0.5,
                                            lookat=[2.6, 2.1, 1.5], front=[0.4, -0.2, -0.85], up=[-0.07, -1, 0.2])

    def show_intro(self):
        intro_text = "This visualization shows the original and converted point clouds side by side.\n\n"
        intro_text += "1. Original points (red)\n2. Converted points (blue)\n\n"
        intro_text += "Click OK to start the visualization."
        messagebox.showinfo("Result", intro_text)

    def start_progress(self, file_path):
        self.update_status("Opening file...", 25)
        self.root.update()
        original_pcd = self.open_ply_file(file_path)

        self.update_status("Converting to left-handed...", 50)
        self.root.update()
        converted_pcd = self.convert_to_left_handed(original_pcd)

        self.update_status("Saving result...", 75)
        self.root.update()
        self.save_result_file(converted_pcd)

        self.update_status("Finished", 100)
        self.root.update()
        self.visualize_pointclouds(original_pcd, converted_pcd)

    def on_click(self):
        file_path = self.get_file_path()
        if file_path:
            self.start_progress(file_path)

    def on_drop(self, event):
        file_path = self.get_file_path_on_drop(event)
        if file_path:
            self.start_progress(file_path)

    def get_file_path_on_drop(self, event):
        file_path = event.data.strip('{}')
        if file_path.lower().endswith(".ply"):
            return file_path
        return None

    def get_file_path(self):
        file_path = filedialog.askopenfilename(filetypes=[("PLY Files", "*.ply")])
        if file_path:
            return file_path
        return None
    
    def get_dir_path(self):
        folder_path = filedialog.askdirectory(title="Select a folder")
        if folder_path:
            return folder_path
        return None

    def convert_to_left_handed(self, pcd: o3d.geometry.PointCloud):
        points = np.asarray(copy.deepcopy(pcd.points))
        points[:, 0] = -points[:, 0]
        target_pcd = copy.deepcopy(pcd)
        target_pcd.points = o3d.utility.Vector3dVector(points)
        return target_pcd

    def open_ply_file(self, path):
        ply_file = o3d.io.read_point_cloud(path)
        return ply_file

    def save_result_file(self, pcd):
        if not os.path.exists("./results"):
            os.makedirs("./results")
        folder_path = self.get_dir_path()
        o3d.io.write_point_cloud(folder_path + "/left_handed.ply", pcd)

if __name__ == '__main__':
    root = TkinterDnD.Tk()
    ply_processor = PLYProcessor(root)
    root.mainloop()
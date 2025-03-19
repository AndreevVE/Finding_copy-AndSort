import shutil
import tkinter as tk
from tkinter import Label
from tkinter import filedialog
from tkinter import messagebox
from PIL import Image, ImageTk
import threading
import cv2
import os

class VideoPlayer:
    def __init__(self, root, video_path):
        self.root = root
        self.video_path = video_path
        self.label = Label(root)
        self.label.pack()
        self.running = False  # Flag to track the video-playing state
        self.thread = None

    def load_video(self):
        try:
            cap = cv2.VideoCapture(self.video_path)
            ret, frame = cap.read()
            if not ret:
                print("Error: Cannot read from video source.")
                return

            source_height, source_width, _ = frame.shape

            self.running = True

            while self.running:
                ret, frame = cap.read()
                if not ret:
                    break

                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame_image = ImageTk.PhotoImage(
                    Image.fromarray(frame).resize((source_width, source_height))
                )

                if self.label.winfo_exists():
                    self.label.config(image=frame_image)
                    self.label.image = frame_image
                else:
                    print("Label no longer exists. Stopping video thread.")
                    break

        except Exception as e:
            print(f"Error in video playback: {e}")

        finally:
            cap.release()
            print("Video playback thread exited.")

    def start_video(self):
        if not self.running:
            self.thread = threading.Thread(target=self.load_video, daemon=True)
            self.thread.start()

    def stop_video(self):
        if self.thread:
            self.thread.join(1)
        self.running = False


class ImageViewer:
    def __init__(self, root):
        self.path_too = None
        self.player = None
        self.stop_video_flag = False
        self.original_image = None
        self.my_label = None
        self.all_files = None
        self.index = None
        self.directory = None
        self.current_file = None
        self.root = root
        self.root.title('Image Viewer')
        self.root.geometry('2400x1200')
        self.root.configure(background='black')

        self.image_label = tk.Label(self.root)
#        self.image_label.pack()

        self.control_frame = tk.Frame(self.root)
        self.control_frame.pack()

        self.prev_button = tk.Button(self.control_frame, text='<', command=self.prev_image)
        self.prev_button.pack(side='left')

        self.open_button = tk.Button(self.control_frame, text='Open', command=self.open_image)
        self.open_button.pack(side='left')

        self.close_button = tk.Button(self.control_frame, text='Quit', command=self.root.quit)
        self.close_button.pack(side='left')

        self.zoom_in_button = tk.Button(self.control_frame, text='Zoom In', command=self.zoom_in)
        self.zoom_in_button.pack(side='left')

        self.zoom_out_button = tk.Button(self.control_frame, text='Zoom Out', command=self.zoom_out)
        self.zoom_out_button.pack(side='left')

        self.rotate_button = tk.Button(self.control_frame, text='Rotate', command=self.rotate)
        self.rotate_button.pack(side='left')

        self.delete_button = tk.Button(self.control_frame, text='Delete', command=self.delete)
        self.delete_button.pack(side='left')

        self.file_transfer_button = tk.Button(self.control_frame, text='File Transfer', command=self.file_transfer)
        self.file_transfer_button.pack(side='left')

        self.next_button = tk.Button(self.control_frame, text='>', command=self.next_image)
        self.next_button.pack(side='left')

        self.current_image_path = ''
        self.zoom_level = 1


    def open_image(self):
        self.current_image_path = filedialog.askopenfilename(defaultextension=".jpg",
            filetypes=[("All Files", "*.*"), ("JPEG", ".jpg"), ("PNG", ".png"), ("GIF", ".gif"), ("mp4", ".mp4")])

        if not self.current_image_path:
            return
        self.directory = os.path.dirname(self.current_image_path)
        self.all_files = sorted(os.listdir(self.directory))
        self.current_file = os.path.basename(self.current_image_path)
        self.index = self.all_files.index(self.current_file)
        self.load_image()

    def load_image(self):
        if self.stop_video_flag:
            self.stop_video()

        self.exctension = os.path.splitext(self.current_image_path)
        if self.current_image_path and self.exctension[1] in [".jpg", ".png", ".gif"]:
            self.image_label.pack(side='top', fill='both', expand=True, padx=10, pady=10)
            image = Image.open(self.current_image_path)

            max_size = (2200, 1100)
            image.thumbnail(max_size)
            self.original_image = image

            self.tk_image = ImageTk.PhotoImage(image)
            self.image_label.configure(image=self.tk_image)
            self.zoom_level = 1
        else:
            if self.image_label:
                self.image_label.pack_forget()
                self.image_label.configure(image='')
                self.load_video()

    def zoom_in(self):
        if self.stop_video_flag:
            return
        if not self.current_image_path:  
            return
        self.zoom_level *= 1.1  
        self.zoom_or_rotate_image()

    def zoom_out(self):
        if self.stop_video_flag:
            return
        if not self.current_image_path:  
            return
        if self.zoom_level < 0.1:  
            return
        self.zoom_level *= 0.9  
        self.zoom_or_rotate_image()

    def rotate(self):
        if self.stop_video_flag:
            return
        if not self.current_image_path: 
            return
        self.original_image = self.original_image.rotate(-90)
        self.zoom_or_rotate_image()

    def zoom_or_rotate_image(self):
        if self.stop_video_flag:
            return
        new_image = self.original_image.resize((int(self.original_image.width * self.zoom_level),
                                                int(self.original_image.height * self.zoom_level)))
        self.tk_image = ImageTk.PhotoImage(new_image)
        self.image_label.configure(image=self.tk_image)

    def delete(self):
        if not self.current_image_path:
            return
        if self.stop_video_flag:
            self.stop_video()

        current_file = os.path.basename(self.current_image_path)
        try:
            os.remove(self.current_image_path)
            self.all_files.remove(current_file)
            if self.all_files:
                index = self.all_files.index(current_file) if current_file in self.all_files else -1
                if index + 1 < len(self.all_files):
                    next_file = self.all_files[index + 1]
                else:
                    next_file = self.all_files[0]
                self.current_image_path = os.path.join(self.directory, next_file)
                self.current_file = os.path.basename(self.current_image_path)
                self.next_image()
            else:
                self.current_image_path = ''
                self.image_label.configure(image='')
                messagebox.showinfo("Удаление", "Файлы в директории закончились.")
        except ValueError:
            messagebox.showerror("Ошибка", "Файл не найден в директории.")


    def file_transfer(self):
        if not self.current_image_path:
            return
        if self.stop_video_flag:
            self.stop_video()

        current_file = os.path.basename(self.current_image_path)
        self.path_too = filedialog.askdirectory()
        try:
            shutil.copy2(self.current_image_path, self.path_too)
            os.remove(self.current_image_path)
            self.all_files.remove(current_file)
            if self.all_files:
                index = self.all_files.index(current_file) if current_file in self.all_files else -1
                if index + 1 < len(self.all_files):
                    next_file = self.all_files[index + 1]
                else:
                    next_file = self.all_files[0]
                self.current_image_path = os.path.join(self.directory, next_file)
                self.current_file = os.path.basename(self.current_image_path)
                self.load_image()
            else:
                self.current_image_path = ''
                self.image_label.configure(image='')
                messagebox.showinfo("Удаление", "Файлы в директории закончились.")
        except ValueError:
            messagebox.showerror("Ошибка", "Файл не найден в директории.")


    def next_image(self):
        if self.stop_video_flag:
            self.stop_video()

        if self.all_files:
            index = self.all_files.index(self.current_file) if self.current_file in self.all_files else -1
            if index + 1 < len(self.all_files):
                next_file = self.all_files[index + 1]
            else:
                next_file = self.all_files[0]
            self.current_image_path = os.path.join(self.directory, next_file)
            self.current_file = os.path.basename(self.current_image_path)
            self.load_image()


    def prev_image(self):
        if self.stop_video_flag:
            self.stop_video()
        index = self.all_files.index(self.current_file)
        if self.all_files:
            next_file = self.all_files[index - 1] if index >= 0 else self.all_files[-1]
            self.current_image_path = os.path.join(self.directory, next_file)
            self.current_file = os.path.basename(self.current_image_path)
            self.load_image()


    def stop_video(self):
        self.player.stop_video()
        self.my_label.destroy()
        self.stop_video_flag = False
        return


    def load_video(self) -> None:
        self.stop_video_flag = True
        self.my_label = tk.Label(self.root)
        butoms = tk.Button(self.my_label, text="Stop", command=self.stop_video, bg='red', fg='white')
        butoms.pack(side='bottom')
        self.my_label.pack(side='top', fill='both', expand=True, padx=10, pady=10)
        self.player = VideoPlayer(self.my_label, self.current_image_path)
        self.player.start_video()



if __name__ == '__main__':
    root = tk.Tk()
    app = ImageViewer(root)
    root.mainloop()
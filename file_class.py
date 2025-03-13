import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from PIL import Image, ImageTk
import os


class ImageViewer:
    def __init__(self, root):
        self.root = root
        self.root.title('Image Viewer')
        self.root.geometry('2400x1200')
        self.root.configure(background='black')

        self.image_label = tk.Label(self.root)
        self.image_label.pack()

        self.control_frame = tk.Frame(self.root)
        self.control_frame.pack()

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

        self.current_image_path = ''
        self.zoom_level = 1


    def open_image(self):
        self.current_image_path = filedialog.askopenfilename(defaultextension=".jpg",
            filetypes=[("All Files", "*.*"), ("JPEG", ".jpg"), ("PNG", ".png"), ("GIF", ".gif")])
        if self.current_image_path:
            self.load_image()

    def load_image(self):
        image = Image.open(self.current_image_path)

        ## Resize image for display
        max_size = (2200, 1100)
        image.thumbnail(max_size)

        ## Save a reference to the original image (for zooming/rotating)
        self.original_image = image

        ## Create a Tkinter-compatible image
        self.tk_image = ImageTk.PhotoImage(image)
        self.image_label.configure(image=self.tk_image)

        self.zoom_level = 1

    def zoom_in(self):
        if not self.current_image_path:  ## No image loaded
            return
        self.zoom_level *= 1.1  ## Increase zoom level by 10%
        self.zoom_or_rotate_image()

    def zoom_out(self):
        if not self.current_image_path:  ## No image loaded
            return
        if self.zoom_level < 0.1:  ## Limit outwards zoom
            return
        self.zoom_level *= 0.9  ## Decrease zoom level by 10%
        self.zoom_or_rotate_image()

    def rotate(self):
        if not self.current_image_path:  ## No image loaded
            return
        self.original_image = self.original_image.rotate(-90)
        self.zoom_or_rotate_image()

    def zoom_or_rotate_image(self):
        ## Zoom and rotate original image, convert to Tk image, and display
        new_image = self.original_image.resize((int(self.original_image.width * self.zoom_level),
                                                int(self.original_image.height * self.zoom_level)))
        self.tk_image = ImageTk.PhotoImage(new_image)
        self.image_label.configure(image=self.tk_image)

    def delete(self):
        if not self.current_image_path:
            return
        directory = os.path.dirname(self.current_image_path)
        all_files = sorted(os.listdir(directory))  # Сортируем список файлов
        current_file = os.path.basename(self.current_image_path)
        try:
            os.remove(self.current_image_path)
            index = all_files.index(current_file)
            all_files.pop(index)
            if all_files:
                next_file = all_files[index] if index < len(all_files) else all_files[0]
                self.current_image_path = os.path.join(directory, next_file)
                self.load_image()
            else:
                self.current_image_path = ''
                self.image_label.configure(image='')
                messagebox.showinfo("Удаление", "Файлы в директории закончились.")
        except ValueError:
            messagebox.showerror("Ошибка", "Файл не найден в директории.")


if __name__ == '__main__':
    root = tk.Tk()
    app = ImageViewer(root)
    root.mainloop()
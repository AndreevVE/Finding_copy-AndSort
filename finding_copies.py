import hashlib
import os
from PIL import Image
from PIL.ExifTags import TAGS
import ffmpeg
import shutil
import tkinter as tk
from tkinter import filedialog as fd

def select_directory():
    root = tk.Tk()  # пустое родительское окно
    root.withdraw()  # прячем его
    result = fd.askdirectory( master=root, mustexist=True)  # только существующие каталоги
    root.destroy()  # уничтожаем родительское окно
#    print(result)
    return result


def slect_mode():
    root = tk.Tk()
    root.title("Select mode")
    root.geometry("300x200")
    x = (root.winfo_screenwidth() - root.winfo_reqwidth()) / 2
    y = (root.winfo_screenheight() - root.winfo_reqheight()) / 2
    root.wm_geometry("+%d+%d" % (x, y-300))

    position = {"padx": 6, "pady": 6, "anchor":"nw"}
    languages = ["Search for copies", "Delete copies", "Sort media"]
    selected_mode = tk.StringVar() # по умолчанию ничего не выборанно
    selected_mode.set("Search for copies")
    header = tk.Label(text="Select mode")
    header.pack(**position)


    def select():
        header.config(text=f"Selected {selected_mode.get()}")



    def select_ok():
        root.destroy()


    for lang in languages:
        lang_btn = tk.Radiobutton(text=lang, value=lang, variable=selected_mode, command=select)
        lang_btn.pack(**position)
    ok_btn = tk.Button(root, text="Ok", command=select_ok)
    ok_btn.pack(padx = 6, pady = 8, anchor = "center")
    root.mainloop()

    return selected_mode.get()


def image_meta(file):
    try:
        image = Image.open(file)
        exifdata = image.getexif()
        for tag_id in exifdata:
            tag = TAGS.get(tag_id, tag_id)
            if tag == "DateTime":
                data = exifdata.get(tag_id)
                if isinstance(data, bytes):
                    data = data.decode()
#           print(f'\n[+] Метаданные файла: {os.path.split(file)[-1]}\n')
        return data
    except UnboundLocalError:
        data = "1970-01-01"
        return data


def vid_aud_metadata(patn_f):
    try:
 #       print(f'\n[+] Метаданные файла: {os.path.split(patn_f)[-1]}\n')
        return ffmpeg.probe(patn_f)["streams"]
    except ffmpeg._run.Error:
        print('[-] Неподдерживаемый формат')
        return 1


def compute_checksums(file_path):
    hash_sha256 = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()
    except Exception as error:
        print (f"File {file_path} open Error: {error} ")

def find_copy(dictionary, key, value):
    if key not in dictionary:
        dictionary[key] = value
        copy = False
        return dictionary, copy
    else:
        dictionary[key] = dictionary.get(key, []) + "$" + value
        copy = True
        return dictionary, copy


def save_result(dictionary, file_save):
    with open(file_save, "w", encoding='utf-8') as file:
        for key, value in dictionary.items():
            if "$" in value:
                new_value = value.replace("$", "||") + "\n"
                file.write(new_value)
                print(new_value)



def make_list_copy():
    dictionary = {}
    file_save= os.path.join(path_result, "Copies.txt")
    for root, dirs, files in os.walk(path_check):
        for name in files:
            file_test = os.path.join(root, name)
            hash_sha256 = compute_checksums(file_test)
            dictionary, copy = find_copy(dictionary, hash_sha256, file_test)
    save_result(dictionary, file_save)
    exit(0)


def sort_media():
    list_file = {}
    for root, _, files in os.walk(path_result):
        for file in files:
            file_test = os.path.join(root, file)
            hash_file = compute_checksums(file_test)
            if hash_file not in list_file:
                list_file[hash_file] = file_test
    for root, dirs, files in os.walk(path_check):
        for name in files:
            file_new = os.path.join(root, name)
            basename, extension = os.path.splitext(name)
            hash_file_new = compute_checksums(file_new)
            if hash_file_new in list_file:
                print(f"Файл {name} уже есть, пропускаем!")
                continue
            if extension == ".jpg" or extension == ".JPG" or extension == ".jpeg":
                meta_date_jpg = image_meta(file_new).split()[0]
                path_too = os.path.join(path_result, meta_date_jpg[0:4], meta_date_jpg[5:7])
                os.makedirs(path_too, exist_ok=True)
                shutil.copy2(file_new, path_too)
 #               os.remove(file_new)
                print(f"Name: {name} - Date: {meta_date_jpg} - To_path: {path_too}")

            else:
                meta_date_mov = vid_aud_metadata(file_new)
                if meta_date_mov != 1:
                    try:
                        meta_date_mov = vid_aud_metadata(file_new)[0]["tags"]['creation_time'].split("T")[0]
                    except:
                        print(f"Файл {file_new} - пропущен!")
                        continue
                    path_too_mov = os.path.join(path_result, meta_date_mov[0:4], meta_date_mov[5:7])
                    os.makedirs(path_too_mov, exist_ok=True)
                    shutil.copy2(file_new, path_too_mov)
 #                   os.remove(file_new)
                    print(f"Name: {name} - Date: {meta_date_mov} - To_path: {path_too_mov}")
                else:
                    print(f"Файл {file_new} - пропущен!")
                    continue
    return 0


def remove_copies():
    file_copies = os.path.join(path_check, "Copies.txt")
    file = open(file_copies, "r", encoding='utf-8')
    while True:
        content = file.readline()
        if not content:
            break
        file_list = content.split("||")
        i = 0
        for path in file_list:
            print (i, " ", path)
            i += 1
        j = 0
        num_save = input("Введите номер для сохранения, n - НЕ Удалять, или r - Удалить ВСЕ: ").lower()
        if num_save == "n":
            print(f"Все копии файлов: \n {file_list} \n будут сохранены!")
            continue
        elif num_save == "r":
            confirm = input("УДАЛЯЕМ ?").lower()
            if confirm != "y":
                continue
            else:
                num_save = 111
        if int(num_save) != 111:
            print(f"Файл {num_save} будет сохранен")
        else:
            print(f"Файл {file_list} \n УДАЛЕНЫ")

        for del_file in file_list:
            if j != int(num_save):
                del_file = del_file.strip("\n")
                del_file.startswith('"')
                del_file.endswith('"')
                os.remove(del_file)
                j += 1
                continue
            j += 1
    file.close()


if __name__ == "__main__":

    mode = slect_mode()
    if mode == "Search for copies":
        path_check = select_directory()
        path_result = select_directory()
        if os.path.isdir(path_check) and os.path.isdir(path_result):
            make_list_copy()
        else:
            print(f"Неверный путь {path_check} или {path_result}")
            exit(1)

    elif mode == "Sort media":
        path_check = select_directory()
        path_result = select_directory()
        if os.path.isdir(path_check) and os.path.isdir(path_result):
            sort_media()
        else:
            print(f"Неверный путь {path_check} или {path_result}")
            exit(1)

    elif mode == "Delete copies":
        path_check = select_directory()
        if os.path.isfile(os.path.join(path_check, "Copies.txt")):
             remove_copies()
        else:
            print(f"Неверный путь {path_check} или файл Copies.txt не найден.")
            exit(1)



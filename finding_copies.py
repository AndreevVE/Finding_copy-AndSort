import hashlib
import os
import sys
from PIL import Image
from PIL.ExifTags import TAGS
import ffmpeg
import shutil


def image_meta(file):
    try:
        image = Image.open(file)
        # извлечь данные EXIF
        exifdata = image.getexif()
        # перебор всех полей данных EXIF
        for tag_id in exifdata:
        # получить имя тега вместо нечитаемого идентификатора
            tag = TAGS.get(tag_id, tag_id)
            if tag == "DateTime":
                data = exifdata.get(tag_id)
            # декодировать байты
                if isinstance(data, bytes):
                    data = data.decode()
        #                print(f"{tag:25}:% {data}")
#        print(f'\n[+] Метаданные файла: {os.path.split(file)[-1]}\n')
        return data
    except UnboundLocalError:
        data = "1970-01-01"
        return data


def vid_aud_matadata(patn_f):
    try:
#        print(f'\n[+] Метаданные файла: {os.path.split(patn_f)[-1]}\n')
        return ffmpeg.probe(patn_f)["streams"]
    except ffmpeg._run.Error:
        print('[-] Неподдерживаемый формат')
        return 1


def compute_checksums(file_path):
    hash_sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_sha256.update(chunk)

    return hash_sha256.hexdigest()


def find_copy(dictionary, key, value):
    if key not in dictionary:
        dictionary[key] = value
        copy = False
        return dictionary, copy
    else:
        dictionary[key] = dictionary.get(key, []) + " $ " + value
        copy = True
        return dictionary, copy


def save_result(dictionary, file_save):
    with open(file_save, "w", encoding='utf-8') as file:
        for key, value in dictionary.items():
            if "$" in value:
                new_value = value.replace("$", "") + "\n"
                file.write(new_value)
                print(new_value)
                file.write("====================================\n")


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
                meta_date_mov = vid_aud_matadata(file_new)
                if meta_date_mov != 1:
                    try:
                        meta_date_mov = vid_aud_matadata(file_new)[0]["tags"]['creation_time'].split("T")[0]
                    except:
                        print(f"Файл {file_new} - пропущен!")
                        continue
                    path_too_mov = os.path.join(path_result, meta_date_mov[0:4], meta_date_mov[5:7])
                    os.makedirs(path_too_mov, exist_ok=True)
                    shutil.copy2(file_new, path_too_mov)
#                    os.remove(file_new)
                    print(f"Name: {name} - Date: {meta_date_mov} - To_path: {path_too_mov}")
                else:
                    print(f"Файл {file_new} - пропущен!")
                    continue
    return 0


if __name__ == "__main__":
    if len(sys.argv) == 1:
        print ("Введите -c для поиска копий или -r для удаления копий и сортировки")
        print ("Затем путь для поиска файлов и путь для сохранения результата.")
    else:
        path_check = sys.argv[2]
        path_result = sys.argv[3]
        if sys.argv[1] == "-c":
            make_list_copy()
        elif sys.argv[1] == "-s":
            sort_media()



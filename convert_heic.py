from PIL import Image, ImageFile
import os
import pillow_heif

ImageFile.LOAD_TRUNCATED_IMAGES = True
pillow_heif.register_heif_opener()
images_list = os.listdir('./HEIC')
if not os.path.exists('./JPG'):
    os.mkdir('./JPG')
count = len(images_list)
progress = 0
for image in images_list:
    if image.endswith('.heic'):
        img = Image.open('./HEIC/' + image)
        img.save('./JPG/' + image[:-5] + '.jpg', format='JPEG',quality=100, optimize=True, progressive=True)
        progress += 1
        print(f'Converting {progress}/{count} images')

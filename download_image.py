import requests
import argparse
import multiprocessing
import math
import os


# Parser things
parser = argparse.ArgumentParser(description='Download Image from Website/Storage Link')
parser.add_argument('url', type=str, help='Specify link/url where the image is stored')
parser.add_argument('--p', type=int, help='Number of images if multiple images exist')
parser.add_argument('--ps', type=int, help='Page start')
parser.add_argument('--pe', type=int, help='Page end')
parser.add_argument('--ifor', type=str, help='Image format (jpg/png/jpeg/etc). Default: jpg')
parser.add_argument('--tf', type=str, help='Specify folder in which the downloaded image will be saved to. Default: current working directory')
parser.add_argument('--force', type=str, help="Specify whether to overwrite the image if it's already exists or not in the current working directory. If you want to force then the options are either string of: true, 1, or yes")

args = parser.parse_args()

main_image_url = args.url
pages = args.p
page_start = args.ps
page_end = args.pe
image_format = args.ifor
target_folder = args.tf


# Set default image format to jpg
if args.ifor == None:
    image_format = 'jpg'

# Set pages if not specified and the task is downloading multiple images
if args.p == None and main_image_url[-1] == "/":
    pages = page_end - page_start

# Set force/overwrite argument
if str(args.force).lower() in ["true", "1", "yes"]:
    force = True
else:
    force = False

# Function to download image/images
def download_image(pages_range):
    if pages_range is not None:
        assert type(pages_range) is list
        for page in pages_range:
            filename = f'{page}'.zfill(3)+f'.{image_format}'
            image_url = main_image_url+f'{page}.{image_format}'
            
            # check whether the file is already exists or not
            if not force:
                if os.path.exists(filename):
                    print("Image", filename, "already exists. Skip downloading from", image_url, f"({multiprocessing.current_process().name})")
                    continue
            
            print(multiprocessing.current_process().name, '- downloading image from:', image_url)
            img_data = requests.get(image_url).content

            with open(filename, 'wb') as handler:
                handler.write(img_data)
    else:
        # if the image is just one and then the image format is specified from the url
        image_url = main_image_url
        filename = image_url.split('/')[-1]
        
        # check whether the file is already exists or not
        if not force:
            if os.path.exists(filename): # note: zfill deliberately not specified
                print("Image", filename, "already exists. Skip downloading from", image_url)
                return
            
        print('Downloading image from:', image_url)
        img_data = requests.get(image_url).content
        with open(f'{filename}', 'wb') as handler:
            handler.write(img_data)


if __name__ == '__main__':
    # Set workdir if the target folder is specified to save the images
    if target_folder is not None:
        if not os.path.isdir(target_folder):
            os.mkdir(target_folder)
        os.chdir(target_folder)
        print("Working Directory:", target_folder)
        
    # Main task
    if pages is not None:
        # If the number of pages is more than one then distribute the process
        # Multiprocessing things
        cpus = multiprocessing.cpu_count()
        if page_start != None:
            assert page_start > 0
            if page_end != None:
                pages_list = [page for page in range(page_start-1, page_end+1)]
            else:
                pages_list = [page for page in range(page_start-1, pages+1)]
        else:
            pages_list = [page for page in range(0, pages+1)]
        pages_per_chunks = math.ceil(pages/cpus)
        pages_chunks = [pages_list[x:x+pages_per_chunks] for x in range(1, pages+1, pages_per_chunks)]

        procs = []
        for pages_chunk in pages_chunks:
            proc = multiprocessing.Process(target=download_image, args=(pages_chunk, ))
            procs.append(proc)
            proc.start()
            
        for proc in procs:
            proc.join()
    
    else:
        # If only one image is downloaded
        download_image(pages_range=None)
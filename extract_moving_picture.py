import os
import sys, getopt


# 修改后的extract函数（新增output_path参数）
def extract(filename, extractImage, output_path=None):
    if output_path is None:
        output_path = os.path.dirname(filename)

    with open(filename, "rb") as binary_file:
        name = os.path.splitext(os.path.basename(binary_file.name))[0]
        binary_file.seek(0, os.SEEK_END)
        num_bytes = binary_file.tell()

        jpg_found = False
        for i in range(num_bytes):
            binary_file.seek(i)

            if extractImage and not jpg_found:
                jpg_end_bytes = binary_file.read(4)
                if jpg_end_bytes == b"\xFF\xD9\x00\x00":
                    binary_file.seek(0)
                    jpg_data = binary_file.read(i + 4)
                    output_name = os.path.join(output_path, f"{name}_i.jpg")
                    with open(output_name, "wb") as outfile:
                        outfile.write(jpg_data)
                    jpg_found = True

            else:
                mp4_start_bytes = binary_file.read(16)
                if mp4_start_bytes == b"\x00\x00\x00\x18\x66\x74\x79\x70\x6D\x70\x34\x32\x00\x00\x00\x00":
                    binary_file.seek(i)
                    mp4_data = binary_file.read(num_bytes - i)
                    output_name = os.path.join(output_path, f"{name}.mp4")
                    with open(output_name, "wb") as outfile:
                        outfile.write(mp4_data)
                    break

def usage():
    print('extract_moving_picture.py -i <文件>')
    print('extract_moving_picture.py -f <文件夹>\n')
    print('extract_moving_picture.py -i <文件> -e')
    print('extract_moving_picture.py -f <文件夹> -e\n')
    print('当附加 -e 参数时会同时提取原始图片')

if __name__ == "__main__":
    print("华为动态图片/Momente提取器\n")
    if sys.version_info[0] < 3:
        print("此脚本需要 Python 3 环境")
        sys.exit(-1)
    filename = None
    extractImage = False
    isFolder = False
    try:
        opts, args = getopt.getopt(sys.argv[1:],"hi:f:e",["ifile=, folder="])
    except getopt.GetoptError:
        usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            usage()
            sys.exit()
        elif opt in ("-i", "--ifile"):
            filename = arg
        elif opt in ("-f", "--folder"):
            filename = arg
            isFolder = True
        elif opt == "-e":
            extractImage = True
    if filename is None:
        usage()
        sys.exit(2)
    if not isFolder:
        print('从文件 "%s" 提取MP4' %(filename))
        extract(filename, extractImage)
    else:
        foldername = os.path.join(os.path.abspath("."), filename)
        print('从文件夹 "%s" 提取MP4' %(foldername))
        for root, dirs, files in os.walk(foldername):
            for file_ in files:
                filename = os.path.join(root, file_)
                print('从文件 "%s" 提取MP4' %(filename))
                extract(filename, extractImage)
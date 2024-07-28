import os
import shutil
import pickle
import time
import threading
import keyboard
import winsound
from colorama import init, Fore, Style

# 初始化 colorama
init()

data_file = 'game_data.pkl'

def load_data():
    if os.path.exists(data_file):
        with open(data_file, 'rb') as f:
            return pickle.load(f)
    return {}

def save_data(data):
    with open(data_file, 'wb') as f:
        pickle.dump(data, f)

def create_save_dir(base_dir, save_id):
    save_dir = os.path.join(base_dir, f'Save_{save_id}')
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    return save_dir

def list_save_dirs(base_dir):
    return sorted([d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d)) and d.startswith('Save_') and d != 'Save_0'], key=lambda x: int(x.split('_')[1]))

def get_next_save_id(base_dir):
    existing_saves = list_save_dirs(base_dir)
    if not existing_saves:
        return 1
    max_id = max([int(d.split('_')[1]) for d in existing_saves])
    return max_id + 1

def delete_and_renumber(base_dir, save_id):
    shutil.rmtree(os.path.join(base_dir, f'Save_{save_id}'))
    saves = list_save_dirs(base_dir)
    for i, save in enumerate(saves):
        new_name = f'Save_{i + 1}'
        os.rename(os.path.join(base_dir, save), os.path.join(base_dir, new_name))

def load_save(game_dir, base_dir, save_id):
    save_dir = os.path.join(base_dir, f'Save_{save_id}')
    save_0_dir = create_save_dir(base_dir, 0)

    # 清空 Save_0 目录
    for file in os.listdir(save_0_dir):
        file_path = os.path.join(save_0_dir, file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except PermissionError:
            print(f"权限错误: 无法删除 {file_path}")

    # 移动游戏目录中的所有文件到 Save_0
    for file in os.listdir(game_dir):
        src_path = os.path.join(game_dir, file)
        dst_path = os.path.join(save_0_dir, file)
        try:
            shutil.move(src_path, dst_path)
        except PermissionError:
            print(f"权限错误: 无法移动 {src_path}")

    # 复制指定保存目录中的所有文件到游戏目录
    for file in os.listdir(save_dir):
        src_path = os.path.join(save_dir, file)
        dst_path = os.path.join(game_dir, file)
        try:
            if os.path.isdir(src_path):
                shutil.copytree(src_path, dst_path, dirs_exist_ok=True)
            else:
                shutil.copy(src_path, dst_path)
        except PermissionError:
            print(f"权限错误: 无法复制 {src_path}")

def store_save(game_dir, base_dir, save_id):
    save_dir = os.path.join(base_dir, f'Save_{save_id}')

    # 清空指定保存目录
    for file in os.listdir(save_dir):
        file_path = os.path.join(save_dir, file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except PermissionError:
            print(f"权限错误: 无法删除 {file_path}")

    # 复制游戏目录中的所有文件到指定保存目录
    for file in os.listdir(game_dir):
        src_path = os.path.join(game_dir, file)
        dst_path = os.path.join(save_dir, file)
        try:
            if os.path.isdir(src_path):
                shutil.copytree(src_path, dst_path, dirs_exist_ok=True)
            else:
                shutil.copy(src_path, dst_path)
        except PermissionError:
            print(f"权限错误: 无法复制 {src_path}")

def autosave(game_dir, base_dir, stop_event):
    while not stop_event.is_set():
        store_save(game_dir, base_dir, 0)
        print("自动保存到 Save_0")
        for _ in range(30):
            if stop_event.is_set():
                break
            time.sleep(1)

def quick_save(game_dir, save_dir, stop_event):
    while not stop_event.is_set():
        if keyboard.is_pressed('F5'):
            winsound.MessageBeep(winsound.MB_OK)  # 播放音效
            store_save(game_dir, save_dir, 0)
            print("快速保存到 Save_0")
        if keyboard.is_pressed('F8'):
            winsound.MessageBeep(winsound.MB_ICONHAND)  # 播放音效
            for file in os.listdir(game_dir):
                file_path = os.path.join(game_dir, file)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                except PermissionError:
                    print(f"权限错误: 无法删除 {file_path}")
            save_0_dir = os.path.join(save_dir, 'Save_0')
            for file in os.listdir(save_0_dir):
                src_path = os.path.join(save_0_dir, file)
                dst_path = os.path.join(game_dir, file)
                try:
                    if os.path.isdir(src_path):
                        shutil.copytree(src_path, dst_path, dirs_exist_ok=True)
                    else:
                        shutil.copy(src_path, dst_path)
                except PermissionError:
                    print(f"权限错误: 无法复制 {src_path}")
            print("快速回溯到 Save_0")
        if keyboard.is_pressed('F1'):
            winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)  # 播放音效
            print("退出快速保存模式")
            break
        time.sleep(1)

def print_menu(header, options):
    print(f"{Fore.RED}=================={Style.RESET_ALL}")
    print(f"{Fore.GREEN}{header}{Style.RESET_ALL}")
    print(f"{Fore.RED}=================={Style.RESET_ALL}")
    for option in options:
        print(f"{Fore.CYAN}{option}{Style.RESET_ALL}")
    print(f"{Fore.RED}=================={Style.RESET_ALL}")

def main():
    data = load_data()
    stop_event = threading.Event()
    autosave_thread = None

    while True:
        print_menu("主页", [
            "1. 添加游戏",
            "2. 选择游戏",
            "3. 删除游戏",
            "4. 显示所有游戏",
            "5. 退出"
        ])
        choice = input("请选择操作: ")

        if choice == '1':
            game_name = input("输入游戏名称: ")
            game_dir = input("输入游戏目录路径: ")
            save_dir = input("输入总存档目录路径: ")
            data[game_name] = {
                'game_dir': game_dir,
                'save_dir': save_dir,
            }
            create_save_dir(save_dir, 0)
            save_data(data)
        elif choice == '2':
            game_name = input("输入游戏名称: ")
            if game_name in data:
                game_dir = data[game_name]['game_dir']
                save_dir = data[game_name]['save_dir']
                while True:
                    print_menu(f"主页{Fore.YELLOW}》{Style.RESET_ALL}{Fore.GREEN}{game_name}{Style.RESET_ALL}", [
                        "1. 查看所有保存",
                        "2. 添加保存",
                        "3. 删除保存",
                        "4. 读取保存",
                        "5. 存储保存",
                        "6. 回溯",
                        "7. 启用自动保存",
                        "8. 快速保存",
                        "9. 返回"
                    ])
                    choice = input("请选择操作: ")
                    
                    if choice == '1':
                        saves = list_save_dirs(save_dir)
                        print(f"当前所有保存: {', '.join(saves)}")
                    elif choice == '2':
                        save_id = get_next_save_id(save_dir)
                        create_save_dir(save_dir, save_id)
                        print(f"已添加保存: Save_{save_id}")
                    elif choice == '3':
                        save_id = input("输入要删除的保存编号: ")
                        if save_id.isdigit():
                            confirmation = input(f"{Fore.RED}确定要删除保存 Save_{save_id} 吗? (y/n): {Style.RESET_ALL}")
                            if confirmation.lower() == 'y':
                                delete_and_renumber(save_dir, int(save_id))
                                print(f"保存 Save_{save_id} 已删除并重新编号")
                    elif choice == '4':
                        save_id = input("输入要读取的保存编号: ")
                        if save_id.isdigit():
                            if f'Save_{save_id}' in list_save_dirs(save_dir):
                                confirmation = input(f"{Fore.RED}确定要读取保存 Save_{save_id} 吗? (y/n): {Style.RESET_ALL}")
                                if confirmation.lower() == 'y':
                                    load_save(game_dir, save_dir, int(save_id))
                                    print(f"保存 Save_{save_id} 已读取")
                            else:
                                print("错误: 保存不存在")
                        else:
                            print("错误: 输入无效")
                    elif choice == '5':
                        save_id = input("输入要存储的保存编号: ")
                        if save_id.isdigit():
                            if f'Save_{save_id}' in list_save_dirs(save_dir):
                                confirmation = input(f"{Fore.RED}确定要存储保存 Save_{save_id} 吗? (y/n): {Style.RESET_ALL}")
                                if confirmation.lower() == 'y':
                                    store_save(game_dir, save_dir, int(save_id))
                                    print(f"保存 Save_{save_id} 已存储")
                            else:
                                print("错误: 保存不存在")
                        else:
                            print("错误: 输入无效")
                    elif choice == '6':
                        confirmation = input("确定要进行回溯吗? (y/n): ")
                        if confirmation.lower() == 'y':
                            for file in os.listdir(game_dir):
                                file_path = os.path.join(game_dir, file)
                                try:
                                    if os.path.isfile(file_path):
                                        os.unlink(file_path)
                                    elif os.path.isdir(file_path):
                                        shutil.rmtree(file_path)
                                except PermissionError:
                                    print(f"权限错误: 无法删除 {file_path}")
                            save_0_dir = os.path.join(save_dir, 'Save_0')
                            for file in os.listdir(save_0_dir):
                                src_path = os.path.join(save_0_dir, file)
                                dst_path = os.path.join(game_dir, file)
                                try:
                                    if os.path.isdir(src_path):
                                        shutil.copytree(src_path, dst_path, dirs_exist_ok=True)
                                    else:
                                        shutil.copy(src_path, dst_path)
                                except PermissionError:
                                    print(f"权限错误: 无法复制 {src_path}")
                            print("游戏已回溯到 Save_0")
                    elif choice == '7':
                        if autosave_thread is None or not autosave_thread.is_alive():
                            stop_event.clear()
                            autosave_thread = threading.Thread(target=autosave, args=(game_dir, save_dir, stop_event))
                            autosave_thread.start()
                            print("自动保存已启动")
                            while True:
                                print_menu(f"主页{Fore.YELLOW}》{Style.RESET_ALL}{Fore.GREEN}{game_name}{Style.RESET_ALL}{Fore.YELLOW}》自动保存{Style.RESET_ALL}", [
                                    "1. 回溯",
                                    "2. 停止自动保存"
                                ])
                                sub_choice = input("请选择操作: ")
                                if sub_choice == '1':
                                    confirmation = input("确定要进行回溯吗? (y/n): ")
                                    if confirmation.lower() == 'y':
                                        for file in os.listdir(game_dir):
                                            file_path = os.path.join(game_dir, file)
                                            try:
                                                if os.path.isfile(file_path):
                                                    os.unlink(file_path)
                                                elif os.path.isdir(file_path):
                                                    shutil.rmtree(file_path)
                                            except PermissionError:
                                                print(f"权限错误: 无法删除 {file_path}")
                                        save_0_dir = os.path.join(save_dir, 'Save_0')
                                        for file in os.listdir(save_0_dir):
                                            src_path = os.path.join(save_0_dir, file)
                                            dst_path = os.path.join(game_dir, file)
                                            try:
                                                if os.path.isdir(src_path):
                                                    shutil.copytree(src_path, dst_path, dirs_exist_ok=True)
                                                else:
                                                    shutil.copy(src_path, dst_path)
                                            except PermissionError:
                                                print(f"权限错误: 无法复制 {src_path}")
                                        print("游戏已回溯到 Save_0")
                                elif sub_choice == '2':
                                    stop_event.set()
                                    autosave_thread.join()
                                    print("自动保存已停止")
                                    save_id = input("输入要存储的保存编号: ")
                                    if save_id.isdigit():
                                        if f'Save_{save_id}' in list_save_dirs(save_dir):
                                            confirmation = input(f"{Fore.RED}确定要存储保存 Save_{save_id} 吗? (y/n): {Style.RESET_ALL}")
                                            if confirmation.lower() == 'y':
                                                store_save(game_dir, save_dir, int(save_id))
                                                print(f"保存 Save_{save_id} 已存储")
                                            break
                                        else:
                                            print("错误: 保存不存在")
                                    else:
                                        print("错误: 输入无效")
                                else:
                                    print("错误: 输入无效")
                        else:
                            print("错误: 自动保存已在进行")
                    elif choice == '8':
                        stop_event.clear()
                        quicksave_thread = threading.Thread(target=quick_save, args=(game_dir, save_dir, stop_event))
                        quicksave_thread.start()
                        print("快速保存模式已启动")
                        quicksave_thread.join()
                    elif choice == '9':
                        if autosave_thread is not None and autosave_thread.is_alive():
                            stop_event.set()
                            autosave_thread.join()
                            print("自动保存已停止")
                        break
            else:
                print("游戏不存在")
        elif choice == '3':
            game_name = input("输入要删除的游戏名称: ")
            if game_name in data:
                confirmation = input(f"确定要删除游戏 {game_name} 吗? (y/n): ")
                if confirmation.lower() == 'y':
                    del data[game_name]
                    save_data(data)
                    print(f"游戏 {game_name} 已删除")
            else:
                print("游戏不存在")
        elif choice == '4':
            print(f"{Fore.RED}=================={Style.RESET_ALL}")
            print("所有游戏及目录:")
            print(f"{Fore.RED}=================={Style.RESET_ALL}")
            for game, paths in data.items():
                print(f"{Fore.GREEN}{game}{Style.RESET_ALL}: 游戏目录->{paths['game_dir']}, 总存档目录->{paths['save_dir']}")
            print(f"{Fore.RED}=================={Style.RESET_ALL}")
        elif choice == '5':
            confirmation = input("确定要退出吗? (y/n): ")
            if confirmation.lower() == 'y':
                save_data(data)
                if autosave_thread is not None and autosave_thread.is_alive():
                    stop_event.set()
                    autosave_thread.join()
                    print("自动保存已停止")
                break
        else:
            print("错误: 输入无效")

if __name__ == "__main__":
    main()

# 用于对opt资源包中的信息进行快速提取
# Used for quick extraction of information in the opt resource package.
# - Kyoku 2024.03
import asyncio
import json
import os.path
import sys
import time
import xml.etree.ElementTree as et

# 全局变量
opt_name = None


async def get_file_by_path_n_name(path, file_name):
    # 初始化存储path的列表
    path_list = []
    # 从目录下找到所有文件
    for filepath, dirname, filename in os.walk(path):
        if not filename == [] and 'Sort.xml' not in str(filename):
            path = os.path.join(filepath, file_name)
            path_list.append(path)
    # 返回获取的数据文件列表
    return path_list


async def save_to_json(json_name, dic):
    with open(f'{json_name}-{opt_name}.json', 'w+', encoding='utf-8') as j:
        j.write(json.dumps(dic, indent=4, ensure_ascii=False))
        j.close()


async def challenge_parse(path):
    xml_list = await get_file_by_path_n_name(path, 'Challenge.xml')
    dics = []
    for xmlfile in xml_list:
        root = et.parse(xmlfile).getroot()
        # 获取解限信息
        relax_data = root.find('Relax')
        all_relaxs = relax_data.findall('ChallengeRelax')
        relax_dics = []
        for relax in all_relaxs:
            relax_dic = {
                "passDays": int(relax.find('Day').text),
                "lifeLimit": int(relax.find('Life').text),
                "difficult": int(relax.find('ReleaseDiff').find('id').text)
            }
            relax_dics.append(relax_dic)
        # 生成字典
        dic = {
            "challengeId": int(root.find('name').find('id').text),
            "challengeName": root.find('name').find('str').text,
            "music": {
                "musicId": int(root.find('Music').find('id').text),
                "musicName": root.find('Music').find('str').text
            },
            "event": {
                "eventId": int(root.find('EventName'). find('id').text),
                "eventName": root.find('EventName').find('str').text
            },
            "relaxData": relax_dics
        }
        dics.append(dic)
    await save_to_json('challenge', dics)


async def chara_parse(path):
    xml_list = await get_file_by_path_n_name(path, 'Chara.xml')
    dics = []
    for xmlfile in xml_list:
        root = et.parse(xmlfile).getroot()
        # 构建字典
        dic = {
            "charaId": int(root.find('name').find('id').text),
            "charaName": root.find('name').find('str').text,
            "colorId": int(root.find('color').find('id').text),
            "colorName": root.find('color').find('str').text,
            "areaId": int(root.find('genre').find('id').text),
            "isDisabled": root.find('disable').text
        }
        dics.append(dic)
    await save_to_json('chara', dics)


async def run_tasks(tasks):
    # 用gather进行伪并发处理
    await asyncio.gather(*tasks)

if __name__ == '__main__':
    # 检测传入的路径是否合理
    try:
        file_root = sys.argv[1]
        opt_name = os.path.basename(os.path.dirname(file_root))

        print('---')
        print('Got the OPT FOLDER PATH: ' + file_root)
    except IndexError as e:
        print('You need to send the OPT FOLDER PATH with this script!')
        sys.exit()

    # 传入路径后检测是否包含指定的文件夹，如包含则在运行列表中加入对应的抽取函数
    task_list = []

    if os.path.exists(f'{file_root}/challenge'):
        print('Find challenge dir!')
        task_list.append(challenge_parse(f'{file_root}/challenge'))
    if os.path.exists(f'{file_root}/chara'):
        print('Find chara dir!')
        task_list.append(chara_parse(f'{file_root}/chara'))

    # 获取当前的时间（开始时间）
    start_time = time.time()

    # 使用asyncio来进行异步并发执行，提升脚本的处理效率
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_tasks(task_list))

    # 获取当前的时间（结束时间）
    end_time = time.time()

    # 计算并输出总的执行时间
    total_time = end_time - start_time
    print(f'Total time spent: {total_time} s\n===')

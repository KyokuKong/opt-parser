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
str_to_bool = {'true': True, 'false': False}


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
    with open(f'{opt_name}-{json_name}.json', 'w+', encoding='utf-8') as j:
        j.write(json.dumps(dic, indent=4, ensure_ascii=False))
        j.close()


def rgb_to_hex(r, g, b):
    r = int(r)
    g = int(g)
    b = int(b)
    return "#{:02X}{:02X}{:02X}".format(r, g, b)


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
                "eventId": int(root.find('EventName').find('id').text),
                "eventName": root.find('EventName').find('str').text
            },
            "relaxData": relax_dics
        }
        dics.append(dic)
    await save_to_json('Challenge', dics)


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
            "genreId": int(root.find('genre').find('id').text),
            "isDisabled": str_to_bool[root.find('disable').text]
        }
        dics.append(dic)
    await save_to_json('Chara', dics)


async def chara_genre_parse(path):
    xml_list = await get_file_by_path_n_name(path, 'CharaGenre.xml')
    dics = []
    for xmlfile in xml_list:
        root = et.parse(xmlfile).getroot()
        # 构建字典
        dic = {
            "charaGenreId": int(root.find('name').find('id').text),
            "charaGenreName": root.find('name').find('str').text,
            "charaGenreNameCN": root.find('genreName').text,
            "color": rgb_to_hex(root.find('Color').find('R').text,
                                root.find('Color').find('G').text,
                                root.find('Color').find('B').text),
            "resourceName": root.find('FileName').text,
            "isDisabled": str_to_bool[root.find('disable').text]
        }
        dics.append(dic)
    await save_to_json('CharaGenre', dics)


async def collection_genre_parse(path):
    xml_list = await get_file_by_path_n_name(path, 'CollectionGenre.xml')
    dics = []
    for xmlfile in xml_list:
        root = et.parse(xmlfile).getroot()
        # 构建字典
        dic = {
            "collectionGenreId": int(root.find('name').find('id').text),
            "collectionGenreName": root.find('name').find('str').text,
            "collectionGenreNameCN": root.find('genreName').text,
            "color": rgb_to_hex(root.find('Color').find('R').text,
                                root.find('Color').find('G').text,
                                root.find('Color').find('B').text),
            "resourceName": root.find('FileName').text,
            "isDisabled": str_to_bool[root.find('disable').text]
        }
        dics.append(dic)
    await save_to_json('CollectionGenre', dics)


async def course_parse(path):
    xml_list = await get_file_by_path_n_name(path, 'Course.xml')
    dics = []
    for xmlfile in xml_list:
        root = et.parse(xmlfile).getroot()
        is_random = str_to_bool[root.find('isRandom').text]
        # 获取课题曲信息
        music_data = root.find('courseMusicData')
        all_musics = music_data.findall('CourseMusicData')
        music_dics = []
        for music in all_musics:
            music_dic = {
                "musicId": int(music.find('musicId').find('id').text),
                "musicName": music.find('musicId').find('str').text,
                "difficulty": int(music.find('difficulty').find('id').text)
            }
            music_dics.append(music_dic)
        # 构建字典
        dic = {
            "courseId": int(root.find('name').find('id').text),
            "cureseName": root.find('name').find('str').text,
            "courseMode": int(root.find('courseMode').find('id').text),
            "baseDaniId": int(root.find('baseDaniId').find('id').text),
            "baseDaniName": root.find('baseDaniId').find('str').text,
            "baseCourseId": int(root.find('baseCourseId').find('id').text),
            "baseCourseName": root.find('baseCourseId').find('str').text,
            "eventId": int(root.find('eventId').find('id').text),
            "eventName": root.find('eventId').find('str').text,
            "courseInfo": {
                "isRandom": is_random,
                "maxLevel": int(root.find('upperLevel').text),
                "minLevel": int(root.find('lowerLevel').text),
                "isLock": str_to_bool[root.find('isLock').text],
                "life": int(root.find('life').text),
                "recover": int(root.find('recover').text),
                "perfectDamage": int(root.find('perfectDamage').text),
                "greatDamage": int(root.find('greatDamage').text),
                "goodDamage": int(root.find('goodDamage').text),
                "missDamage": int(root.find('missDamage').text),
            },
            "courseMusic": music_dics if not is_random else []
        }
        dics.append(dic)
    await save_to_json('Course', dics)


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
    if os.path.exists(f'{file_root}/charaGenre'):
        print('Find chareGenre dir!')
        task_list.append(chara_genre_parse(f'{file_root}/charaGenre'))
    if os.path.exists(f'{file_root}/collectionGenre'):
        print('Find collectionGenre dir!')
        task_list.append(collection_genre_parse(f'{file_root}/collectionGenre'))
    if os.path.exists(f'{file_root}/course'):
        print('Find course dir!')
        task_list.append(course_parse(f'{file_root}/course'))

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

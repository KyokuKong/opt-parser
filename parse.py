# 用于对opt资源包中的信息进行快速提取
# Used for quick extraction of information in the opt resource package.
# - Kyoku 2024.03
import asyncio
import json
import re
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
        if 'music000000' not in filepath and 'music000001' not in filepath:
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


def ma2_reader(ma2_file):
    if os.path.exists(ma2_file):
        # 读取ma2文件
        with open(ma2_file, 'r') as f:
            ma2 = f.read()
            f.close()
        num_tap = int(next(iter(re.findall(r"T_NUM_TAP\s(\d+)", ma2)), '0'))
        # print(num_tap)
        num_break = int(next(iter(re.findall(r"T_NUM_BRK\s(\d+)", ma2)), '0'))
        # print(num_break)
        num_hold = int(next(iter(re.findall(r"T_NUM_HLD\s(\d+)", ma2)), '0'))
        # print(num_hold)
        num_slide = int(next(iter(re.findall(r"T_NUM_SLD\s(\d+)", ma2)), '0'))
        # print(num_slide)
        num_all = int(next(iter(re.findall(r"T_NUM_ALL\s(\d+)", ma2)), '0'))
        # print(num_all)
        # 传出获取到的值
        return num_tap, num_break, num_hold, num_slide, num_all


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


async def event_parse(path):
    xml_list = await get_file_by_path_n_name(path, 'Event.xml')
    dics = []
    for xmlfile in xml_list:
        root = et.parse(xmlfile).getroot()
        # 构建字典
        dic = {
            "eventId": int(root.find('name').find('id').text),
            "eventName": root.find('name').find('str').text,
            "infoType": int(root.find('infoType').text),
            "alwaysOpen": str_to_bool[root.find('alwaysOpen').text]
        }
        dics.append(dic)
    await save_to_json('Event', dics)


async def frame_parse(path):
    xml_list = await get_file_by_path_n_name(path, 'Frame.xml')
    dics = []
    for xmlfile in xml_list:
        root = et.parse(xmlfile).getroot()
        # 构建字典
        dic = {
            "frameId": int(root.find('name').find('id').text),
            "frameName": root.find('name').find('str').text,
            "frameInfo": {
                "releaseVersion": root.find('releaseTagName').find('str').text,
                "netOpen": root.find('netOpenName').find('str').text,
                "eventId": int(root.find('eventName').find('id').text),
                "collectionGenre": int(root.find('genre').find('id').text),
                "isDisabled": str_to_bool[root.find('disable').text],
                "isDefault": str_to_bool[root.find('isDefault').text],
                "isEffect": str_to_bool[root.find('isEffect').text],
                "dispCond": root.find('dispCond').text,
                "text": root.find('normText').text
            }
        }
        dics.append(dic)
    await save_to_json('Frame', dics)


async def icon_parse(path):
    xml_list = await get_file_by_path_n_name(path, 'Icon.xml')
    dics = []
    for xmlfile in xml_list:
        root = et.parse(xmlfile).getroot()
        # 构建字典
        dic = {
            "iconId": int(root.find('name').find('id').text),
            "iconName": root.find('name').find('str').text,
            "iconInfo": {
                "releaseVersion": root.find('releaseTagName').find('str').text,
                "netOpen": root.find('netOpenName').find('str').text,
                "eventId": int(root.find('eventName').find('id').text),
                "collectionGenre": int(root.find('genre').find('id').text),
                "isDisabled": str_to_bool[root.find('disable').text],
                "isDefault": str_to_bool[root.find('isDefault').text],
                "dispCond": root.find('dispCond').text,
                "text": root.find('normText').text
            }
        }
        dics.append(dic)
    await save_to_json('Icon', dics)


async def login_bonus_parse(path):
    xml_list = await get_file_by_path_n_name(path, 'LoginBonus.xml')
    dics = []
    for xmlfile in xml_list:
        root = et.parse(xmlfile).getroot()
        # 构建字典
        dic = {
            "loginBonusId": int(root.find('name').find('id').text),
            "loginBonusName": root.find('name').find('str').text,
            "itemId": int(root.find('itemID').text),
            "eventId": int(root.find('OpenEventId').find('id').text),
            "bonusType": root.find('BonusType').text,
            "bonusValue": {
                "partnerId": int(root.find('PartnerId').find('id').text),
                "partnerName": root.find('PartnerId').find('str').text,
                "characterId": int(root.find('CharacterId').find('id').text),
                "characterName": root.find('CharacterId').find('str').text,
                "musicId": int(root.find('MusicId').find('id').text),
                "musicName": root.find('MusicId').find('str').text,
                "titleId": int(root.find('TitleId').find('id').text),
                "titleName": root.find('TitleId').find('str').text,
                "plateId": int(root.find('PlateId').find('id').text),
                "plateName": root.find('PlateId').find('str').text,
                "iconId": int(root.find('IconId').find('id').text),
                "iconName": root.find('IconId').find('str').text,
                "frameId": int(root.find('FrameId').find('id').text),
                "frameName": root.find('FrameId').find('str').text,
                "ticketId": int(root.find('TicketId').find('id').text),
                "ticketName": root.find('TicketId').find('str').text,
            },
            "bonusInfo": {
                "maxPoint": int(root.find('maxPoint').text),
                "isRepeatGet": str_to_bool[root.find('IsRepeatGet').text],
                "isCollabo": str_to_bool[root.find('IsCollabo').text],
            }
        }
        dics.append(dic)
    await save_to_json('LoginBonus', dics)


async def map_parse(path):
    xml_list = await get_file_by_path_n_name(path, 'Map.xml')
    dics = []
    for xmlfile in xml_list:
        root = et.parse(xmlfile).getroot()
        map_details = []
        detail_data = root.find('TreasureExDatas')
        details = detail_data.findall('MapTreasureExData')
        for detail in details:
            map_detail = {
                "distance": int(detail.find('Distance').text),
                "flag": detail.find('Flag').text,
                "subParam1": int(detail.find('SubParam1').text),
                "subParam2": int(detail.find('SubParam2').text),
                "treasureId": int(detail.find('TreasureId').find('id').text),
                "treasureName": detail.find('TreasureId').find('str').text,
            }
            map_details.append(map_detail)
        # 构建字典
        dic = {
            "mapId": int(root.find('name').find('id').text),
            "mapName": root.find('name').find('str').text,
            "islandId": int(root.find('IslandId').find('id').text),
            "islandName": root.find('IslandId').find('str').text,
            "colorId": int(root.find('ColorId').find('id').text),
            "colorName": root.find('ColorId').find('str').text,
            "bonusMusicId": int(root.find('BonusMusicId').find('id').text),
            "bonusMusicName": root.find('BonusMusicId').find('str').text,
            "eventId": int(root.find('OpenEventId').find('id').text),
            "bonusMusicMagnification": int(root.find('BonusMusicMagnification').text),
            "mapInfo": {
                "isCollabo": str_to_bool[root.find('IsCollabo').text],
                "isInfinity": str_to_bool[root.find('IsInfinity').text],
            },
            "mapDetail": map_details
        }
        dics.append(dic)
    await save_to_json('Map', dics)


async def map_bonus_music_parse(path):
    xml_list = await get_file_by_path_n_name(path, 'MapBonusMusic.xml')
    dics = []
    for xmlfile in xml_list:
        root = et.parse(xmlfile).getroot()
        music_details = []
        music_data = root.find('MusicIds')
        details = music_data.find('list').findall('StringID')
        for detail in details:
            music_detail = {
                "musicId": int(detail.find('id').text),
                "musicName": detail.find('str').text,
            }
            music_details.append(music_detail)
        # 构建字典
        dic = {
            "mapBonusId": int(root.find('name').find('id').text),
            "mapBonusName": root.find('name').find('str').text,
            "musicList": music_details
        }
        dics.append(dic)
    await save_to_json('MapBonusMusic', dics)


async def map_color_parse(path):
    xml_list = await get_file_by_path_n_name(path, 'MapColor.xml')
    dics = []
    for xmlfile in xml_list:
        root = et.parse(xmlfile).getroot()
        # 构建字典
        dic = {
            "mapColorId": int(root.find('name').find('id').text),
            "mapColorName": root.find('name').find('str').text,
            "colorGroupId": int(root.find('ColorGroupId').find('id').text),
            "colorGroupName": root.find('ColorGroupId').find('str').text,
            "color": rgb_to_hex(root.find('Color').find('R').text,
                                root.find('Color').find('G').text,
                                root.find('Color').find('B').text),
            "colorDark": rgb_to_hex(root.find('ColorDark').find('R').text,
                                    root.find('ColorDark').find('G').text,
                                    root.find('ColorDark').find('B').text),
        }
        dics.append(dic)
    await save_to_json('MapColor', dics)


async def map_treasure_parse(path):
    xml_list = await get_file_by_path_n_name(path, 'MapTreasure.xml')
    dics = []
    for xmlfile in xml_list:
        root = et.parse(xmlfile).getroot()
        # 构建字典
        dic = {
            "treasureId": int(root.find('name').find('id').text),
            "treasureName": root.find('name').find('str').text,
            "treasureType": root.find('TreasureType').text,
            "treasureDetail": {
                "characterId": int(root.find('CharacterId').find('id').text),
                "characterName": root.find('CharacterId').find('str').text,
                "musicId": int(root.find('MusicId').find('id').text),
                "musicName": root.find('MusicId').find('str').text,
                "numeric": int(root.find('Numeric').text),
                "namePlateId": int(root.find('NamePlate').find('id').text),
                "namePlateName": root.find('NamePlate').find('str').text,
                "frameId": int(root.find('Frame').find('id').text),
                "frameName": root.find('Frame').find('str').text,
                "titleId": int(root.find('Title').find('id').text),
                "titleName": root.find('Title').find('str').text,
                "iconId": int(root.find('Icon').find('id').text),
                "iconName": root.find('Icon').find('str').text,
                "challengeId": int(root.find('Challenge').find('id').text),
                "challengeName": root.find('Challenge').find('str').text,
            }
        }
        dics.append(dic)
    await save_to_json('MapTreasure', dics)


async def music_parse(path):
    xml_list = await get_file_by_path_n_name(path, 'Music.xml')
    dics = []
    for xmlfile in xml_list:
        # 获取文件的目录
        ma2_dir = os.path.dirname(xmlfile)
        # 读取文件
        root = et.parse(xmlfile).getroot()
        # 获取谱面信息
        note_details = []
        notes_data = root.find('notesData')
        notes = notes_data.findall('Notes')
        for note in notes:
            if note.find('level').text != '0':
                ma2_file = os.path.join(ma2_dir, note.find('file').find('path').text)
                note_num = ma2_reader(ma2_file)
                note_detail = {
                    "level": int(note.find('level').text) + int(note.find('levelDecimal').text) / 10,
                    "designerId": int(note.find('notesDesigner').find('id').text),
                    "designerName": note.find('notesDesigner').find('str').text,
                    "noteType": int(note.find('notesType').text),
                    "musicLevelId": int(note.find('musicLevelID').text),
                    "isEnable": str_to_bool[note.find('isEnable').text],
                    "volume": {
                        "tap": note_num[0] if note_num else 0,
                        "break": note_num[1] if note_num else 0,
                        "hold": note_num[2] if note_num else 0,
                        "slide": note_num[3] if note_num else 0,
                        "all": note_num[4] if note_num else 0
                    }
                }
                note_details.append(note_detail)
        # 构建字典
        dic = {
            "musicId": int(root.find('name').find('id').text),
            "musicName": root.find('name').find('str').text,
            "sortName": root.find('sortName').text,
            "artistId": int(root.find('artistName').find('id').text),
            "artistName": root.find('artistName').find('str').text,
            "genreId": int(root.find('genreName').find('id').text),
            "genreName": root.find('genreName').find('str').text,
            "bpm": float(root.find('bpm').text),
            "version": root.find('version').text,
            "info": {
                "lockType": int(root.find('lockType').text),
                "subLockType": int(root.find('subLockType').text),
                "eventId": int(root.find('eventName').find('id').text),
                "eventName": root.find('eventName').find('str').text,
            },
            "note": note_details,
        }
        dics.append(dic)
    await save_to_json('Music', dics)


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

    '''if os.path.exists(f'{file_root}/challenge'):
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
    if os.path.exists(f'{file_root}/event'):
        print('Find event dir!')
        task_list.append(event_parse(f'{file_root}/event'))
    if os.path.exists(f'{file_root}/frame'):
        print('Find frame dir!')
        task_list.append(frame_parse(f'{file_root}/frame'))
    if os.path.exists(f'{file_root}/icon'):
        print('Find icon dir!')
        task_list.append(icon_parse(f'{file_root}/icon'))
    if os.path.exists(f'{file_root}/loginBonus'):
        print('Find loginBonus dir!')
        task_list.append(login_bonus_parse(f'{file_root}/loginBonus'))
    if os.path.exists(f'{file_root}/map'):
        print('Find map dir!')
        task_list.append(map_parse(f'{file_root}/map'))
    if os.path.exists(f'{file_root}/mapBonusMusic'):
        print('Find mapBonusMusic dir!')
        task_list.append(map_bonus_music_parse(f'{file_root}/mapBonusMusic'))
    if os.path.exists(f'{file_root}/mapColor'):
        print('Find mapColor dir!')
        task_list.append(map_color_parse(f'{file_root}/mapColor'))
    if os.path.exists(f'{file_root}/mapTreasure'):
        print('Find mapTreasure dir!')
        task_list.append(map_treasure_parse(f'{file_root}/mapTreasure'))
        '''
    if os.path.exists(f'{file_root}/music'):
        print('Find music dir!')
        task_list.append(music_parse(f'{file_root}/music'))

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

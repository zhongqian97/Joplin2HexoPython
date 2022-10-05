import os
import yaml
import requests
from pprint import pprint
from typing import Set, Dict, Any, TextIO
import json
from copy import deepcopy
import os
from multiprocessing import Pool

# 配置部分, 读取yaml文件即可
# config.yaml 只需要路径path、 基础端口port、 身份验证token 以及 笔记标签 tags 即可！
#
#

def _load_config(fp: TextIO) -> Dict[str, Any]:
    """
    Load the yaml config from the file-like object.
    """
    try:
        return yaml.safe_load(fp)
    except yaml.parser.ParserError as e:
        raise Exception(
            "Error parsing yaml file. Please check for formatting errors. "
            "A tool such as http://www.yamllint.com/ can be helpful with this."
        ) from e

def load_config(config_path: str) -> Dict[str, Any]:
    try:
        with open(config_path) as data_file:
            args = _load_config(data_file)
            return args
    except OSError:
        abs_path = os.path.abspath(config_path)
        raise Exception(f"Config file could not be found at {abs_path}.")
    except UnicodeDecodeError:
        raise Exception(
            f"There was an error decoding Config file from {config_path}. "
            f"Make sure your file is save using UTF-8"
        )

args = load_config('./joplin2hexoPython/config.yaml')
print("My config file: " + str(args))
args['path'] += "source/_posts/"

# 可调函数部分
def getJson(url, payload):
    headers = {
    'content-type': 'application/x-www-form-urlencoded;charset=UTF-8'
    }
    r = requests.get(url, params=payload, headers=headers)
    # pprint(r.json())
    return r.json()

def getPicture(url, payload):
    headers = {
    'content-type': 'application/x-www-form-urlencoded;charset=UTF-8'
    }
    r = requests.get(url, params=payload, headers=headers)
    # pprint(r.content)
    return r.content

def getText(url, payload):
    headers = {
    'content-type': 'application/x-www-form-urlencoded;charset=UTF-8'
    }
    r = requests.get(url, params=payload, headers=headers)
    # pprint(r.text)
    return r.text

def HasPing():
    global args
    url = 'http://localhost:'+ str(args['port']) + '/ping'
    payload = {}
    try:
        if getText(url, payload) == 'JoplinClipperServer':
            return True
        else:
            return False
    except:
        return False
    return False

def HasTokenIsWorked():
    global args
    url = 'http://localhost:'+ str(args['port']) + '/auth/check/'
    payload = deepcopy(args)
    try:
        if getJson(url, payload)["valid"] == True:
            return True
        else:
            return False
    except:
        return False
    return False

def getAllTags():
    global args
    url = 'http://localhost:'+ str(args['port']) + '/tags'
    payload = deepcopy(args)
    i = 1
    all_jsons = {}
    while True:
        try:
            payload['page'] = i
            temp_json = getJson(url, payload)
            if len(all_jsons) == 0:
                all_jsons = temp_json
            else:
                all_jsons["items"].extend(temp_json["items"])
            
            i += 1
            if temp_json["has_more"] == False:
                break
        except:
            return []
    return all_jsons["items"]

def _tagsList2Dict(tags_list):
    d = {}
    for tag in tags_list:
        d[tag['title']] = tag['id']
    return d

def getNoteListByTags(tags_list):
    global args
    all_jsons = {}
    payload = deepcopy(args)
    tags = args['tags']
    tags_dict = _tagsList2Dict(tags_list)
    for tag_title in tags:
        if tag_title not in tags_dict:
            continue
        tag = tags_dict[tag_title]
        url = 'http://localhost:'+ str(args['port']) + '/tags/' + tag + "/notes"
        i = 1
        while True:
            try:
                payload['page'] = i
                temp_json = getJson(url, payload)
                if len(all_jsons) == 0:
                    all_jsons = temp_json
                else:
                    all_jsons["items"].extend(temp_json["items"])
                
                i += 1
                if temp_json["has_more"] == False:
                    break
            except:
                return []
    return all_jsons["items"]

def getNoteBodyByNoteId(note_id):
    global args
    url = 'http://localhost:'+ str(args['port']) + '/notes/' + note_id + '/'
    payload = deepcopy(args)
    payload['fields'] = 'body'
    try:
        body = getJson(url, payload)
        return body['body']
    except:
        return ""
    return ""

def getNoteAllResourceIdByNoteId(note_id):
    global args
    url = 'http://localhost:'+ str(args['port']) + '/notes/' + note_id + '/resources'
    payload = deepcopy(args)
    i = 1
    all_jsons = {}
    while True:
        try:
            payload['page'] = i
            temp_json = getJson(url, payload)
            if len(all_jsons) == 0:
                all_jsons = temp_json
            else:
                all_jsons["items"].extend(temp_json["items"])
            
            i += 1
            if temp_json["has_more"] == False:
                break
        except:
            return []
    return all_jsons["items"]


def getNoteResourceFileByResourceId(resource_id):
    global args
    url = 'http://localhost:'+ str(args['port']) + '/resources/' + resource_id + '/file'
    payload = deepcopy(args)
    try:
        img = getPicture(url, payload)
        return img
    except:
        return None
    return None

def saveNoteMarkdownFile(name, text):
    global args
    with open(args["path"] + name + '.md', "w", encoding='utf-8') as f:
        f.write(getNoteBodyByNoteId(text))
    pass

def saveResourceFile(title, name, img):
    global args
    path = args["path"] + title + '/'
    if os.path.exists(path) == False:
        os.makedirs(path)
    with open(path + name, "wb") as f:
        f.write(getNoteResourceFileByResourceId(img))
    pass

# 单元测试
# assert HasPing() == True
# assert HasTokenIsWorked() == True
# tags_list = getAllTags()
# print(len(tags_list))
# note_list = getNoteListByTags(tags_list)
# print(len(note_list))
# print(getNoteBodyByNoteId(note_list[0]['id']))
# for note in note_list:
#     print(getNoteAllResourceIdByNoteId(note['id']))
# resource = getNoteAllResourceIdByNoteId(note['id'])
# getNoteResourceFileByResourceId(resource[0]['id'])

# 主流程部分
if __name__ == '__main__':
    assert HasPing() == True
    assert HasTokenIsWorked() == True
    tags_list = getAllTags()
    note_list = getNoteListByTags(tags_list)
    # 串行代码
    # for note in note_list:
    #     saveNoteMarkdownFile(note['title'], getNoteBodyByNoteId(note['id']))
    #     resource = getNoteAllResourceIdByNoteId(note['id'])
    #     for r in resource:
    #         saveResourceFile(note['title'], r['title'], getNoteResourceFileByResourceId(r['id']))
    #     pass

    # 并行代码
    p = Pool(12)
    for note in note_list:
        p.apply_async(saveNoteMarkdownFile, args=(note['title'], note['id']))
        resource = getNoteAllResourceIdByNoteId(note['id'])
        for r in resource:
            p.apply_async(saveResourceFile, args=(note['title'], r['title'], r['id']))

    print('Waiting for all subprocesses done...')
    p.close()
    p.join()
    print("zhongqian: done!!!!")
import json
from Logger import logger
import os
from multiprocessing import Pool
from Scholar import search_author, search_photo
import time
import warnings
import example
warnings.filterwarnings('ignore')

_MAXRETRY = 6
_ERRORMESSAGE = "id: {0} | Error: {1}"
_INFOMESSAGE = "id: {0} has done."
_RESULT_PATH = os.path.join(os.getcwd(), "result", "author_google_info")


def get_author_data(data):
    if type(data) is tuple:
        keywords = "(%s) + (%s)" % data
    else:
        keywords = data

    tries = 0
    while tries < _MAXRETRY:
        tries += 1
        try:
            author = next(search_author(keywords)).fill()
            return author.get_info()
        except StopIteration:
                if type(data) is tuple and len(data[1]) > 0:
                    return get_author_data(data[0])
                else:
                    logger.error("Can not find author %s" % keywords.encode("utf-8"))
                    return None
        except Exception as e:
            if tries < _MAXRETRY:
                logger.info(_ERRORMESSAGE.format(str(keywords), str(e)) + " | tries: %d" % tries)
            else:
                logger.error(_ERRORMESSAGE.format(str(keywords), str(e)) + " | tries: %d" % tries)
            time.sleep(tries)
    return None


def get_author_img(google_id):
    tries = 0
    while tries < _MAXRETRY:
        tries += 1
        try:
            return search_photo(google_id)
        except Exception:
            time.sleep(tries)


def write_data_proc(author):
    auId, auName, auOrg = author
    r = get_author_data((auName, auOrg))
    if r is None:
        return
    r["msId"] = auId

    path_data = os.path.join(os.getcwd(), 'dataGS')
    if not os.path.exists(path_data):
        os.makedirs(path_data)
    file_name_data = os.path.join(path_data, '%s.json' % auId)
    with open(file_name_data, 'w') as fw:
        json.dump(r, fw)

    path_img = os.path.join(os.getcwd(), 'dataGS_img')
    if not os.path.exists(path_img):
        os.makedirs(path_img)
    file_name_img = os.path.join(path_img, '%s.jpg' % auId)
    with open(file_name_img, 'wb') as fi:
        fi.write(get_author_img(google_id=r.setdefault("id", "")))
        fi.flush()

    logger.info("id: %s\tname: %s" % (auId, auName))


# 使用前维护此函数,按照样例生成程序
def get_author_list():
    al = [
        ("1", "jeff dean", "google"),   # id, name, organization
        ("2", "Scott Shenker", "UC Berkeley"),
        ("3", "Geoffrey Hinton", ""),   # 如果不存在组织信息，则最后一项置空
        ("4", "wang peng", "southeast university"),
        ("5", "sdfdsfsdafasdf", "")

    ]
    return al


def get_remain(total_list):
    path = os.path.join(os.getcwd(), "dataGS")
    if not os.path.exists(path):
        os.makedirs(path)
    file_list = os.listdir(path)
    existing = set()
    for file in file_list:
        existing.add(file.split(".")[0])
    set_auid = set(i[0] for i in total_list)
    remain = set_auid - existing
    logger.info('all task: %d' % len(set_auid))
    logger.info('existing: %d' % len(existing))
    logger.info('remain: %d' % len(remain))
    return [au for au in total_list if au[0] in remain]


if __name__ == '__main__':
    """ 
    使用时改写get_author_list()函数；
    返回值为一个元组列表：[(auId, auName, auOrganization), (),]
    """
    pool = Pool(8)
    a_list = get_remain(get_author_list())
    # a_list = example.get_author_list(os.path.join(os.getcwd(), "author_raw_data_example"))
    for a in a_list:
        pool.apply_async(write_data_proc, (a, ))
    pool.close()
    pool.join()



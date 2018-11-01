import os
import json

"""
    示例文件，获取作者列表
"""


def get_author_list(path_data):
    author_list = list()
    for file_name in os.listdir(path_data):
        AuId = file_name.replace(".json", "")
        with open(os.path.join(path_data, file_name), "r") as f:
            try:
                r = json.load(f)
                dAuN, lastKnownAffiliation = r["dAuN"], r["lastKnownAffiliation"]
                affi = lastKnownAffiliation.setdefault("lt", "") if lastKnownAffiliation is not None else ""
                author_list.append((AuId, dAuN, affi))
            except Exception as e:
                print(file_name, str(e))
    return author_list


if __name__ == '__main__':
    path_author_raw_data = os.path.join(os.getcwd(), "author_raw_data_example")
    l = get_author_list(path_author_raw_data)
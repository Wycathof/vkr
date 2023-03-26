import json
import pprint
from datetime import datetime
import pandas as pd
from warnings import simplefilter

simplefilter(action="ignore", category=pd.errors.PerformanceWarning)

path = r"C:\Users\ArVip\PycharmProjects\nirs\csvpack\block.csv"

start_time = datetime.now()


def read_data(path):
    csv_data = pd.read_csv(path, delimiter=';', encoding="", encoding_errors="ignore")
    for i, body in enumerate(csv_data['body']):
        start = '{"Event"'
        check = body.startswith(start)
        if not check:
            csv_data = csv_data.drop(index=i)
    csv_data.reset_index(drop=True, inplace=True)
    return csv_data


csv_data = read_data(path)
pprint.pprint(len(csv_data))


# pprint.pprint(len(csv_data)) #len 39 -------------------------------------------------------------------------
def to_json_object(csv_data, new_dict):
    for i, body in enumerate(csv_data['body']):
        json_object = json.loads(body)
        new_dict[i] = json_object
    return new_dict


new_dict = {}
new_dict = to_json_object(csv_data, new_dict)
# pprint.pprint(len(new_dict)) #len 39 -------------------------------------------------------------------------


def find_only(new_dict, list_msg, list_target_host_name):
    for i, body in enumerate(new_dict):
        list_msg.insert(i, new_dict[i]["Event"]["System"]["EventID"])
        list_target_host_name.insert(i, new_dict[i]["Event"]["System"]["Computer"])
    return new_dict, list_msg, list_target_host_name


list_msg = []
list_target_host_name = []
find_only(new_dict, list_msg, list_target_host_name)
csv_data["msgid"] = list_msg
csv_data["target_host_name"] = list_target_host_name
unique_msgid = csv_data['msgid'].value_counts()
unique_target_host_name = csv_data['target_host_name'].value_counts()


# print(unique_msgid)  # 4625 - 31,  4103 - 4, {'text': '800', 'Qualifiers': '0'}  -   4 -------------------------
# print(unique_target_host_name)
# print(csv_data)

def drop_not_win_aud(csv_data, new_dict):
    for i, body in enumerate(new_dict):
        if new_dict[i]["Event"]["System"]["Provider"]["Name"] != "Microsoft-Windows-Security-Auditing":
            csv_data = csv_data.drop(index=i)
    csv_data.reset_index(drop=True, inplace=True)
    return csv_data


csv_data = drop_not_win_aud(csv_data, new_dict)

# pprint.pprint(len(csv_data)) #len 31 --------------------------
unique_msgid = csv_data['msgid'].value_counts()
# print(unique_msgid) # 4625 - 31

csv_data.columns = csv_data.columns.str.replace('п»ї"time"', 'time')

new_dict_new = {}
new_dict_new = to_json_object(csv_data, new_dict_new)


# pprint.pprint(len(new_dict_new)) #len 31 --------------------------

def find(new_dict_new, new_find_value, return_list, index):
    key_in_body = []
    for i, l in enumerate(new_dict_new):
        key_in_body.insert(i, l["Name"])
    if new_find_value in key_in_body:
        for l in new_dict_new:
            if (l["Name"] == new_find_value):
                if ("text" in l):
                    return_list.insert(index, l["text"])
                else:
                    return_list.insert(index, "NULL")
    else:
        return_list.insert(index, "NULL")


def find2(new_dict_new, new_find_value, return_list, index):
    key_in_body = []
    for i, l in enumerate(new_dict_new):
        key_in_body.insert(i, l["Name"])
    if new_find_value in key_in_body:
        for l in new_dict_new:
            if (l["Name"] == new_find_value):
                if ("text" in l):
                    return_list.append(l["text"])
                else:
                    return_list.append("NULL")
    else:
        return_list.append("NULL")


def crate_dict_with_one_body_unique_msgid(arr_unique_body, csv_data):
    for i, msg in enumerate(csv_data['msgid']):
        check = ""
        if i != check:
            arr_unique_body[msg] = json.loads(csv_data.iloc[i]['body'])
            check = i
    return arr_unique_body


arr_unique_body = {}
arr_unique_body = crate_dict_with_one_body_unique_msgid(arr_unique_body, csv_data)

name_coloumn = []


def getting_column_names(arr_unique_body, name_coloumn):
    for body in arr_unique_body.values():
        for l in body["Event"]["EventData"]["Data"]:
            i = 0
            if l["Name"] not in name_coloumn:
                name_coloumn.insert(i, l["Name"])
                i += 1

    return name_coloumn


def getting_column_names2(arr_unique_body, name_coloumn):
    for body in arr_unique_body.values():
        for l in body["Event"]["EventData"]["Data"]:
            if l["Name"] not in name_coloumn:
                name_coloumn.append(l["Name"])

    return name_coloumn


return_list = []
name_coloumn = getting_column_names(arr_unique_body, name_coloumn)


def insert_in_df2(csv_data, name_coloumn):
    for name in name_coloumn:
        return_list = []
        for i, body in enumerate(new_dict_new):
            find(new_dict_new[i]["Event"]["EventData"]["Data"], name, return_list, i)
        csv_data[name] = return_list


def insert_in_df(csv_data, name_coloumn):
    for ind, name in enumerate(name_coloumn):
        return_list = []
        for i, body in enumerate(new_dict_new):
            find(new_dict_new[i]["Event"]["EventData"]["Data"], name, return_list, i)
        csv_data.insert(ind + 6, name, return_list)


insert_in_df(csv_data, name_coloumn)

# ----------
pd.set_option('display.max_rows', None)
abc = len(csv_data["msgid"])
# ----------
print("Время выполнения", datetime.now() - start_time)


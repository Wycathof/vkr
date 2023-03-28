import json
import pprint
from datetime import datetime
import pandas as pd
from warnings import simplefilter

simplefilter(action="ignore", category=pd.errors.PerformanceWarning)
# path = r"C:\Users\ArVip\PycharmProjects\nirs\csvpack\block.csv"

def read_data(path):
    csv_data = pd.read_csv(path, delimiter=';', encoding="", encoding_errors="ignore")
    for i, body in enumerate(csv_data['body']):
        start = '{"Event"'
        check = body.startswith(start)
        if not check:
            csv_data = csv_data.drop(index=i)
    csv_data.reset_index(drop=True, inplace=True)
    return csv_data


def to_json_object(csv_data, new_dict):
    for i, body in enumerate(csv_data['body']):
        json_object = json.loads(body)
        new_dict[i] = json_object
    return new_dict


def find_only(new_dict, list_msg, list_target_host_name):
    for i, body in enumerate(new_dict):
        list_msg.insert(i, new_dict[i]["Event"]["System"]["EventID"])
        list_target_host_name.insert(i, new_dict[i]["Event"]["System"]["Computer"])
    return new_dict, list_msg, list_target_host_name


def drop_not_win_aud(csv_data, new_dict):
    for i, body in enumerate(new_dict):
        if new_dict[i]["Event"]["System"]["Provider"]["Name"] != "Microsoft-Windows-Security-Auditing":
            csv_data = csv_data.drop(index=i)
    csv_data.reset_index(drop=True, inplace=True)
    return csv_data


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


def crate_dict_with_one_body_unique_msgid(arr_unique_body, csv_data):
    for i, msg in enumerate(csv_data['msgid']):
        check = ""
        if i != check:
            arr_unique_body[msg] = json.loads(csv_data.iloc[i]['body'])
            check = i
    return arr_unique_body


def getting_column_names(arr_unique_body, name_coloumn):
    for body in arr_unique_body.values():
        for l in body["Event"]["EventData"]["Data"]:
            i = 0
            if l["Name"] not in name_coloumn:
                name_coloumn.insert(i, l["Name"])
                i += 1

    return name_coloumn


def insert_in_df2(csv_data, name_coloumn, new_dict_new):
    for ind, name in enumerate(name_coloumn):
        return_list = []
        for i, body in enumerate(new_dict_new):
            find(new_dict_new[i]["Event"]["EventData"]["Data"], name, return_list, i)
        csv_data.insert(ind + 6, name, return_list)

def insert_in_df(csv_data, name_coloumn, new_dict_new):
    for name in name_coloumn:
        return_list = []
        for i, body in enumerate(new_dict_new):
            find(new_dict_new[i]["Event"]["EventData"]["Data"], name, return_list, i)
        csv_data[name] = return_list

def find_name_and_count_cd(all_count, all_name):
    all_count_arr = []
    all_name_arr = []

    itog = ""
    for i in all_count:
        all_count_arr.append(i)
    for a in all_name:
        all_name_arr.append(a)
    for i, q in enumerate(all_name_arr):
        itog += f"•{q} - {all_count_arr[i]} событий\n"
    return itog

def main(path):
    start_time = datetime.now()

    csv_data = read_data(path)
    new_dict = {}
    new_dict = to_json_object(csv_data, new_dict)

    list_msg = []
    list_target_host_name = []
    new_dict, list_msg, list_target_host_name = find_only(new_dict, list_msg, list_target_host_name)
    csv_data["msgid"] = list_msg
    csv_data["Computer"] = list_target_host_name

    unique_msgid = csv_data['msgid'].value_counts()
    unique_target_host_name = csv_data['Computer'].value_counts()
    csv_data = drop_not_win_aud(csv_data, new_dict)

    unique_msgid = csv_data['msgid'].value_counts()
    # print(unique_msgid) # 4625 - 31

    csv_data.columns = csv_data.columns.str.replace('п»ї"time"', 'time')

    new_dict_new = {}
    new_dict_new = to_json_object(csv_data, new_dict_new)

    # pprint.pprint(len(new_dict_new)) #len 31 --------------------------

    arr_unique_body = {}
    arr_unique_body = crate_dict_with_one_body_unique_msgid(arr_unique_body, csv_data)

    name_coloumn = []

    return_list = []
    name_coloumn = getting_column_names(arr_unique_body, name_coloumn)

    insert_in_df(csv_data, name_coloumn, new_dict_new)

    # ----------
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)

    # ----------


    result_str = f"За последние сутки зафиксировано многочисленные блокировки УЗ {csv_data[csv_data['msgid'] == '4740']['TargetUserName'].unique()[0]} на контроллерах домена:\n" \
                 f"{find_name_and_count_cd(csv_data[csv_data['msgid'] == '4740']['Computer'].value_counts(), csv_data[csv_data['msgid'] == '4740']['Computer'].unique())}" \
                 f"Хосты инициаторы блокировок:\n" \
                 f"{find_name_and_count_cd(csv_data[csv_data['msgid'] == '4740']['TargetDomainName'].value_counts(), csv_data[csv_data['msgid'] == '4740']['TargetDomainName'].unique())}"
    # print(result_str)


    print("Время выполнения", datetime.now() - start_time)
    return result_str

def pizda5():
    itog = "Ваша строка: 5"
    return itog

def pizda10():
    itog = "Ваша строка: 10"
    return itog

# main(path)
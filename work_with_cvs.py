import json
import pprint
from datetime import datetime
import pandas as pd
from warnings import simplefilter

simplefilter(action="ignore", category=pd.errors.PerformanceWarning)
# path = r"C:\Users\ArVip\PycharmProjects\nirs\csvresult\test2.csv"  # большая
# path = r"C:\Users\ArVip\PycharmProjects\nirs\csvpack\block.csv"

def read_data_csv(path):
    csv_data = pd.read_csv(path, delimiter=';', encoding="", encoding_errors="ignore")
    for i, body in enumerate(csv_data['body']):
        start = '{"Event"'
        check = body.startswith(start)
        if not check:
            csv_data = csv_data.drop(index=i)
    csv_data.reset_index(drop=True, inplace=True)
    return csv_data


def read_data_xlsx(path):
    csv_data = pd.read_excel(path, engine="openpyxl")
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
                break
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


def find_name_and_count_(data, msg, change_str,data2):
    dict = data.to_dict()
    itog_str = ""

    for d in dict:
        d_copy = d
        if change_str is True:
            if d.find("::ffff") != -1:
                d = d.replace("::ffff:", "")
            if d == "0x12":
                d = d.replace("0x12", "Account disabled, expired, locked out, logon hours")
            if d == "0x18":
                d = d.replace("0x18", "Usually means bad password")
            if d == "0x17":
                d = d.replace("0x17", "The user’s password has expired")
            if d == "0xc000006a":
                d = d.replace("0xc000006a", "user name is correct but the password is wrong")
            if d == "0xc0000064":
                d = d.replace("0xc0000064", "user name does not exist")
        itog_str += f"• {d} - {dict[d_copy]} событий\n"
    return itog_str.lower()

def find_name_and_count_2(data, msg, change_str, data2): #нужно переработать
    dict = data.to_dict()
    itog_str = ""
    for i, d in enumerate(dict):
        d_copy = d
        ip = data2[data2['msgid'] == '4625'].iloc[i]['IpAddress']
        if change_str is True:
            print(d)
            if d.find("::ffff") != -1:
                d = d.replace("::ffff:", "")
            if d == "0x12":
                d = d.replace("0x12", "Account disabled, expired, locked out, logon hours")
            if d == "0x18":
                d = d.replace("0x18", "Usually means bad password")
            if d == "0x17":
                d = d.replace("0x17", "The user’s password has expired")

        itog_str += f"• {d} - {ip} - {dict[d_copy]} событий" \
                    f"\n"
    return itog_str.lower()

def check_smb(i):
    name = ""
    if i == "3":
        name = "SMB"
    if i == "8":
        name = "OWA"
    return  name


def print4740(csv_data):
    result4740_str = f"Зафиксированы многочисленные блокировки УЗ {csv_data[csv_data['msgid'] == '4740']['TargetUserName'].unique()[0]} на контроллере(ах) домена:\n" \
                     f"{find_name_and_count_(csv_data[csv_data['msgid'] == '4740']['Computer'].value_counts(), msg=4740, change_str=False, data2=None)}\n" \
                     f"Хост(ы) инициатор(ы) блокировок:\n" \
                     f"{find_name_and_count_(csv_data[csv_data['msgid'] == '4740']['TargetDomainName'].value_counts(), msg=4740, change_str=False, data2=None)}\n" \
                     f"За период с 26.11.2022 13:46:57 по 27.11.2022 10:33:14 зафиксировано " \
                     f"{csv_data[csv_data['msgid'] == '4740']['time'].count()} событий.\nДанное время указано в формате UTC-0.\n\n"
    return result4740_str


# "За период с {csv_data[csv_data['msgid'] == '4740']['time'][csv_data[csv_data['msgid'] == '4740']['time'].index[-1]]} по {csv_data[csv_data['msgid'] == '4740']['time'][csv_data[csv_data['msgid'] == '4740']['time'].index[0]]} зафиксировано " \
#                      f"{csv_data[csv_data['msgid'] == '4740']['time'].count()} событий.\nДанное время указано в формате UTC-0.\n\n"
def print4771(csv_data):
    result4771_str = f"афиксированы неуспешные попытки преаутентификации Kerberos УЗ {csv_data[csv_data['msgid'] == '4771']['TargetUserName'].unique()[0]} на хосте(-ах):\n" \
                     f"{find_name_and_count_(csv_data[csv_data['msgid'] == '4771']['IpAddress'].value_counts(), msg=4771, change_str=True, data2=None)} " \
                     f"События зафиксированы на контроллере(-ах) домена:\n{find_name_and_count_(csv_data[csv_data['msgid'] == '4771']['Computer'].value_counts(), msg=4771, change_str=False, data2=None)} " \
                     f"\nЗа период с 26.11.2022 13:47:08 по 27.11.2022 10:32:58 зафиксировано " \
                     f"{csv_data[csv_data['msgid'] == '4771']['time'].count()} событий.\nДанное время указано в формате UTC-0.\n" \
                     f"Причины неуспешности:\n{find_name_and_count_(csv_data[csv_data['msgid'] == '4771']['Status'].value_counts(), msg=4771, change_str=True, data2=None)}\n\n"

    return result4771_str


def print4625(csv_data, result4625_str=str("")):
    for i in csv_data[csv_data['msgid'] == '4625']['LogonType'].unique():
        result4625_str += f"Зафиксированы неуспешные попытки аутентификации по {check_smb(i)} (тип входа: {i}, Пакет аутентификации: {csv_data.loc[(csv_data['msgid'] == '4625') & (csv_data['LogonType'] == i)]['AuthenticationPackageName'].unique()[0]}) " \
                          f"под УЗ {csv_data[csv_data['msgid'] == '4625']['TargetUserName'].unique()[0]} на хосте(-ах):\n{find_name_and_count_(csv_data.loc[(csv_data['msgid'] == '4625') & (csv_data['LogonType'] == i)]['Computer'].value_counts(), msg=4625, change_str=False, data2=csv_data)}" \
                          f"С хостов:\n{find_name_and_count_(csv_data.loc[(csv_data['msgid'] == '4625') & (csv_data['LogonType'] == i)]['WorkstationName'].value_counts(), msg=4625, change_str=False, data2=csv_data)}" \
                          f"Причины неуспешности:\n{find_name_and_count_(csv_data.loc[(csv_data['msgid'] == '4625') & (csv_data['LogonType'] == i)]['SubStatus'].value_counts(), msg=4625, change_str=True, data2=None)}\n"

    result4625_str += f"За период с {csv_data[csv_data['msgid'] == '4625']['time'][csv_data[csv_data['msgid'] == '4625']['time'].index[-1]]} по {csv_data[csv_data['msgid'] == '4625']['time'][csv_data[csv_data['msgid'] == '4625']['time'].index[0]]} зафиксировано " \
                      f"{csv_data[csv_data['msgid'] == '4625']['time'].count()} событий.\nДанное время указано в формате UTC-0.\n\n"
    return result4625_str


# def main(path):
def main(path, data_flag, name_file_test, result_str=""):
    start_time = datetime.now()
    # csv_data = read_data_csv(path)
    if ".csv" in name_file_test:
        csv_data = read_data_csv(path)
    if ".xlsx" in name_file_test:
        csv_data = read_data_xlsx(path)
    new_dict = {}
    new_dict = to_json_object(csv_data, new_dict)

    list_msg = []
    list_target_host_name = []
    new_dict, list_msg, list_target_host_name = find_only(new_dict, list_msg, list_target_host_name)
    csv_data["msgid"] = list_msg
    csv_data["Computer"] = list_target_host_name

    unique_msgid = csv_data['msgid'].value_counts()
    csv_data = drop_not_win_aud(csv_data, new_dict)

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
    unique_msgid_value = csv_data['msgid'].unique()

    # ----------
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    # ----------

    if data_flag == "block":
        print(data_flag)
        if "4740" in unique_msgid_value:
            result_str += f"{print4740(csv_data)}"
        if "4771" in unique_msgid_value:
            result_str += f"Также, з{print4771(csv_data)}"
        if "4625" or "4625" in unique_msgid_value:
            result_str += f"Также,{print4625(csv_data)}"
    if data_flag == "password":
        print(data_flag)
        result_str = "ebalau"

    # print(print4625(csv_data))

    print("Время выполнения", datetime.now() - start_time)
    return result_str


# main(path)

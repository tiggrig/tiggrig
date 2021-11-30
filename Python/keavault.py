import subprocess
import sys
# from datetime import datetime
from time import sleep
import json
import getpass


class Bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def welcome_menu():
    print("\nWelcome to KeyVault management iteractive menu, through this menu it is "
          "possible different oparations with KeyVault")
    print("You will be promted depends on oparation you want to apply")


def main_menu():
    print("\nCreate a Keyvault [c] / Create KeyVault secret:value(s) [s]")
    print("List KeyVault secret names [ls] / Show secret/value pair [sh]")
    print("Purge secret [ps] / Purge Keyvault [ps]")
    print("Delete Keyvault [dk] / delete secret [ds]")
    print("Backup/restote Keyvault [br]")
    print("Quit program [q]")


def check_azure_keyvault(keyvaultname: str, rg: str):
    entrylist = []
    txt = "az keyvault list --resource-group {} --resource-type vault"
    cmd = txt.format(rg)
    command = subprocess.check_output(["powershell", "-Command", cmd], text=True)
    commandoutputlist = json.loads(command)
    for items in commandoutputlist:
        vault = items.get("name")
        entrylist.append(vault)
    if keyvaultname in entrylist:
        return True
    else:
        return False


def azure_keyvault_set_create_secret_for_restor(keyvaultname: str, inputdict: dict):
    for key, value in inputdict.items():        
        #value = "'"+value+"'"
        txt = "az keyvault secret set --vault-name {} -n {} --value '{}'"
        cmd = txt.format(keyvaultname, key, value)
        command = subprocess.run(["powershell", "-Command", cmd], capture_output=True)
        if command.returncode != 0:
            print("An error occurred: %s", command.stderr)
        else:
            print("SECRET " + key + " SUCCESSFULLY CREATE with " + value)


def azure_keyvault_set_create_secret(keyvaultname: str):
    secretdict: dict = {}
    secretcount = input("\nHow many secrets you want to create: ")
    for x in range(int(secretcount)):
        secretname = input("\nPlease type secret name: ")
        secretvalue = getpass.getpass("Enter secret value: ", stream=None)
        secretdict.update({secretname: secretvalue})

    for key, value in secretdict.items():
        txt = "az keyvault secret set --vault-name {} -n {} --value {}"
        cmd = txt.format(keyvaultname, key, value)
        command = subprocess.run(["powershell", "-Command", cmd], capture_output=True)
        if command.returncode != 0:
            print("An error occurred: %s", command.stderr)
        else:
            print("SECRET " + key + " SUCCESSFULLY CREATE!!!")


def azure_keyvault_secret_list(keyvaultname: str):
    entrylist = []
    txt = "az keyvault secret list --vault-name {}"
    cmd = txt.format(keyvaultname)
    command = subprocess.check_output(["powershell", "-Command", cmd], text=True)
    commandoutputlist = json.loads(command)
    for items in commandoutputlist:
        keyvaultentry = items.get("name")
        entrylist.append(keyvaultentry)        
    return entrylist


def azure_keyvault_secret_show_by_secret_name(keyvaultname: str):
    secretname = input("Please type secret name: ")
    txt = "az keyvault secret show --vault-name {} -n {}"
    cmd = txt.format(keyvaultname, secretname)
    commandoutput = subprocess.check_output(["powershell", "-Command", cmd], text=True)
    jsonloader = json.loads(commandoutput)
    secretvalue = jsonloader["value"]    
    print("For SECRET NAME: " + secretname + "\nVALUE IS: " + secretvalue)


def azure_keyvault_secret_show_for_backup(keyvaultname: str, inputlist: list):
    # inputlist = azure_keyvault_secret_list(keyvaultname)
    keyvultsecretdict = {}
    for item in inputlist:
        txt = "az keyvault secret show --vault-name {} -n {}"
        cmd = txt.format(keyvaultname, item)
        commandoutput = subprocess.check_output(["powershell", "-Command", cmd], text=True)
        jsonloader = json.loads(commandoutput)
        secret_value = jsonloader["value"]
        keyvultsecretdict[item] = str(secret_value)
    return keyvultsecretdict


def azure_keyvault_secret_show(keyvaultname: str, inputlist: list):
    # inputlist = azure_keyvault_secret_list(keyvaultname)
    keyvultsecretdict = {}
    i: int = 1
    for item in inputlist:
        txt = "az keyvault secret show --vault-name {} -n {}"
        cmd = txt.format(keyvaultname, item)
        print(cmd)
        commandoutput = subprocess.check_output(["powershell", "-Command", cmd], text=True)
        jsonloader = json.loads(commandoutput)
        print(type(item))
        secret_value = jsonloader["value"]
        keyvultsecretdict[item] = secret_value
        print(type(secret_value))
    for key, value in keyvultsecretdict.items():
        print("\n" + str(i) + ".  SECRET NAME:  " + key + "\n    SECRET VALUE: " + value)        
        i = i + 1


def azure_keyvault_create(keyvaultname: str, rg: str):
    location = input("Please type location (default is westeurope): ") or "westeurope"
    sku = input("Please type sku (default is standart): ") or "standard"
    txt = "az keyvault create -g {} -n {} -l {} --sku {}"
    cmd = txt.format(rg, keyvaultname, location, sku)
    command = subprocess.Popen(["powershell", "-Command", cmd], text=True)
    while command.poll() is None:
        print("--Creating--")
        sleep(15)
    if command.returncode != 0:
        print("An error occurred: %s", command.stderr)
    else:
        print("KeyVault " + keyvaultname + " successfuly created!!!")


def azure_keyvault_delete_secret_purge(keyvaultname: str, secretname: str):
    print("deleting secret " + secretname + " permanently")
    txt = "az keyvault secret purge --vault-name {} -n {}"
    cmd = txt.format(keyvaultname, secretname)
    command1 = subprocess.Popen(["powershell", "-Command", cmd], text=True)
    while command1.poll() is None:
        sleep(10)
    print("SECRET " + secretname + " PERMANENTLY DELETED FROM " + keyvaultname + " SUCCESSFULLY")


def azure_keyvault_delete_secret(keyvaultname: str, secretlist: list):
    secret_for_purge: list = []
    secrets_not_for_purge: list = []
    print("following secrets exist in " + keyvaultname + "\n")
    i = 1
    for secrets in secretlist:
        print(str(i) + ". " + secrets)
        i = i + 1
    delete_secrets_amount = input("\nHow many secrets want to delete from " + keyvaultname + " keyvault: ")
    for x in range(int(delete_secrets_amount)):
        secretname = input("Enter secret name to delete: ")
        permanent_delete_question = input("Delete permanently ? (yes/no): ")
        if permanent_delete_question.casefold() == "yes":
            secret_for_purge.append(secretname)
        else:
            secrets_not_for_purge.append(secretname)
    for secret_item in secrets_not_for_purge:
        txt = "az keyvault secret delete --vault-name {} -n {}"
        cmd = txt.format(keyvaultname, secret_item)
        command = subprocess.Popen(["powershell", "-Command", cmd], text=True)
        while command.poll() is None:
            print("--Deleting secret--")
            sleep(5)
    if command.returncode != 0:
        print("An error occurred: %s", command.stderr)
    else:
        sleep(1)
        print("SECRET " + secretname + " SUCCESSFULLY DELETED FROM " + keyvaultname + "KYEVAULT")
    print("--Deleting selected secrets permanently--")
    for y in secret_for_purge:
        azure_keyvault_delete_secret_purge(keyvaultname, y)


def azure_keyvault_delete(keyvaultname: str, rg: str):
    # rg = input("Please type recovery group (default is cargoo-kv-rg-weu1): ") or "cargoo-kv-rg-weu1"
    # keyvaultname = input("Please type vault name you want to delete: ")
    txt = "az keyvault delete --name {} -g {}"
    cmd = txt.format(keyvaultname, rg)
    command = subprocess.Popen(["powershell", "-Command", cmd], text=True)
    while command.poll() is None:
        print("--Deleting--")
        sleep(15)
    if command.returncode != 0:
        print("An error occurred: %s", command.stderr)
    else:
        print("KeyVault " + keyvaultname + " successfuly deleted!!!")


def close_program():
    print("\nScript will be interrupted")
    sys.exit()


if __name__ == '__main__':

    default_rg: str = "cargoo-kv-rg-weu1"
    source_keyvaultname: str = ""
    welcome_menu()
    trigger = False

    # While block
    while trigger is False:
        main_menu()
        answer = input("Please choose operation: ")

        # Create Keyvault block
        if answer == "c":
            source_rg = input("\nPlease type RG name (default is " + default_rg + "): ") or default_rg
            source_keyvaultname = input("Please type vault name: ")
            print("Checking if " + source_keyvaultname + " already exist in " + source_rg + " Resource group")
            is_keyvault_exist = check_azure_keyvault(source_keyvaultname, source_rg)
            if is_keyvault_exist:
                print("\nKeyvault " + source_keyvaultname + " already exist")
                input("Press enter to return main menu: ")
                trigger = False
            else:
                azure_keyvault_create(source_keyvaultname, source_rg)
                input("\n Press enter to return main menu: ")
                trigger = False

        # Create Keyvault secret/value pair block
        elif answer == "s":
            source_rg = input("\nPlease type RG name (default is " + default_rg + "): ") or default_rg
            source_keyvaultname = input("Please type vault name: ")
            print("Checking if " + source_keyvaultname + " already exist in " + source_rg + " Resource group")
            is_keyvault_exist = check_azure_keyvault(source_keyvaultname, source_rg)
            if is_keyvault_exist:
                keyvault_list_s = azure_keyvault_secret_list(source_keyvaultname)
                if len(keyvault_list_s) != 0:
                    item_count = 1
                    print("Following secrets exist in " + source_keyvaultname + " keyvault\n")
                    for items in keyvault_list_s:
                        print(str(item_count) + ". " + items)
                        item_count = item_count + 1
                    azure_keyvault_set_create_secret(source_keyvaultname)
                    input("\nPress enter to return main menu: ")
                    trigger = False
                else:
                    print("There is no secrets in " + source_keyvaultname + " keyvault")
                    azure_keyvault_set_create_secret(source_keyvaultname)
                    input("\nPress enter to return main menu: ")
                    trigger = False
            else:
                print("\nThere is no such keyvault")
                input("Press enter to return main menu: ")
                trigger = False

        elif answer == "ls":
            source_rg = input("\nPlease type RG name (default is " + default_rg + "): ") or default_rg
            source_keyvaultname = input("Please type vault name: ")
            print("Checking if " + source_keyvaultname + " already exist in " + source_rg + " Resource group")
            is_keyvault_exist = check_azure_keyvault(source_keyvaultname, source_rg)
            if is_keyvault_exist:
                secret_list_ls = azure_keyvault_secret_list(source_keyvaultname)
                if len(secret_list_ls) != 0:
                    item_count: int = 1
                    print("Following secrets exist in " + source_keyvaultname + "\n")
                    for items in secret_list_ls:
                        print(str(item_count) + ". " + items)
                        item_count = item_count + 1
                    input("\nPress enter to return main menu: ")
                    trigger = False
                else:
                    print("There is no secrets in " + source_keyvaultname + " keyvault")
                    input("\nPress enter to return main menu: ")
                    trigger = False
            else:
                print("There is no such keyvault")
                input("\nPress enter to return main menu: ")
                trigger = False

        elif answer == "sh":
            source_rg = input("\nPlease type RG name (default is " + default_rg + "): ") or default_rg
            source_keyvaultname = input("Please type vault name: ")
            print("Checking if " + source_keyvaultname + " already exist in " + source_rg + " Resource group")
            is_keyvault_exist = check_azure_keyvault(source_keyvaultname, source_rg)
            if is_keyvault_exist:
                print("Keyvalt " + source_keyvaultname + " exist")
                sleep(1)
                print("Retriving secret list from " + source_keyvaultname + " keyvault \n--Please wait--")
                secret_list_sh = azure_keyvault_secret_list(source_keyvaultname)
                if len(secret_list_sh) != 0:
                    azure_keyvault_secret_show(source_keyvaultname, secret_list_sh)
                    input("\nPress enter to return main menu: ")
                    trigger = False
                else:
                    print("There is no secrets in " + source_keyvaultname + " keyvault")
                    input("\nPress enter to return main menu: ")
                    trigger = False
            else:
                print("There is no such keyvault")
                input("\nPress enter to return main menu: ")
                trigger = False

        elif answer == "dk":
            source_rg = input("\nPlease type RG name (default is " + default_rg + "): ") or default_rg
            source_keyvaultname = input("Please type vault name: ")
            print("Checking if " + source_keyvaultname + " already exist in " + source_rg + " Resource group")
            is_keyvault_exist = check_azure_keyvault(source_keyvaultname, source_rg)
            if is_keyvault_exist:
                secret_list_dk = azure_keyvault_secret_list(source_keyvaultname)
                if len(secret_list_dk) == 0:
                    azure_keyvault_delete(source_keyvaultname, source_rg)
                    input("\nPress enter to return main menu: ")
                    trigger = False
                else:
                    print("There are " + str(len(secret_list_dk)) + " secrets exist in " +
                          source_keyvaultname + " keyvault")
                    delete_answer = input("Are you sure to delete (yes/no): ")
                    if delete_answer.casefold() == "yes":
                        azure_keyvault_delete(source_keyvaultname, source_rg)
                        input("\nPress enter to return main menu: ")
                        trigger = False
                    else:
                        input("\nPress enter to return main menu: ")
                        trigger = False
            else:
                print("\nThere is no such keyvault")
                input("Press enter to return main menu: ")
                trigger = False

        elif answer == "ds":
            source_rg = input("\nPlease type RG name (default is " + default_rg + "): ") or default_rg
            source_keyvaultname = input("Please type vault name: ")
            print("Checking if " + source_keyvaultname + " already exist in " + source_rg + " Resource group")
            is_keyvault_exist = check_azure_keyvault(source_keyvaultname, source_rg)
            sleep(1)
            if is_keyvault_exist:
                secret_list_ds = azure_keyvault_secret_list(source_keyvaultname)
                if len(secret_list_ds) != 0:
                    azure_keyvault_delete_secret(source_keyvaultname, secret_list_ds)
                    input("\nPress enter to return main menu: ")
                    trigger = False
                else:
                    print("There is no secrets in " + source_keyvaultname + " keyvault to delete")
                    input("\nPress enter to return main menu: ")
                    trigger = False
            else:
                print("There is no such keyvault")
                input("\nPress enter to return main menu: ")
                trigger = False

        elif answer == "br":
            source_rg = input("\nPlease type source RG name (default is " + default_rg + "): ") or default_rg
            source_keyvaultname = input("Please type source vault name: ")
            print("Checking if " + source_keyvaultname + " already exist in " + source_rg + " Resource group")
            is_source_keyvault_exist = check_azure_keyvault(source_keyvaultname, source_rg)

            if is_source_keyvault_exist:
                print("Keyvault " + source_keyvaultname + " exist in " + source_rg + " resource group")
                sleep(1)
                print("Retriving secrets from " + source_keyvaultname + " keyvault")
                source_keyvaultname_secret_list = azure_keyvault_secret_list(source_keyvaultname)

                if len(source_keyvaultname_secret_list) != 0:
                    source_keyvaultname_dict = azure_keyvault_secret_show_for_backup(source_keyvaultname, source_keyvaultname_secret_list)
                    print(source_keyvaultname_dict)
                    print("Backup completed")
                    sleep(1)
                    print("Starting resore process")
                    destination_rg = input("Please type destination RG name (default is " + default_rg +
                                           "): ") or default_rg
                    destination_keyvaultname = input("Please type destination vault name: ")
                    print("Checking if " + destination_keyvaultname + " keyvault already exist in destination" +
                          destination_rg + " Resource group")
                    is_destination_keyvault_exist = check_azure_keyvault(destination_keyvaultname, destination_rg)

                    if not is_destination_keyvault_exist:
                        print("destination " + destination_keyvaultname + " doesn't exist in destination" +
                              destination_rg + " resource group")
                        sleep(1)
                        print("Creating destination " + destination_keyvaultname + " keyvault in destination " +
                              destination_rg + " resource group")
                        azure_keyvault_create(destination_keyvaultname, destination_rg)
                        input("Press enter to start restore to destination " + destination_keyvaultname + " keyvault")
                        print("Creating secret/value for destination " + destination_keyvaultname + " Keyvault")
                        print(source_keyvaultname_dict)
                        azure_keyvault_set_create_secret_for_restor(destination_keyvaultname, source_keyvaultname_dict)
                        
                    else:
                        print("Destination " + destination_keyvaultname + " keyvault alerady exist")
                        input("Press enter to start restoration to destination " + destination_keyvaultname
                              + " keyvault: ")
                        print("Creating secret/value for destination " + destination_keyvaultname + " Keyvault")
                        print(source_keyvaultname_dict)
                        azure_keyvault_set_create_secret_for_restor(destination_keyvaultname, source_keyvaultname_dict)
                        
                else:
                    print("There is no secrets in " + source_keyvaultname + " keyvault to backup")
                    print("Back to main menu and create secrets first")
                    input("Press enter to return main menu: ")
                    trigger = False
            else:
                print("Source " + source_keyvaultname + " keyvault doesn't exist")
                print("Back to main menu and create keyvault first")
                input("\nPress enter to return main menu: ")
                trigger = False

        elif answer == "q":
            close_program()
            trigger = True

        else:
            print("\nthere is no such oparation key defined")
            trigger = False

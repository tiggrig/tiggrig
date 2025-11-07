import yaml
import json
import os
import time



user_profile = os.environ['USERPROFILE']
kube_path = user_profile+"\\.kube\\"
key = input("Enter the config name: ")
username = ""
clustername = ""
yamlik = {'apiVersion': 'v1', 'clusters': [], 'kind': 'Config', 'contexts': [], 'users': [] }
with open(kube_path+"config") as f:    
    pod = yaml.safe_load(f) 
    contexts = pod['contexts']
    for context in contexts:
        if context['name']==key:            
            contexts.remove(context)
            username+=context['context']['user']
            clustername+=context['context']['cluster']
            for line in contexts:
                yamlik["contexts"].append(line)    
                clusters = pod['clusters']                
                for cluster in clusters:
                    if clustername in str(cluster):           
                        clusters.remove(cluster)
                        #clusterdel+=str(cluster)            
                        for line in clusters:
                            yamlik["clusters"].append(line)                    
                users = pod['users']
                #print(users)
                for name in users:
                    if username in str(name):
                        users.remove(name)
                        for line in users:
                            yamlik["users"].append(line)
            with open(kube_path+"config", 'w') as outfile:
                yaml.dump(yamlik, outfile, default_flow_style=False)
            print("Config "+key+" deleted")            
        else:
            print("Config Name Not Found")
time.sleep(5)


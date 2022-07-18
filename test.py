import yaml, json

def walk(d):
    global path
    for k,v in d.items():
        if isinstance(v, str) or isinstance(v, int) or isinstance(v, float):
            path.append(k)
            print("{}={}".format(".".join(path), v))
            path.pop()
        elif v is None:
            path.append(k)
            ## do something special
            path.pop()
        elif isinstance(v, dict):
            path.append(k)
            walk(v)
            path.pop()
        else:
            print("###Type {} not recognized: {}.{}={}".format(type(v), ".".join(path),k, v))


# data={}
# data['images']=[]
# data['images'].append({'image': 'image1'})

# print(data)
# print(yaml.dump(data))



mydict = {'Other': {'Stuff': {'Here': {'Key': 'Value'}}}, 'root1': {'address': {'country': 'Brazil', 'city': 'Sao', 'x': 'Pinheiros'}, 'surname': 'Fabiano', 'name': 'Silos', 'height': 1.9}, 'root2': {'address': {'country': 'Brazil', 'detail': {'neighbourhood': 'Central'}, 'city': 'Recife'}, 'surname': 'My', 'name': 'Friend', 'height': 1.78}}

path = []
walk(mydict)


#"Even" if i%2==0 else "Odd" for i in range(10)
print([k if k=='Other' else v for k,v in mydict.items()])

with open('tmp.json','r') as input_file:
    #print(json.dumps(json.load(input_file),indent=4))
    data = json.load(input_file)
    walk(data)
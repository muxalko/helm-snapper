from textwrap import indent
import yaml
import json
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("helmchart_path", help="Specify your multi doc yaml file")
parser.add_argument("yaml_docs_file", help="Specify your multi doc yaml file")
args = parser.parse_args()


def yaml_as_python(val):
    """Convert YAML to dict"""
    try:
        return yaml.safe_load(val)
    except yaml.YAMLError as exc:
        return exc

def yamls_as_python(val):
    """Convert YAML to dict"""
    try:
        return yaml.safe_load_all(val)
    except yaml.YAMLError as exc:
        return exc


if __name__ == '__main__':
    #
    # read version from Charts.yaml
    with open(args.helmchart_path +'/Chart.yaml', 'r') as input_file:
        results = yaml_as_python(input_file)
        try:
            print(results['name']+'-'+results['version'])
        except KeyError as err:
                print("Oops!  There was no key {0} found.".format(err))

    # read all docs and iterate over to find Deployment kinds
    with open(args.yaml_docs_file, 'r') as input_file:
        results = yamls_as_python(input_file)
        for value in results:
            #print(json.dumps(value, indent=4))
            try:
                if value['REVISION']:
                    print("Revision: {0}".format(value['REVISION']))
            except KeyError as err:
                pass #print("Oops!  There was no key {0} found.".format(err))
            try:
                if value['kind'] == 'Deployment':
                    print(value['metadata']['name'])
                    for container in value['spec']['template']['spec']['containers']:
                        print("\t name: {0}, image: {1}".format(container['name'], container['image']))
            except KeyError as err:
                pass #print("Oops!  There was no key {0} found.".format(err))


    
from os import environ
from smtplib import SMTPSenderRefused
#from socket import send_fds
from kubernetes import client, config
import json
#import re
from docker_image import reference
from collections import Counter
import argparse


parser = argparse.ArgumentParser()
#parser.add_argument("environment", help="Environment to use when gathering metrics.", r)

args = parser.parse_args()

#environment = args.environment
#print(environment)
#pattern_text = r'(?P<ingredient>\w+):\s+(?P<amount>\d+)\s+(?P<unit>\w+)'
#pattern = re.compile(pattern_text)
#match = pattern.match(ingredient)>>> match is NoneFalse>>> match.groups()

registry_host = 'harbor.rogers.lab'
namespace_filter = ['kube-system','tca-system','tkg-system']

namespaces = []
images = []
nodes = []
tags = {}

# Configs can be set in Configuration class directly or using helper utility
config.load_kube_config()
#config.load_kube_config(
#            config_file=environ['KUBECONFIG'],
#            context="rtrm-"+environment+"-admin@rtrm-"+environment)

# conf = config.list_kube_config_contexts()[1]
# print(json.dumps(conf, indent=4))
contexts, active_context = config.list_kube_config_contexts()
if not contexts:
    print("Cannot find any context in kube-config file.")
    exit(1)
#contexts = [context['name'] for context in contexts]
#active_index = contexts.index(active_context['name'])
cluster = active_context['context']['cluster']

v1 = client.CoreV1Api()
#print("Listing pods with their IPs:")
ret = v1.list_pod_for_all_namespaces(watch=False)

#ret = v1.list_namespaced_pod('ecs',watch=False)
#print("%s\t%s\t%s\t%s" % ('IP', 'NAMESPACE', 'NAME', 'IMAGE'))
for i in ret.items:
    nodes.append((i.spec.node_name,i.metadata.namespace))
    #namespaces.append(i.metadata.namespace)
    if i.metadata.namespace not in namespace_filter:
        for j in i.spec.containers:
            ref = reference.Reference.parse(j.image)
            hostname, image_name = ref.split_hostname()
            #print('namespace: {}, image_name: {}, tag: {}'.format(i.metadata.namespace, image_name, ref['tag']))
            if ref['tag'] is not None:
                images.append(image_name + ":" + ref['tag'])
            
                # TODO: need to check case when the same image with different version is used
                if image_name not in tags:
                    tags[image_name] = ref['tag']
            # #print(ref)
            # if ref['tag']:
            #     print("%s\t%s\t%s" % (i.metadata.namespace, j.name, ref['name'], ref['tag']))
            # else:
            #     print("%s\t%s\t%s" % (i.metadata.namespace, j.name, ref['name'], ref['digest']))
            # #print("\n")
            # #print(json.dumps(i.metadata))
            # #print("%s\t%s\t%s\t%s" % (i.status.pod_ip, i.metadata.namespace, i.metadata.name, j.image))
            # #print("%s\t%s" % (j.name, j.image))
            # #print(ref)

# counter_ns = Counter(namespaces)
# print('# HELP amount_pods The total amount of pods in namespace running on a cluster')
# print('# TYPE amount_pods gauge')
# for ns in counter_ns:
#     print('amount_pods{environment=\"%s\", namespace=\"%s\"} %i' % (cluster.split('-')[1], ns, node_name, counter_ns[ns])) 

counter_n = Counter(nodes)
print('# HELP amount_pods The total amount of pods in namespace running on a cluster')
print('# TYPE amount_pods gauge')
for (node,ns) in counter_n:
    print('amount_pods{environment=\"%s\", node_name=\"%s\", namespace=\"%s\"} %i' % (cluster.split('-')[1], node, ns, counter_n[(node,ns)])) 


print()
counter_images = Counter(images)
print('# HELP amount_images The total amount of image usages')
print('# TYPE amount_images gauge')
for image in counter_images:
    print('amount_images{environment=\"%s\", image=\"%s\"} %i' % (cluster.split('-')[1], image, counter_images[image])) 
    
print()
print('# HELP images The current images versions')
print('# TYPE images gauge')
for i in tags.keys():
    print('images{environment=\"%s\", image=\"%s\", tag=\"%s\"} %i' % (cluster.split('-')[1], i, tags[i], counter_images[i+":"+tags[i]]))


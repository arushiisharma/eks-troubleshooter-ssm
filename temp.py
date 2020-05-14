from __future__ import print_function
from sys import argv
import boto3
import json
import sys
from reportlab.pdfgen import canvas


# 1.Modification to  subnetTagsCheck(taken as an example) to confirm if the ec2 has any tags or not else it is giving error when its not there along with try catch.
# - To run: python3 temp.py <clustername> <region>
# 2.The output i.e the subnet IDS are printed to a pdf file uses PyPDF2 library for the same
# 3.Same way could use it as per req to print anything to pdf to make the report.

# TIP: Need to handle error scenarios in all scripts as we are not handling any wrong input or exceptions.

point = 1
inch = 72

def subnetTagsCheck(clusterName,reg='us-east-1'):
    elbKey = 0
    key = 0
    try:
        client = boto3.client('ec2')
        response = client.describe_subnets()
        subnets = response['Subnets']
        subnet_ids=[]
        for subnet in subnets:
            subnet_ids.append(subnet['SubnetId'])
        print(json.dumps(subnet_ids, indent=4, sort_keys=True, default=str))
        region = reg
        eksClient = boto3.client('eks', region_name=region)
        ec2 = boto3.resource('ec2', region_name=region)
        for subnetId in subnet_ids:
            elbKey = 0
            key = 0
            if(ec2.Subnet(subnetId).tags is not None):
                for tag in ec2.Subnet(subnetId).tags:
                    if(tag is not None):
                        if(str('kubernetes.io/cluster/'+clusterName) in tag.values()):
                            key=1
                            if('shared' not in tag.values()):
                                print("Add", 'kubernetes.io/cluster/'+clusterName, "shared tag in subnet",subnetId)
                        if('kubernetes.io/role/elb' in tag.values() or 'kubernetes.io/role/internal-elb' in tag.values()):
                            elbKey = 1
                            if('1' not in tag.values()):
                                print("Add 'For private subnets- kubernetes.io/role/internal-elb -> 1'  or 'For public subnets- kubernetes.io/role/elb -> 1' tag in the subnet",subnetId)
                if(not elbKey):
                    print("Add 'kubernetes.io/role/internal-elb -> 1' tag for private subnets or 'kubernetes.io/role/elb -> 1' tag for public subnets:",subnetId)
                if(not key):
                    print("Add", 'kubernetes.io/cluster/'+clusterName, "shared tag in subnet",subnetId)
    except:
        print('Error occured try adding corresponding exception catch')
    return subnet_ids

def designPDF(output_filename, arr):
    title = output_filename
    c = canvas.Canvas(output_filename, pagesize=(8.5 * inch, 11 * inch))
    c.setStrokeColorRGB(0,0,0)
    c.setFillColorRGB(0,0,0)
    c.setFont("Helvetica", 12 * point)
    v = 10 * inch
    c.drawString( 1 * inch, v,"Subnet IDs are:")
    c.drawString( 1 * inch, v,"")
    v -= 24 * point
    for subtline in arr:
        c.drawString( 1 * inch, v, subtline )
        v -= 12 * point
    c.showPage()
    c.save()

subIds=subnetTagsCheck(sys.argv[1],sys.argv[2])
designPDF("abc.pdf",subIds)
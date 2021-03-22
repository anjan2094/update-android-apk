#!/usr/bin/python

import sys
import base64
import json
import urllib2
import hashlib
import requests
import os
import subprocess

#file_link = sys.argv[1]
#file_name = sys.argv[2]
TEMPLATE_ID = sys.argv[1]

def upload_to_blackblaze(file_link, file_name):
    try:
        print("starting to upload to blackblaze")
        print(file_link)
        print("above is file link")
        print(file_name)
        print("above is file name")
        id_and_key = '8bfecb0cb73d:0027032eef12cc74e72360f3abe374739b9b90ef3e'
        basic_auth_string = 'Basic ' + base64.b64encode(id_and_key)
        headers = { 'Authorization': basic_auth_string }

        request = urllib2.Request(
            'https://api.backblazeb2.com/b2api/v2/b2_authorize_account',
            headers = headers
            )
        response = urllib2.urlopen(request)
        response_data = json.loads(response.read())
        response.close()
        #print(response_data)
        account_authorization_token = response_data['authorizationToken']

        api_url = 'https://api002.backblazeb2.com/b2api/v2/b2_get_upload_url'
        bucket_id = '985bbf9ebcfbe08c7b37031d'
        request2 = urllib2.Request(
            api_url,
            json.dumps({ 'bucketId' : bucket_id }),
            headers = { 'Authorization': account_authorization_token }
            )
        response = urllib2.urlopen(request2)
        response_data = json.loads(response.read())
        #print(response_data)
        upload_url = response_data['uploadUrl']
        upload_authorization_token= response_data['authorizationToken']
        with open(file_link, 'rb') as content_file:
            file_data = content_file.read()
        content_type = "application/vnd.android.package-archive"

        headers = {
            'Authorization' : upload_authorization_token,
            'X-Bz-File-Name' :  file_name,
            'Content-Type' : content_type,
            'X-Bz-Content-Sha1' : 'do_not_verify'
            }

        r = requests.post(upload_url, headers=headers, data=file_data)

        print(r.json())
        return
    except:
        print("Error in upload_to_blackblaze method")
        e = sys.exc_info()[0]
        print(e)   

def FlockSend(message):
    try:
        print('sending flock msg')
        url = 'https://api.flock.com/hooks/sendMessage/d05c26fd-5402-4174-bb63-f664ba35a17b'
        dd = {"text" : message}
        response = requests.post(url, data = json.dumps(dd), headers = {"Content-Type" : "application/json"})
        print(response)
        return
    except:
        print("Error in Flock Send")
        e = sys.exc_info()[0]
        print(e)


def getShellResponse(cmd):
    try:    
        output = subprocess.check_output(cmd, shell=True)
        return output[:len(output) - 1]
    except:
        print("Error in getShellResponse")
        e = sys.exc_info()[0]
        print(e)


def changeVersionProperties(propertyName, propertyValue):
    try:

        cmd = """sed -i "s/${propertyName}=[^ ]*/${propertyName}=${propertyValue}/g" version.properties"""
        cmd = cmd.replace("${propertyName}", propertyName).replace("${propertyValue}", propertyValue)
        print("Changing Campaign Name")
        os.system(cmd)
    except:
        print("Error in changeVersionProperties")
        e = sys.exc_info()[0]
        print(e)


def readVersionProperties(propertyName):
    try:
        print(propertyName)
        print('property name above')
        cmd = """cat version.properties | grep -w ${propertyName} | cut -d'=' -f2"""
        cmd = cmd.replace("${propertyName}", propertyName)
        output = getShellResponse(cmd)
        print("version is ")
        print(output)
        return output
    except:
        print("Error in readVersionProperties")
        e = sys.exc_info()[0]
        print(e)


# def fetchAllEligibleCampaigns(currentApkVersion):
#     try:
#         url = 'https://api.sportscafe.in/v3/game/web/getActiveCampaigns?secret_key=HalleluahMrAlderson&version_code=' + str(currentApkVersion)
#         print(url)
#         request = urllib2.Request(url)
#         response = urllib2.urlopen(request)
#         response_data = json.loads(response.read())
#         return response_data
#     except:
#         print("Error in fetchAllEligibleCampaigns")
#         e = sys.exc_info()[0]
#         print(e)


def updateCampaignApk(campaignName, VERSION_CODE, app_link):
    try:
        url = 'https://api.sportscafe.in/v3/game/web/updateCampaignApk'
        #remove unicode
        app_link = app_link.encode('ascii', 'ignore')
        campaignName = campaignName.encode('ascii', 'ignore')

        dd = { 'app_link' : app_link, 'template_id' : campaignName, 'version_code' :  int(VERSION_CODE), 'secret_key' : 'HalleluahMrAlderson'}

        response = requests.post(url, data = dd)
        print(response)
        print(response.status)
        print(response.reason)
        return
    except:
        print("Error in updateCampaignApk")
        e = sys.exc_info()[0]
        print(e)      

def generateAndroidBuild(campaignName):
    try:

        changeVersionProperties("CAMPAIGN_NAME", campaignName)
        os.system(""" ./gradlew clean :app:assembleNostragamusProRelease """)
        os.system(""" mkdir -p ./final_builds """)
        os.system(""" mv ./app/build/outputs/apk/NostragamusPro/release/*.apk ./final_builds/ """)
        return
    except:
        print("Error in generateAndroidBuild")
        e = sys.exc_info()[0]
        print(e)



def ApkLink(VERSION_NAME, campaign):
    try:
        return "https://f002.backblazeb2.com/file/nostrapro/NostragamusPro-" + VERSION_NAME + "-" + campaign + ".apk"
    except:
        print("Error in ApkLink")
        e = sys.exc_info()[0]
        print(e)


def main():

    VERSION_CODE = readVersionProperties("VERSION_CODE")
    VERSION_NAME = readVersionProperties("VERSION_NAME")
    VERSION_CODE = readVersionProperties("VERSION_CODE")
    STABLE_VERSION_NAME= readVersionProperties("STABLE_VERSION_NAME")
    # allCampaignDict = fetchAllEligibleCampaigns(STABLE_VERSION_CODE)

    # for campaign in allCampaignDict[:3]:
    campaignName = "searchmoney"
    FlockSend("Started generating build for Campaign = " + campaignName)
    output_files = generateAndroidBuild(campaignName)
    file_name = "NostragamusPro-" + VERSION_NAME + "-" + campaignName + ".apk"
    file_link = "./final_builds/" + file_name
    # upload_to_blackblaze(file_link, file_name)
    print("Output File = " + output_files)
    # updateCampaignApk(campaignName, VERSION_CODE, ApkLink(VERSION_NAME, campaignName))
    FlockSend("Updated Apk for Campaign = " + campaignName + " -- " + ApkLink(VERSION_NAME, campaignName))
    print("LOOP OVER")

    # for campaign_names in allCampaignDict:
    cName = "searchmoney"
    print("Download link = " + ApkLink(VERSION_NAME, cName))


if __name__ == '__main__':
    main()

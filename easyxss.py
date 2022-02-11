import urllib.parse as urlparse
import requests
from colorama import init , Style, Back,Fore
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import requests
import time
import argparse
import concurrent.futures
from slack import WebClient
from slack.errors import SlackApiError
import re

# ToDO
# [+] Support for cookies

def log0():

    # Because no tool is complete without logo ;) xD

    print("""
                                                            
        ___      ___      ___                       ___      ___    
      //___) ) //   ) ) ((   ) ) //   / / \\ / /  ((   ) ) ((   ) ) 
     //       //   / /   \ \    ((___/ /   \/ /    \ \      \ \     
    ((____   ((___( ( //   ) )      / /    / /\ //   ) ) //   ) )     
    

    EasyXSS - Find reflection of multiple parameters
    Author: Splint3r7 - ( https://github.com/Splint3r7 )               

        """) 

parser = argparse.ArgumentParser(description="Identify Reflection in parameters")

parser.add_argument('-f','--list',
                            help = "List of urls with parameters",
                            type = str,
                            required = False)
parser.add_argument('-t','--slacktoken',
                            help = "Slack Token",
                            type = str,
                            required = False)

parser.add_argument('-o','--output',
                            help = "Output file",
                            type = str,
                            required = False)

args = parser.parse_args()

def send_to_slack_inner(_token_ , _channel_, _message_):

    client = WebClient(token="{}".format(_token_))

    response = client.chat_postMessage(
        channel="#{}".format(_channel_),
        username="Automation Bot",
        blocks=[{"type": "section",
        "text": 
        {"type": "mrkdwn",
        "text": "{}".format(_message_)}}]
        )

def send_to_slack(_token_ , _channel_, _message_):
    try:
        response = send_to_slack_inner(_token_ , _channel_, _message_)
    except SlackApiError as e:
        if e.response["error"] == "ratelimited":
            delay = int(e.response.headers['Retry-After'])
            print(f"Rate limited. Retrying in {delay} seconds")
            time.sleep(10)
            response = send_to_slack_inner(_token_ , _channel_, _message_)
        else:
            raise e
            
def generatig_params(_Url_, _Triggers_):

    result = []

    _Url_ = _Url_.rstrip()
    parsed = urlparse.urlparse(_Url_)
    querys = parsed.query.split("&")
    for pairs in _Triggers_:
        new_query = "&".join([ "{}{}".format(query, pairs) for query in querys])
        parsed = parsed._replace(query=new_query)
        result.append(urlparse.urlunparse(parsed))

    return result

def cleanParams(url, triggers):
    
    param = ""
    empty = ""

    url = url.rstrip()
    parsed = urlparse.urlparse(url)
    querys = parsed.query.split("&")
    lista = []
    for n in querys:
        x = re.sub("[=].*", "={}".format(empty), n)
        lista.append(x)

    result = []
    for pairs in triggers:
        new_query = "&".join([ "{}{}".format(query, pairs) for query in lista])
        parsed = parsed._replace(query=new_query)
        result.append(urlparse.urlunparse(parsed))

    for i in result:
        param = i

    return param

def xss(_URL_):

    headers = {
    'User-Agent' : 'Mozilla/5.0 (X11; Linux x86_64; rv:63.0) Gecko/20100101 Firefox/63.0'
    }

    triggersHTMLConText = ['"><testXSS', "</x>testXSS", '"testXSS']

    payloadedUrl = generatig_params(_URL_, triggersHTMLConText) 

    for url in payloadedUrl:
        try:
            req = requests.get(url, verify=False, allow_redirects=False, timeout=7, headers=headers)
            print(Style.DIM+Fore.WHITE+"[+] Testing "+Style.RESET_ALL+"| "+Style.BRIGHT+Fore.BLUE+url+Style.RESET_ALL)
            for payload in identifiers:
                if payload in req.text:
                    print(Style.BRIGHT+Fore.RED+"[!] Vulnerable "+Style.RESET_ALL+"| {}".format(url)+" | "+Style.BRIGHT+Fore.GREEN+"identifier: "+Style.RESET_ALL+"["+Style.DIM+Fore.YELLOW+payload+Style.RESET_ALL+"]")
                    xss_out.write(url+"\n")
                    slack_data = "<!channel> Reflection Found ```{}```".format(url)
                    #send_to_slack(args.slacktoken, "reflected-xss", slack_data)
        except Exception as e:
            print(e)
            #print("SITE IS NOT UP | {}".format(url))

def run_xss_scan(_function_, _listUrls_):
    with concurrent.futures.ThreadPoolExecutor(max_workers=200) as executor:
        executor.map(_function_, _listUrls_)

if __name__ == "__main__":

    log0()
    identifiers = ['"><testXSS', "</x>testXSS", '"testXSS']
    xss_out = open(args.output, "w")

    arr = []
    with open(args.list, "r") as domain:
        lines = domain.readlines()
        for i in lines:
            i = i.strip()
            arr.append(i)
        
    run_xss_scan(xss, arr)

    xss_out.close()    

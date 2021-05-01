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
                            required = True)
parser.add_argument('-t','--slacktoken',
                            help = "Slack Token",
                            type = str,
                            required = False)

parser.add_argument('-o','--output',
                            help = "Output file",
                            type = str,
                            required = True)

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


def xss(_URL_):

    headers = {
    'User-Agent' : 'Mozilla/5.0 (X11; Linux x86_64; rv:63.0) Gecko/20100101 Firefox/63.0'
    }

    try:
        req = requests.get(_URL_, verify=False, allow_redirects=False, timeout=7, headers=headers)
        print(Style.DIM+Fore.WHITE+"[+] Testing "+Style.RESET_ALL+"| "+Style.BRIGHT+Fore.BLUE+_URL_+Style.RESET_ALL)
        for payload in identifiers:
            if payload in req.text:
                print(Style.BRIGHT+Fore.RED+"[!] Vulnerable "+Style.RESET_ALL+"| {}".format(_URL_)+" | "+Style.BRIGHT+Fore.GREEN+"identifier: "+Style.RESET_ALL+"["+Style.DIM+Fore.YELLOW+payload+Style.RESET_ALL+"]")
                xss_out.write(_URL_+"\n")
                slack_data = "<!channel> Reflection Found ```{}```".format(_URL_)
                send_to_slack(args.slacktoken, "reflected-xss", slack_data)
    except Exception as e:
        print("SITE IS NOT UP | {}".format(url))
        pass

if __name__ == "__main__":

    scan = input("[1] SQL injection \n[2] Cross Site Scripting \n[-]Select 1/2: ")

    if scan == "1":
    
        payloads = [
        "'", 
        "\"", 
        "\/", 
        "\"\"", 
        "%27", 
        "%22", 
        ")",
        "("]

        identifiers = [
        "You have an error in your SQL syntax", 
        "ORA-00933: SQL command not properly ended", 
        "Microsoft SQL Native Client error", 
        "MySQL Error: 1064", 
        "SQL syntax error", 
        "PostgreSQL query failed: ERROR: parser: parse error", 
        "PSQLException", 
        "SQLiteException", 
        "ODBC Microsoft Access", 
        "OracleException"]

    if scan == "2":
        payloads = ["testXSS"]
        identifiers = ["testXSS"]


    log0()

    xss_out = open(args.output, "w")

    def run_xss_scan(_function_, _listUrls_):
        with concurrent.futures.ThreadPoolExecutor(max_workers=25) as executor:
            executor.map(_function_, _listUrls_)

    with open(args.list, "r") as domain:
        lines = domain.readlines()

    for line in lines:
        line = line.strip()

        urls = generatig_params(line, payloads)
        run_xss_scan(xss, (urls))

    xss_out.close()    

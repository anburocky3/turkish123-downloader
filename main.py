import json
import os
import re
import sys
import urllib.request
from signal import signal, SIGINT

import requests
from art import text2art
from bs4 import BeautifulSoup
from colored import fg, attr
from terminaltables import AsciiTable
from tqdm.auto import tqdm

sys.stdout = sys.__stdout__

reset = attr('reset')

searching_color = fg("green")

rows, columns = os.popen('stty size', 'r').read().split()

version = "1.0.0"

# BASE URL
base_url = 'https://turkish123.com/'

movie_title = ''


def search_movies(query):
    search_result_table = [["Index", "Drama Name"]]

    print(searching_color + "[*] Searching for " + query + "....." + reset)

    drama_details_urls = []

    drama_names = []

    my_obj = {'s': query, 'action': 'searchwp_live_search', 'swpengine': 'default', 'swpquery': query}
    result = requests.post(base_url + 'wp-admin/admin-ajax.php', data=my_obj).text

    print(len(result))

    if len(result) == 0:
        print(f"{fg('red')}[*] No results found for {query}!{reset}")
        exit()

    soup = BeautifulSoup(result, "html.parser")

    drama_titles = soup.find_all('a', {'class': 'ss-title'})

    for drama_title in drama_titles:
        drama_names.append(drama_title.text)
        drama_details_urls.append(drama_title['href'])

    for i in range(len(drama_names)):
        search_result_table.append([str(i + 1), drama_names[i]])

    table = AsciiTable(search_result_table)
    table_color = fg("#66e887")
    print(table_color + table.table + reset)
    print()
    print(searching_color + "[*] Total Results " +
          str(len(drama_names)) + '\n' + reset)

    drama_choice = int(
        input("Enter the index number of the drama you want to scrape: ")) - 1
    print()

    global movie_title
    movie_title = drama_names[drama_choice]
    get_episodes_url(drama_details_urls[drama_choice].replace("'", ""))

    # print(x.text)


def yes_or_no(question):
    while "the answer is invalid":
        reply = str(input(f'{fg("yellow")}{question}{reset} (y/n): ')).lower().strip()
        if reply[:1] == 'y':
            return True
        if reply[:1] == 'n':
            return False


def check_script(movie_detail_url, episode):
    result = requests.get(movie_detail_url).text
    soup = BeautifulSoup(result, "html.parser")
    iframe_obj = soup.body.find(text=re.compile('<iframe width="560" height="315" src="'))
    regex = r"(?:(?:https):\/\/)?[\w\/\-?=%.]+\.[\w\# \/\-&?=%.]+"
    m = re.findall(regex, iframe_obj)
    if m:
        found_url = m[1]
        # file_name = found_url.rsplit('#', 1)[-1]
        file_name = f'Episode #{episode}.mp4'
        video_key = found_url.rsplit('/', 1)[-1]
        # print(f"""
        # found_url: {found_url},
        # file_name: 'Episode #{episode}.mp4,
        # video_key: {video_key},
        # movie_name: {movie_title}
        # """)
        download_video_from_internet(video_key, movie_title, file_name)
    else:
        print(f'Error in finding: ${movie_detail_url}')


def get_episodes_url(movie_detail_url):
    episode_result_table = [["Index", "Drama Name"]]

    result = requests.get(movie_detail_url).text
    soup = BeautifulSoup(result, "html.parser")

    download_list = []

    download_links = soup.find_all(attrs={'class': 'episodi'})

    #
    for index, link in enumerate(download_links):
        movie_name_with_episode = link['href'].rsplit('/', 2)
        episode_result_table.append([str(index + 1), movie_name_with_episode[1].capitalize()])
        download_list.append(link['href'])
    #

    # for i in range(len(download_list)):
    #     search_result_table.append([str(i + 2), download_list[i]])

    table = AsciiTable(episode_result_table)
    table_color = fg("#66e887")
    print(table_color + table.table + reset)
    print()
    print(searching_color + "[*] This Movie/Drama(" + movie_title + ") has " +
          str(len(download_list)) + " Episodes.\n\n" + reset)

    decision = yes_or_no('Do you want to download it all?')

    if decision:
        for episode, single_movie in enumerate(download_list):
            check_script(single_movie, episode + 1)
    else:
        print(f'{fg("red")}Okay Caption! Exiting...{reset}')
        exit(0)


class TqdmUpTo(tqdm):
    """Provides `update_to(n)` which uses `tqdm.update(delta_n)`."""

    def update_to(self, b=1, bsize=1, tsize=None):
        """
        b  : Blocks transferred so far
        bsize  : Size of each block
        tsize  : Total size
        """
        if tsize is not None:
            self.total = tsize
        self.update(b * bsize - self.n)


#
#
def downloadVideoToLocal(download_url, file_name, download_location):
    with TqdmUpTo(unit='B', unit_scale=True, unit_divisor=1024, miniters=1,
                  desc=file_name) as t:  # all optional kwargs
        urllib.request.urlretrieve(
            download_url, filename=download_location, reporthook=t.update_to, data=None)
        t.total = t.n


#
#
def download_video_from_internet(video_key, movie_title, file_name):
    headers = {
        'authority': 'lajkema.com',
        'content-length': '0',
        'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="90", "Google Chrome";v="90"',
        'accept': '*/*',
        'x-requested-with': 'XMLHttpRequest',
        'sec-ch-ua-mobile': '?0',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/90.0.4430.93 Safari/537.36',
        'origin': 'https://lajkema.com',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'referer': 'https://lajkema.com/f/' + video_key,
        'accept-language': 'en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7',
    }

    response = requests.post('https://lajkema.com/api/source/' + video_key, headers=headers)

    response_data = response.text
    data = json.loads(response_data)

    downloadable_url = data['data'][0]['file']

    download_path = f'downloaded/{movie_title}'

    # Clear screen
    os.system('cls' if os.name == 'nt' else 'echo -e \\\\033c')

    print(f"\n\nDownloading episode from {file_name} to {download_path}/{file_name} \n\n")

    if not os.path.exists(download_path):
        os.makedirs(download_path)

    downloadVideoToLocal(downloadable_url, file_name, download_path + '/' + file_name)


# getVideo()
# Save it in local disk


def show_main_screen():
    os.system("title " + "Turkish123 Downloader  Anbuselvan Rocky")
    os.system('cls' if os.name == 'nt' else 'echo -e \\\\033c')

    available_columns = int(columns)

    art = text2art("Turkish  123   GRABBER")
    print(fg("red") + art + reset)
    print(f"{fg('#0ecf12')}*" * available_columns + reset)
    print(
        f"{fg('#0ecf12')}\t\t Developed by:{reset} {fg('#fff')}Anbuselvan Rocky,{reset} {fg('#48B8FF')}v"
        f"{version}{reset}".center(available_columns))
    print(f"{fg('#0ecf12')}*" * available_columns + "\n" + reset)

    movie_name = input("What movie are you searching?: \t")
    search_movies(movie_name)


def handler(signal_received, frame):
    print(f"{fg('red')} \n\nWant to quit?. Exiting gracefully.. Good Bye!" + reset)
    sys.exit(0)


if __name__ == "__main__":
    signal(SIGINT, handler)
    show_main_screen()

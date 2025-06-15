import os
import sys
import urllib.request
from signal import signal, SIGINT

import requests
from art import text2art
from bs4 import BeautifulSoup
from colored import Fore, attr
from terminaltables import AsciiTable
from tqdm.auto import tqdm

sys.stdout = sys.__stdout__

reset = attr('reset')

searching_color = Fore.rgb(0, 255, 0)  # Green color

rows, columns = os.popen('stty size', 'r').read().split()

version = "2.0.0"

# BASE URL
base_url = 'https://hds.turkish123.com/'

movie_title = ''


def search_movies(query):
    search_result_table = [["Index", "Drama Name"]]

    print(searching_color + "\n[*] Searching for " + query + "....." + reset + '\n')

    drama_details_urls = []

    drama_names = []

    my_obj = {'s': query, 'action': 'searchwp_live_search', 'swpengine': 'default', 'swpquery': query}
    result = requests.post(base_url + 'wp-admin/admin-ajax.php', data=my_obj).text

    if len(result) == 0:
        print(f"{Fore.rgb(255, 0, 0)}[*] No results found for {query}!{reset}")  # Red color
        exit()

    soup = BeautifulSoup(result, "html.parser")

    drama_titles = soup.find_all('a', {'class': 'ss-title'})

    for drama_title in drama_titles:
        drama_names.append(drama_title.text)
        drama_details_urls.append(drama_title['href'])

    for i in range(len(drama_names)):
        search_result_table.append([str(i + 1), drama_names[i]])

    table = AsciiTable(search_result_table)
    table_color = Fore.rgb(102, 232, 135)  # Light green color
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
        reply = str(input(f'{Fore.rgb(255, 255, 0)}{question}{reset} (y/n) {Fore.rgb(128, 128, 128)}(default: y){reset}: ')).lower().strip() or 'y'  # Default to 'y'
        if reply[:1] == 'y':
            return True
        if reply[:1] == 'n':
            return False


def check_script(movie_detail_url, episode):
    result = requests.get(movie_detail_url).text
    soup = BeautifulSoup(result, "html.parser")

    anchor_tag = soup.find('div', class_='download_navi').find('ul', class_='dlTabsi').find('li').find('a')

    # Extract the href attribute
    if anchor_tag:
        src = anchor_tag['href']
        print(f"Anchor href: {src}")
        download_url = requests.get('https://tokvoy.com/d/spyprrodgshd_n').text
        soup = BeautifulSoup(download_url, "html.parser")
        download_orig = soup.find('input', attrs={'name': 'op'}).get('value')
        movie_id = soup.find('input', attrs={'name': 'id'}).get('value')
        mode = soup.find('input', attrs={'name': 'mode'}).get('value')
        hash = soup.find('input', attrs={'name': 'hash'}).get('value')

        download_video_from_internet(movie_id, download_orig, mode, hash, episode)

    else:
        print("Anchor tag not found.")


    # regex = r"(?:(?:https):\/\/)?[\w\/\-?=%.]+\.[\w\# \/\-&?=%.]+"
    # print(f"{searching_color}[*] Checking - {iframe_obj} - {result}...{reset}")
    # m = re.findall(regex, iframe_obj)
    # if m:
    #     found_url = m[1]
    #     # file_name = found_url.rsplit('#', 1)[-1]
    #     file_name = f'Episode #{episode}.mp4'
    #     video_key = found_url.rsplit('/', 1)[-1]
    #     # print(f"""
    #     # found_url: {found_url},
    #     # file_name: 'Episode #{episode}.mp4,
    #     # video_key: {video_key},
    #     # movie_name: {movie_title}
    #     # """)
    #     download_video_from_internet(video_key, movie_title, file_name)
    # else:
    #     print(f'Error in finding: ${movie_detail_url}')


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
    table_color = Fore.rgb(102, 232, 135)  # Light green color
    print(table_color + table.table + reset)
    print()
    print(searching_color + "[*] This Movie/Drama(" + movie_title + ") has " +
          str(len(download_list)) + " Episodes.\n\n" + reset)

    decision = yes_or_no('Do you want to download it all?') or True

    if decision:
        for episode, single_movie in enumerate(download_list):
            check_script(single_movie, episode + 1)
    else:
        print(f'{Fore.rgb(255, 0, 0)}Okay Caption! Exiting...{reset}')  # Red color
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
    print(Fore.rgb(0, 255, 0))  # Green color
    with TqdmUpTo(unit='B', unit_scale=True, unit_divisor=1024, miniters=1,
                  desc=file_name) as t:  # all optional kwargs
        urllib.request.urlretrieve(
            download_url, filename=download_location, reporthook=t.update_to, data=None)
        t.total = t.n
        print(reset)


#
#
def download_video_from_internet(movie_id, download_orig, mode, hash, episode):
    headers = {
        'accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language':'"en-IN,en;q=0.9,kn;q=0.8,en-GB;q=0.7,ta;q=0.6"',
        'cache-control':'max-age=0',
        'content-type':'application/x-www-form-urlencoded',
        'origin':'https://tokvoy.com',
        'priority':'u=0, i',
        'referer': '"https://tokvoy.com/d/' + movie_id + '_' + mode,
        'sec-ch-ua':'"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
        'sec-ch-ua-mobile':'?0',
        'sec-ch-ua-platform':'"Windows"',
        'sec-fetch-dest':'document',
        'sec-fetch-mode':'navigate',
        'sec-fetch-site':'same-origin',
        'sec-fetch-user':'?1',
        'upgrade-insecure-requests':'1',
        'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
        'Cookie':'lang=1'
    }

    print(f"{searching_color}[*] Downloading {movie_title} - Episode {episode}...{reset}"'')

    final_url = 'https://tokvoy.com/d/' + movie_id + '_' + mode

    print(f'Requesting video: {final_url}')

    my_obj = {'op': download_orig, 'id': movie_id, 'mode': mode, 'hash': hash}

    response = requests.post(final_url, data=my_obj, headers=headers)

    response_data = response.text

    soup = BeautifulSoup(response_data, "html.parser")

    download_span_tag = soup.find('span')

    if download_span_tag:
        downloadable_url = download_span_tag.find('a')['href']

        if downloadable_url:
            file_name = f'Episode #{episode}.mp4'

            download_path = f'downloaded/{movie_title}'

            # Clear screen
            os.system('cls' if os.name == 'nt' else 'echo -e \\\\033c')

            print(f"\n\nDownloading episode from {Fore.rgb(255, 255, 0)}{episode}{reset} to "
              f"{Fore.rgb(255, 255, 0)}{download_path}/{file_name}{reset} \n")  # Yellow color


            if not os.path.exists(download_path):
                os.makedirs(download_path)

            downloadVideoToLocal(downloadable_url, file_name, download_path + '/' + file_name)
        else:
            print(f'Error in finding: ${final_url}')
    else:
        print(f"{Fore.rgb(255, 0, 0)}Error: Download link not found in the response.{reset}")





    # data = json.loads(response_data)
    #
    # downloadable_url = data['data'][0]['file']
    #
    # download_path = f'downloaded/{movie_title}'
    #
    # # Clear screen
    # os.system('cls' if os.name == 'nt' else 'echo -e \\\\033c')
    #
    # print(f"\n\nDownloading episode from {Fore.rgb(255, 255, 0)}{file_name}{reset} to "
    #   f"{Fore.rgb(255, 255, 0)}{download_path}/{file_name}{reset} \n")  # Yellow color
    #
    #
    # if not os.path.exists(download_path):
    #     os.makedirs(download_path)
    #
    # downloadVideoToLocal(downloadable_url, file_name, download_path + '/' + file_name)


# getVideo()
# Save it in local disk


def show_main_screen():
    os.system("title " + "Turkish123 Downloader  Anbuselvan Annamalai")
    os.system('cls' if os.name == 'nt' else 'echo -e \\\\033c')

    available_columns = int(columns)

    art = text2art("Turkish  123   GRABBER")
    print(Fore.rgb(255, 0, 0) + art + reset)  # Red color
    print(f"{Fore.rgb(14, 207, 18)}*" * available_columns + reset)  # Green color
    print(
        f"{Fore.rgb(14, 207, 18)}\t\t Developed by:{reset} {Fore.rgb(255, 255, 255)}Anbuselvan Rocky,{reset} {Fore.rgb(72, 184, 255)}v"
        f"{version}{reset}".center(available_columns))
    print(f"{Fore.rgb(14, 207, 18)}*" * available_columns + "\n" + reset)

    movie_name = input("What movie are you searching?: \t")
    search_movies(movie_name)


def handler(signal_received, frame):
    print(f"{Fore.rgb(255, 0, 0)} \n\nWant to quit?. Exiting gracefully.. Good Bye!" + reset)  # Red color
    sys.exit(0)


if __name__ == "__main__":
    signal(SIGINT, handler)
    show_main_screen()

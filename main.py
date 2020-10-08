import requests
import spinner
from http.client import responses

# Pls put here your token, from https://yandex.ru/dev/disk/poligon/
ya_token = ''


class YaUploader:
    def __init__(self, token: str):
        self.TOKEN = {'Authorization': 'OAuth ' + token}
        self.HOST_API = 'https://cloud-api.yandex.net:443'
        self.UPLOAD_SCHEME = '/v1/disk/resources/upload'
        self.LIST_SCHEME = '/v1/disk/resources/files'
        self.USER_AGENT = {"User-Agent": "Netology"}
        self.HEADERS = {**self.USER_AGENT, **self.TOKEN}

    def __do_request(self, method='get', url=None, params=None, headers=None, files=None):
        """This private method is middleware for insertion headers and other info in request in same manner"""
        if headers is None:
            headers = self.HEADERS
        if params is None:
            params = {}
        if url is None:
            url = self.LIST_SCHEME
        if method == 'get':
            return requests.get(url, params=params, headers=headers)
        if method == 'put':
            return requests.put(url, params=params, headers=headers, files=files)
        if method == 'post':
            return requests.post(url, params=params, headers=headers)
        return 'method not defined'

    def upload(self, file_path: str):
        """This method uploads file_path to Yandex disk"""
        # first we have to get upload link
        upload_link = self.__do_request('get', self.HOST_API + self.UPLOAD_SCHEME, params={'path': file_path})
        if upload_link.status_code != requests.codes.ok:
            return f'\nError while getting upload link. Error code: ' \
                   f'{upload_link.status_code} ({responses[upload_link.status_code]})'
        # using upload link let's actually start file uploading
        files = {'file': open(file_path, 'rb')}
        request = self.__do_request('put', upload_link.json()['href'], params={'path': file_path}, files=files)
        if not (200 <= request.status_code < 300):
            return f'\nError while uploading file. Error code: ' \
                   f'{request.status_code} ({responses[request.status_code]})'
        return f'\nFile uploaded. Code: {request.status_code} ({responses[request.status_code]})'

    def list_files(self, limit=20):
        """This method show files list at Yandex disk, where limit is for pagination purposes"""
        result = []
        offset = 0
        try:
            while True:
                # foll line is for debug purposes
                print('requesting ' + str(limit) + ' files with offset ' + str(offset) + '...')
                request = self.__do_request('get',
                                            self.HOST_API + self.LIST_SCHEME,
                                            params={'limit': limit, 'fields': 'path, size', 'offset': offset})
                # first check status of request and exit if it has no success
                if not (200 <= request.status_code < 300):
                    return [f'\nError while listing directories. Error code: '
                            f'{request.status_code} ({responses[request.status_code]})']
                # try to parse items - there might be errors
                items = request.json()['items']
                # if no files found, we do exit
                if len(items) < 1:
                    break
                result += [f'\n- {x["path"].lstrip("disk:/")} ({str(int(x["size"] / 1024))} kB)'
                           for x in request.json()['items']]
                # if returned less files than we requested, means that no more files left
                if len(items) < limit:
                    break
                offset += limit
        except:
            pass
        return result


while ya_token == '':
    ya_token = input('Please enter your Yandex OAuth token: ')
print('File uploading, please wait...')
with spinner.Spinner():
    uploader = YaUploader(ya_token)
    print(uploader.upload('picture.jpg'))
print('\nFiles list in Yandex disk:')
print(*uploader.list_files(5))

#!/usr/bin/env python3

import argparse
import aiofiles
import aiohttp
import asyncio
import ssl
import yaml

def load_config(config_file):
    config_dict = {}

    with open(config_file, 'rt') as f:
        config_dict = yaml.load(f, Loader=yaml.FullLoader)

    return config_dict

def print_results(method, result):
    print('\n===== HTTP %s METHOD BENCHMARK RESULT =====\n' %(method.upper()))
    print('%-15s%-15s%-15s' %('ROUND #', 'HTTP RC', '# OF HTTP RC'))
    print('-' * 45)
    for c in result.keys():
        for rc in sorted(result[c]['response_code'].keys()):
            print('%-15d%-15s%-15d' %(c+1, rc, result[c]['response_code'][rc]['count']))

async def http_get_resp(session, config_dict, result):
    try:
        async with session.get(config_dict['url']) as resp:
            rc = str(resp.status)

            # check if user wants to download the response body
            if config_dict['get_data_to_null']:
                async with aiofiles.open('/dev/null', 'wb') as f:
                    while True:
                        chunk = await resp.content.read(config_dict['get_data_chunk_size'])
                        if not chunk:
                            break
                        await f.write(chunk)
    except:
        rc = '000'

    # save response code
    if rc in result['response_code']:
        result['response_code'][rc]['count'] += 1
    else:
        result['response_code'][rc] = {}
        result['response_code'][rc]['count'] = 1

async def http_head_resp(session, config_dict, result):
    try:
        async with session.head(config_dict['url'], allow_redirects=True) as resp:
            rc = str(resp.status)
    except:
        rc = '000'

    # save response code
    if rc in result['response_code']:
        result['response_code'][rc]['count'] += 1
    else:
        result['response_code'][rc] = {}
        result['response_code'][rc]['count'] = 1

async def http_post_resp(session, config_dict, result):
    post_data = None

    # check if POST data exists
    if config_dict['post_data']:
        post_data = config_dict['post_data']

    try:
        async with session.post(config_dict['url'], data=post_data) as resp:
            rc = str(resp.status)
    except:
        rc = '000'

    # save response code
    if rc in result['response_code']:
        result['response_code'][rc]['count'] += 1
    else:
        result['response_code'][rc] = {}
        result['response_code'][rc]['count'] = 1

async def http_call(http_resp, config, result):
    # check if headers are set
    headers = None

    if config['headers']:
        headers = config['headers']

    # check if mTLS is enabled
    ssl_context = None
    enable_cleanup_closed = False

    if config['mtls']:
        ssl_context = ssl.create_default_context(cafile=config['tls_ca'])
        ssl_context.load_cert_chain(config['tls_cert'], config['tls_key'])
        enable_cleanup_closed = True

    # set up TCPConnector parameters
    conn = aiohttp.TCPConnector(limit=config['concurrency'], limit_per_host=0, ssl=ssl_context, enable_cleanup_closed=enable_cleanup_closed)

    # set up client session
    timeout = aiohttp.ClientTimeout(total=config['timeout'])

    async with aiohttp.ClientSession(connector=conn, timeout=timeout, headers=headers) as session:
        urls = [config['url'] for i in range(config['concurrency'])]

        for c in range(config['count']):
            result[c] = {}
            result[c]['response_code'] = {}

            tasks = []
            for url in urls:
                task = asyncio.create_task(http_resp(session, config, result[c]))
                tasks.append(task)

            await asyncio.gather(*tasks, return_exceptions=True)

            # sleep a gap time between each batch
            await asyncio.sleep(config['gap_time'])

if __name__ == '__main__':
    # set up args
    parser = argparse.ArgumentParser(description="HTTP Traffic Benchmarker (asyncio-based)")
    parser.add_argument("-c", "--config", type=str, required=True, help="HTTP traffic config file")
    args = parser.parse_args()

    # load the benchmark config
    config_dict = load_config(args.config)

    print('\n===== HTTP BENCHMARK PARAMETERS =====\n')
    print('URL: %s' %(config_dict['url']))
    print('CONCURRENCY: %d' %(config_dict['concurrency']))
    print('# OF RUNNING ROUND: %d' %(config_dict['count']))
    print('REQUEST TIMEOUT(SECOND): %f' %(float(config_dict['timeout'])))
    print('BATCH GAP PERIOD(SECOND): %f' %(float(config_dict['gap_time'])))

    # set up result output dict.
    result = {}

    # HTTP GET - process block
    if config_dict['method'].upper() == 'GET':
        asyncio.run(http_call(http_get_resp, config_dict, result))

        print_results('GET', result)

    # HTTP HEAD - process block
    if config_dict['method'].upper() == 'HEAD':
        asyncio.run(http_call(http_head_resp, config_dict, result))

        print_results('HEAD', result)

    # HTTP POST - process block
    if config_dict['method'].upper() == 'POST':
        asyncio.run(http_call(http_post_resp, config_dict, result))

        print_results('POST', result)

# Eric's HTTP Traffic Benchmarker

## Intro

This is a small and lightweight HTTP traffic benchmark tool. It uses Async I/O to generate high throughput traffic.

## Python Module Dependencies

Following Python modules are needed to run this benchmark tool.

```
aiofiles
aiohttp
asyncio
ssl
yaml
```

## Features

* Support HTTP GET / HEAD / POST methods
* Support mTLS HTTPS connections
* Allow customized headers in the request
* Lightweight traffic creation by asyncio

This benchmark tool CANNOT retrieve traffic latency metrics because `aiohttp` module does not record those metrics. This tool only prints out count of requests and HTTP Response Code.

Here's the [reason](https://github.com/aio-libs/aiohttp/issues/1309) why aiohttp does not have traffic latency attributes.

## Usage

```
usage: http_benchmarker.py [-h] -c CONFIG [-d]

HTTP Traffic Benchmarker (asyncio-based)

optional arguments:
  -h, --help            show this help message and exit
  -c CONFIG, --config CONFIG
                        HTTP traffic config file
  -d, --debug           Enable debug mode(show exception message)
```

This tool reads the HTTP traffic parameters by using a configuration file. The next part `Configuration File` gives detailed explanations of parameters.

## Configuration File

The configuration file is using YAML format. Here's the example:

```
method: 'GET'
url: 'http://www.yahoo.com'
concurrency: 50
count: 3
gap_time: 5
timeout: 60
headers:
  'Content-Type': 'plain/text'
mtls: 0
tls_ca: ''
tls_cert: ''
tls_key: ''
get_data_to_null: 1
get_data_chunk_size: 65535
post_data: '{"key1": 1}'
```

### Explanations of Parameters

| Name | Value Type | Meaning | Example |
| --- | --- | --- | --- |
| method | String | HTTP method | `'GET'` |
| url | String | Testing URL | `'https://www.yahoo.com'`|
| concurrency | Integer | # of parallel connections | `10` |
| count | Integer | # of testing round | `5` |
| gap_time | Float | Gap period between each round(second) | `1.0` |
| timeout | Float | Connection total timeout(second) | `60` |
| headers | Dictionary | HTTP headers | `'Content-Type': 'plain/text'` |
| get_data_to_null | Integer | Write data to /dev/null flag(0: disable; 1: enable) | `1` |
| get_data_chunk_size | Integer | Chunk size in byte of each writing operation | `65535` |
| post_data | String | Data enclosed for POST body | `'{"key1": 1}'` |
| mtls | Integer | mTLS enabling flag(0: disable; 1: enable) | `1` |
| tls_ca | String | TLS CA certificate path | `'/opt/certs/ca.cert'` |
| tls_cert | String | TLS certificate path | `'/opt/certs/cert.pem'` |
| tls_key | String | TLS private key path | `'/opt/cert/key.pem'` |

Please make sure the TLS related settings `tls_*` are in the configuration file even they are not used. Simply set them as empty string `''` would be okay.

## Example

### Configuration File Contents

```
method: 'GET'
url: 'http://www.yahoo.com'
concurrency: 50
count: 3
gap_time: 5
timeout: 60
headers:
  'Content-Type': 'plain/text'
mtls: 0
tls_ca: ''
tls_cert: ''
tls_key: ''
get_data_to_null: 1
get_data_chunk_size: 65535
post_data: '{"key1": 1}'
```

### Command Line Output

```
$ ./http_benchmarker.py -c example.yaml 

===== HTTP BENCHMARK PARAMETERS =====

URL: https://www.yahoo.com
CONCURRENCY: 50
# OF RUNNING ROUND: 3
REQUEST TIMEOUT(SECOND): 60.000000
BATCH GAP PERIOD(SECOND): 5.000000

===== HTTP GET METHOD BENCHMARK RESULT =====

ROUND #        HTTP RC        # OF HTTP RC   
---------------------------------------------
1              200            50             
2              200            50             
3              200            50 

$
```

## Notes

* If any exception is encountered, the HTTP RESPONSE CODE would be `000`.
* If user would like to benchmark actual GET download data performance, please enable `get_data_to_null` and set up a proper value on `get_data_chunk_size` parameter.
* `post_data` field in the configuration file is enabled only when using HTTP POST method.
* aiohttp loads only the headers when .get() is executed, letting you decide to pay the cost of loading the body afterward. [The aiohttp Request Lifecycle](https://docs.aiohttp.org/en/stable/http_request_lifecycle.html)
* User would experience ceiling download speed limit when the concurrency number is greater than a specific value. aiohttp is using single thread so a single processor core has its own limit on how much data it can process.

## TODO

* ~~Add HTTP POST support~~
* ~~Add HTTP header support~~
* ~~Add HTTP GET data support~~

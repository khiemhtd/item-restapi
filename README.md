# Item-RestAPI
A simple Rest API with following functions:
- Retrieve account/accounts
- Add account
- Edit account
- Delete account

# Requirements
- Python 3.6+ installed
- Package [aiohttp](https://docs.aiohttp.org/en/stable/index.html) installed

# Usage
```
cd /path/to/item-restapi
python3 -m item.main --help
usage: main.py [-h] [-v] [--ip IP] [--port PORT] [--log-file LOG_FILE] [--data-file DATA_FILE]

Item's Rest API

optional arguments:
  -h, --help            show this help message and exit
  -v, --verbose         increase log output verbosity
  --ip IP, -i IP        The ip address to serve the Rest API
  --port PORT, -p PORT  The port to serve the Rest API
  --log-file LOG_FILE, -l LOG_FILE
                        Output logs to specified file
  --data-file DATA_FILE, -d DATA_FILE
                        Path to data file containing json data
```
E.g. run on local host with sample data
```
cd /path/to/item-restapi
python3 -m item.main --data-file resources/sample.json
```
E.g. run server on custom ip and port
```
cd /path/to/item-restapi
python3 -m item.main --ip 1.2.3.4 --port 1234
```
E.g. output logs to a file
```
cd /path/to/item-restapi
python3 -m item.main --log-file /path/to/logfile.log
```

# REST API
| Method  | URL | Description |
| ------------- | ------------- | ------------- |
| GET | "/api/v1/test" | Displays "Hello World", useful for connection tests |
| GET | "/api/v1/account/{account_id} | Get account information given account id |
| GET | "/api/v1/accounts/{number}" | Get an alphabetically sorted list of accounts, number indicates the number of accounts to return |
| POST | "/api/v1/accounts/add" | Add an account via json post data |
| PUT | "/api/v1/accounts/edit/{account_id}" | Edit an account given an account id and PUT data |
| DELETE | "/api/v1/accounts/delete/{account_id}" | Delete an account given account id |

All calls returns json with following fields:
| FIELD  | Description |
| ------------- | ------------- |
|'id'| in json-rpc this is set by sender/client but in this case server generates it, only used for testing |
|'result'| True if request was successful, False otherwise |
|'message'| A message that may contain relevant information e.g. why a call failed |
|'data'| json data e.g. account information |

Sample Response
```
{
  "id": 6,
  "result": true,
  "message": "Successfully retrieved account",
  "data": {
    "name": "CompanyAAA",
    "orgno": 1,
    "leader_title": "admin",
    "leader_name": "LeaderAAA",
    "type": "Technology"
  }
}
```
# TODO:
- persistent data (save data on shutdown)
- unit tests
- test API calls (zero testing on these):
  - add account
  - delete account
  - edit account

import aiohttp
import asyncio
import logging

from aiohttp import web

LOGGER = logging.getLogger(__name__)

"""
e.g. entry:
{
    "name": "",
    "orgno": 0,
    "leader_title": "",
    "leader_name": "",
    "type": ""
}

Requirements
- Sort alphabetically
- Given number n, provide n records
- Ability to change company info (except companyId)
- Ability to delete company
- Return response returns true/false indicating whether action was successful
"""

FIELD_RESP_ID = "id"
FIELD_RESP_RESULT = "result"
FIELD_RESP_MESSAGE = "message"
FIELD_RESP_DATA = "data"

FIELD_NAME = "name"
FIELD_ORGNO = "orgno"
FIELD_LEADER_TITLE = "leader_title"
FIELD_LEADER_NAME = "leader_name"
FIELD_TYPE = "type"
ACCOUNT_FIELDS = [FIELD_NAME, FIELD_ORGNO, FIELD_LEADER_TITLE, FIELD_LEADER_NAME, FIELD_TYPE]

class ItemServer:
    def __init__(self, host="127.0.0.1", port=8080, data={}):
        self.app = web.Application()
        self.host = host
        self.port = port
        self.accounts=  {}
        self.message_id = 0 # Should never be called directly

        # Minimal sanitation
        # TODO: Could check valid data
        if data:
            if isinstance(data, dict):
                self.accounts = data
                LOGGER.info(f"Data successfully loaded: {data}")
            else:
                LOGGER.error(f"Could not load data: {data}")
                raise Exception(f"Invalid data: {data}")

        self._setup_routes()

    def _setup_routes(self):
        self.app.router.add_get("/api/v1/test", self.test)
        self.app.router.add_get("/api/v1/account/{account_id}", self.get_account)
        self.app.router.add_get("/api/v1/accounts", self.get_accounts)
        self.app.router.add_get("/api/v1/accounts/{number}", self.get_accounts)
        self.app.router.add_post("/api/v1/accounts/add", self.add_contact)
        self.app.router.add_put("/api/v1/accounts/edit/{account_id}", self.edit_contact)
        self.app.router.add_delete("/api/v1/accounts/delete/{account_id}", self.delete_contact)

    def _generate_resp(self, id, result, message="", data=None):
        """
        Generates a json response.
        Attempts to mimic JSON-RPC like response by having an id and result field.
        'id' in json-rpc this is set by sender/client but here we will have the
        'result' True if request was successful, False otherwise
        'message' additional information
        'data' json data
        """
        resp = {FIELD_RESP_ID : id, FIELD_RESP_RESULT: result, FIELD_RESP_MESSAGE : message}
        if data:
            resp[FIELD_RESP_DATA] = data
        return resp

    @property
    def id(self):
        id = self.message_id
        self.message_id += 1
        return id

    async def _validate_account_id(self, account_id):
        """
        Checks and validates provided account id.
        :param account_id: target account id (str or int) to be validated
        :return: None if valid account_id, a Response object if it's not.
        """
        # Check if orgno present
        if account_id == None:
            return web.json_response(self._generate_resp(id, False, "Field 'orgno' either doesn't exist or is null"))

        # Ensure it's a positive integer
        try:
            if int(account_id) < 0:
                return web.json_response(self._generate_resp(id, False, f"Account {account_id} is a negative integer"))
        except ValueError:
            return web.json_response(self._generate_resp(id, False, f"Account {account_id} is not an integer"))

        return None

    async def get_account(self, request):
        id = self.id
        account_id = str(request.match_info.get("account_id", None))
        LOGGER.info(f"get_account: {account_id}")

        # Check if account exists
        if account_id not in self.accounts:
            LOGGER.error(f"Account doesnt exist: {self._generate_resp(id, False, f'Account {account_id} doesnt exist')}")
            return web.json_response(self._generate_resp(id, False, f"Account {account_id} doesn't exist"))

        # Validate account id:
        resp = await self._validate_account_id(account_id)
        if resp:
            return resp

        return web.json_response(self._generate_resp(id, True, f"Successfully retrieved account", self.accounts[account_id]))

    async def get_accounts(self, request):
        id = self.id
        sorted_data = sorted(self.accounts.values(), key=lambda x: x["name"])
        number = int(request.match_info.get("number", 0))
        LOGGER.info(f"get_accounts: {number}")

        LOGGER.info(f"get_accounts: {number}")
        if number and number < len(sorted_data):
            return web.json_response(self._generate_resp(id, True, f"Successfully retrieved account", sorted_data[:number]))
        return web.json_response(self._generate_resp(id, True, f"Successfully retrieved account", sorted_data))

    async def add_contact(self, request):
        id = self.id
        data = await request.json()
        account_id = data.get(FIELD_ORGNO, None)
        LOGGER.info(f"add_contact: {account_id}")

        # Validate account id:
        resp = await self._validate_account_id(account_id)
        if resp:
            return resp

        # Check if account already exist
        if str(account_id) in self.accounts:
            return web.json_response(self._generate_resp(id, False, f"Account {account_id} already exist"))

        # Create new account
        new_account = {}
        for key in ACCOUNT_FIELDS:
            value = data.get(key, None)
            if not value:
                return web.json_response(self._generate_resp(id, False, f"Missing field '{key}', no value found."))
            new_account[key] = value
        self.accounts[str(account_id)] = new_account

    async def delete_contact(self, request):
        id = self.id
        account_id = str(request.match_info.get("account_id", None))
        LOGGER.info(f"delete_account: {account_id}")

        # Validate account id:
        resp = await self._validate_account_id(account_id)
        if resp:
            return resp

        # Attempt to delete account id
        try:
            self.accounts.pop(account_id)
        except KeyError:
            return web.json_response(self._generate_resp(id, False, f"Account {account_id} not found"))

        # Success
        return web.json_response(self._generate_resp(id, True, f"Account {account_id} successfully deleted"))

    async def edit_contact(self, request):
        data = await request.json()
        account_id = str(request.match_info.get("account_id", None))
        LOGGER.info(f"edit_account: {account_id}")

        # Validate account id:
        resp = await self._validate_account_id(account_id)
        if resp:
            return resp

        # Check if account exists
        if account_id not in self.accounts:
            return web.json_response(self._generate_resp(id, False, f"Account {account_id} doesn't exist"))

        # Edit every valid field found
        something_changed = False
        for key in ACCOUNT_FIELDS:
            value = data.get(key, None)
            #TODO: Check if value is different?
            if value:
                something_changed = True
                self.accounts[account_id][key] = value

        # Return True if something changed else False
        if something_changed:
            return web.json_response(self._generate_resp(id, True, f"Account {account_id} successfully updated"))
        else:
            return web.json_response(self._generate_resp(id, True, f"No updated data provided for account {account_id}"))


    async def test(self, request):
        LOGGER.info("test")
        return web.Response(text="Hello world, connection successful")

    def run(self):
        web.run_app(self.app, host=self.host, port=self.port)


async def handle(request):
    name = request.match_info.get("name", "Anonymous")
    text = "Hello, " + name
    return web.Response(text=text)

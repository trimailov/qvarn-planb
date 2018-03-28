import urllib.parse

import aiohttp

from apistar import http
from apistar import Settings

from qvarn.backends import Storage
from qvarn.backends import ResourceNotFound
from qvarn.exceptions import NotFound


async def auth_token(headers: http.Headers, body: http.Body, settings: Settings):
    """
    Proxy /auth/token requests to Gluu.
    """
    async with aiohttp.ClientSession() as session:
        endpoint = urllib.parse.urljoin(settings['QVARN']['TOKEN_ISSUER'], 'oxauth/.well-known/openid-configuration')
        async with session.get(endpoint) as resp:
            config = await resp.json()
        headers = {
            'authorization': headers['authorization'],
            'content-type': headers['content-type'],
        }
        async with session.post(config['token_endpoint'], data=body, headers=headers) as resp:
            content_type = resp.headers['content-type']
            if content_type == 'application/json':
                return http.Response(await resp.json(), status=resp.status)
            else:
                return http.Response(await resp.read(), status=resp.status, content_type=content_type)


async def resource_get(resource_type, storage: Storage):
    return {
        'resources': [
            {'id': resource_id} for resource_id in await storage.list(resource_type)
        ],
    }


async def resource_post(resource_type, data: http.RequestData, storage: Storage):
    return await storage.create(resource_type, data)


async def resource_id_get(resource_type, resource_id, storage: Storage):
    try:
        return await storage.get(resource_type, resource_id)
    except ResourceNotFound:
        raise NotFound({
            'error_code': 'ItemDoesNotExist',
            'item_id': resource_id,
            'message': "Item does not exist",
        })
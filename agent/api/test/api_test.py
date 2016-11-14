from asyncio import get_event_loop, new_event_loop

import pytest

from json import dumps, loads
from functools import reduce

from jsonschema import ValidationError

from agent.links.api.invitation import acceptInvitation
from agent.claims.api.claims import getClaim
from agent.onboarding.api.onboard import onboard
from agent.login.api.login import login
from agent.api.apiServer import api


@pytest.fixture
def client(loop, test_client):
    # loop = new_event_loop()
    return loop.run_until_complete(test_client(api(loop, "Faber", "Faber000000000000000000000000000")))


def test_onboardError(loop, client):
    postData = dumps({
        'sovrinId': 'sovrinId',
        'publicKey': 'o9889899bs0y8asndjds99sd79sdndjs7=',
        'route': 'register'
    })
    with pytest.raises(ValidationError):
        loop.run_until_complete(onboard(postData, client.app))


def test_loginError(loop):
    postData = dumps({
        'signature': '979nknksdnknkskdsha797979878',
        'route': 'register'
    })
    with pytest.raises(ValidationError):
        loop.run_until_complete(login(postData))


def test_claimError(loop):
    postData = dumps({
        'signature': '979nknksdnknkskdsha797979878',
        'route': 'register'
    })
    with pytest.raises(ValidationError):
        loop.run_until_complete(getClaim(postData))

    postData = {
        'signature': '979nknksdnknkskdsha797979878',
        'invitationId': '3W2465HP3OUPGkiNlTMl2iZ+NiMZegfUFIsl8372334',
        'route': 'getClaim'
    }
    responseJson = loop.run_until_complete(getClaim(postData))
    response = loads(responseJson)
    assert response['status'] == 400
    assert response['message'] == 'invalid claim'


def test_invitationError(loop):
    postData = {
        'route': 'acceptInvitation',
        'signature': '979nknksdnknkskdsha797979878',
        'invitation': {
            'id': '3W2465HP3OUPGkiNlTMl2iZ+NiMZegfUFIsl8378KH4=',
            'publicKey': 'adfasdfuyaddfiaifd8f8d6f8df764svua',
            'signature': 'oiadmmat0-tvknaai7efa7f5aklfaf=adf8ff'
        }
    }
    with pytest.raises(ValidationError):
        loop.run_until_complete(acceptInvitation(postData))

    postData = {
        'route': 'acceptInvitation',
        'signature': '979nknksdnknkskdsha797979878',
        'sovrinId': 'sovrinId',
        'invitation': {
            'id': '3W2465HP3OUPGkiNlTMl2iZ+NiMZegfUFIsl8378K875',
            'publicKey': 'adfasdfuyaddfiaifd8f8d6f8df764svua',
            'signature': 'oiadmmat0-tvknaai7efa7f5aklfaf=adf8ff'
        }
    }
    responseJson = loop.run_until_complete(acceptInvitation(postData))
    response = loads(responseJson)
    assert response['status'] == 400
    assert response['message'] == 'invalid invitation'


def test_onboardSuccess(loop, client):
    # TODO:KS generate this signature, key from nacl
    postData = dumps({
        'signature': 'xTayONsFJnVNmgGH8CFIGbZcfI6ikR+w9kPuzUkAqFFTdkm6Eujy5AYx+PwEgwZkm5ob6nPDXYGS2aTCFyhcDHNvdnJpbklk',
        'sovrinId': 'sovrinId',
        'data': dumps({'message': 'sovrinId'}),
        'publicKey': 'eutTvvZLl5OmPkCl29WNFmwUpsJrDzuZUuS+hm36TJ4=',
        'route': 'register'
    })
    responseJson = loop.run_until_complete(onboard(loads(postData), client.app))
    response = loads(responseJson)
    assert response['status'] == 200
    assert 'success' in response
    assert response['success'] == True


def test_loginSuccess(loop):
    # TODO:KS generate this signature from nacl generated secret key
    postData = dumps({
        'signature': '979nknksdnknkskdsha797979878',
        'sovrinId': 'sovrinId',
        'route': 'register'
    })
    responseJSON = loop.run_until_complete(login(postData))
    response = loads(responseJSON)
    assert response['status'] == 200
    assert 'success' in response
    assert response['success'] == True


# TODO:SC test websocket connection
def test_acceptInvitationSuccess(loop):
    postData = {
        'route': 'acceptInvitation',
        'signature': '979nknksdnknkskdsha797979878',
        'sovrinId': 'sovrinId',
        'invitation': {
            'id': '3W2465HP3OUPGkiNlTMl2iZ+NiMZegfUFIsl8378KH4=',
            'publicKey': 'adfasdfuyaddfiaifd8f8d6f8df764svua',
            'signature': 'oiadmmat0-tvknaai7efa7f5aklfaf=adf8ff'
        }
    }
    responseJson = loop.run_until_complete(acceptInvitation(postData))
    response = loads(responseJson)
    assert "claims" in response
    assert "cd40:98nkk86698688" in response["claims"]


# TODO:SC test websocket connection
def test_getClaimSuccess(loop):
    postData = {
        'signature': '979nknksdnknkskdsha797979878',
        'invitationId': '3W2465HP3OUPGkiNlTMl2iZ+NiMZegfUFIsl8378KH4=',
        'route': 'getClaim'
    }
    responseJson = loop.run_until_complete(getClaim(postData))
    response = loads(responseJson)
    assert 'claims' in response
    claims = response['claims']
    assert len(claims) > 0
    claim = reduce((lambda x, y: y), list(filter(
        lambda x: x['identifier'] == 'cd40:98nkk86698688',
        claims
    )), {})
    assert 'degree' in claim['attributes']

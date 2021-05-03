import datetime
from enum import Enum
import json
from playsound import playsound
import requests
import sys
import time


PINCODES = []
STATE = ''
DISTRICTS = []


_SCHEME = 'https'
_HOSTNAME = 'cdn-api.co-vin.in'
_BASE_ENDPOINT = '/api/v2'
_AGE_LIMIT = 18



class FeeType(Enum):
    FREE = 'Free'
    PAID = 'Paid'


class Vaccine(Enum):
    COVAXIN = 'COVAXIN'
    COVISHIELD = 'COVISHIELD'


class State:
    def __init__(self, data):
        self.state_id = data['state_id']
        self.state_name = data['state_name']


class District:
    def __init__(self, data):
        self.district_id = data['district_id']
        self.district_name = data['district_name']


class Center:
    def __init__(self, data):
        self.center_id = data['center_id']
        self.name = data['name']
        self.state_name = data['state_name']
        self.district_name = data['district_name']
        self.block_name = data['block_name']
        self.pincode = data['pincode']
        self.from_ = data['from']
        self.to_ = data['to']
        self.fee_type = FeeType(data['fee_type'])
        self.sessions = [Session(item) for item in data['sessions']]
#        if self.fee_type == FeeType.PAID:
#            self.vaccine_fees = [VaccineFee(item) for item in data['vaccine_fees']]


class VaccineFee:
    def __init__(self, data):
        self.vaccine = data['vaccine']
        self.fee = data['fee']


class Session:
    def __init__(self, data):
        self.session_id = data['session_id']
        self.date = data['date']
        self.available_capacity = data['available_capacity']
        self.min_age_limit = data['min_age_limit']
        self.vaccine = data['vaccine']
        self.slots = data['slots']


class Appointment:
    def __init__(self, data):
        self.center_id = data['center_id']
        self.name = data['name']
        self.state_name = data['state_name']
        self.district_name = data['district_name']
        self.block_name = data['block_name']
        self.pincode = data['pincode']
        self.from_ = data['from']
        self.to_ = data['to']
        self.fee_type = FeeType(data['fee_type'])
        self.dose = data['dose']
        self.appointment_id = data['appointment_id']
        self.session_id = data['session_id']
        self.date = data['date']
        self.slot = data['slot']


def _make_get_request(url, query_params, request_headers):
    r = requests.get(url, params=query_params, headers=request_headers)
    r.raise_for_status()
    if r.status_code == requests.codes.ok:
        return r.json()
    else:
        print(r.text)
        raise Exception('unexpected response')


def _get_endpoint(endpoint):
    return _SCHEME + '://' + _HOSTNAME + _BASE_ENDPOINT + endpoint

def get_calendar_by_pin(pincode, date):
    endpoint = '/appointment/sessions/public/calendarByPin'
    query_params = {'pincode': pincode, 'date': date}
    headers = {'accept': 'application/json'}
    url = _get_endpoint(endpoint)
    resp = _make_get_request(url, query_params, headers)
    return resp


def get_calendar_by_district(district_id, date):
    endpoint = '/appointment/sessions/public/calendarByDistrict'
    query_params = {'district_id': district_id, 'date': date}
    headers = {'accept': 'application/json'}
    url = _get_endpoint(endpoint)
    resp = _make_get_request(url, query_params, headers)
    return resp


def get_states():
    endpoint = '/admin/location/states'
    headers = {'accept': 'application/json'}
    url = _get_endpoint(endpoint)
    resp = _make_get_request(url, {}, headers)
    return resp


def get_districts(state_id):
    endpoint = '/admin/location/districts/' + str(state_id)
    headers = {'accept': 'application/json'}
    url = _get_endpoint(endpoint)
    resp = _make_get_request(url, {}, headers)
    return resp


def parse_calendar_response(resp):
    opening_found = False
    centers = [Center(item) for item in resp['centers']]

    for c in centers:
        for s in c.sessions:
            if s.min_age_limit == 45 and s.available_capacity > 80:
                print('\n Pincode', c.pincode, 'Center ID', c.center_id)
                print(' Center Name:', c.name)
                print('  Available date:', s.date)
                print('  Available capacity:', s.available_capacity)
                print('  Vaccine:', s.vaccine)
                print('  Slots:', s.slots)
                print('  Fee type:', c.fee_type)
                opening_found = True
    return opening_found


def get_district_id_list():
    resp = get_states()
    states = [State(item) for item in resp['states']]
    d_list = list()
    for s in states:
        if STATE == s.state_name:
            print('State:', s.state_name, 'State ID:', s.state_id)
            resp1 = get_districts(s.state_id)
            districts = [District(item) for item in resp1['districts']]
            for d in districts:
                if d.district_name in DISTRICTS:
                    print('District:', d.district_name, 'District ID:', d.district_id)
                    d_list.append(d.district_id)
            break
    return d_list


def start_tracking_by_district():
    district_list = get_district_id_list()
    if not district_list:
        print('No districts found, please check the input')
        return

    while True:
        today = datetime.datetime.now()
        print('Current time:', today)
        date_str = "{:02d}-{:02d}-{}".format(today.day, today.month, today.year)
        opening_found = False

        for district in district_list:
            try:
                resp = get_calendar_by_district(district, date_str)
            except Exception as e:
                print('Something went wrong while fetching calendar by district', e)
                continue
            opening_found = parse_calendar_response(resp)
            if opening_found:
                try:
                    while True:
                        playsound('test.wav')
                except KeyboardInterrupt:
                    continue
        time.sleep(15)


def start_tracking_by_pin():
    if not PINCODES:
        print('No pincodes found, please check the input')
        return

    while True:
        today = datetime.datetime.now()
        print('Current time:', today)
        date_str = "{:02d}-{:02d}-{}".format(today.day, today.month, today.year)
        opening_found = False

        for pincode in PINCODES:
            try:
                resp = get_calendar_by_pin(pincode, date_str)
            except Exception as e:
                print('Something went wrong while fetching calendar by pincode:', e)
                continue
            opening_found = parse_calendar_response(resp)
            if opening_found:
                try:
                    while True:
                        playsound('test.wav')
                except KeyboardInterrupt:
                    continue
        time.sleep(15)


if __name__ == '__main__':
    mode = sys.argv[1]
    if mode == 'pincodes':
        print('Tracking by pincodes')
        start_tracking_by_pin()
    elif mode == 'districts':
        print('Tracking by districts')
        start_tracking_by_district()
    else:
        print('So long, and thanks for all the fish!')


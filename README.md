# Co-Win Appointment Availability Tracker

Quick hack to track available appointments by pincode or district for 18+ age category in the next 7 days. Plays an alarm sound when available appointments are found.

Based on Co-Win Public APIs: https://apisetu.gov.in/public/marketplace/api/cowin/cowin-public-v2

Tested with Python 3.8.0.

## How to use
#### 1. Edit appt-tracker.py file to include your choice of pincodes OR (state, districts)
```
PINCODES = [562157, 560064, 560017, 560071, 560020, 560066, 560027, 562106]
```
or
```
STATE = 'Karnataka'
DISTRICTS = ['BBMP', 'Bangalore Urban']
```

#### 2. Install requirements

```
pip install -r requirements.txt
```

#### 3. Run the script
```
# to track by pincodes:
python appt-tracker.py pincodes

# to track by districts:
python appt-tracker.py districts
```

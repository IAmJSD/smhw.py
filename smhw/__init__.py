import urllib
import requests
import json
import time
import datetime
# Imports go here.

def GetResponse(resource, request):
    response = requests.get("https://api.showmyhomework.co.uk/api/" + resource + "?" + request,
                           headers = {"Accept" : "application/smhw.v3+json"})
    return json.loads(response.text)
# Gets response from the SMHW API.

def SearchSchools(Filter, maxquery=None):
    if maxquery == None:
        maxquery = ""
    else:
        maxquery = "&limit=" + str(maxquery)
    return GetResponse("schools", "filter=" + urllib.parse.quote(Filter) + maxquery)
# Searches for schools and parses results in JSON.

def GetSchoolID(subdomain):
    return int(GetResponse("schools", "subdomain=" + subdomain + "&limit=1")["schools"][0]["id"])
# Gets the ID of the school.

def GetSchoolStaff(subdomain, Filter=None):
    if Filter == None:
        Filter = ""
    else:
        Filter = "&filter=" + urllib.parse.quote(Filter)
    return GetResponse("employees", "school_id=" + str(GetSchoolID(subdomain)) + Filter)
# Lists the staff and filters if specified. This can be a BIG request if not filtered.

def GetSchoolSubjects(subdomain):
    return GetResponse("subjects", "school_id=" + str(GetSchoolID(subdomain)))
# Lists all of the subjects in the school. This can be a BIG request.

def GetSchoolCalendar(subdomain):
    return GetResponse("calendars", "subdomain=" + str(subdomain))
# Gets calendar data through the subdomain. This can be a BIG request.

def LoginStudent(username, password, subdomain):
    response = requests.post("https://api.showmyhomework.co.uk/oauth/token?client_id=a44486a71714841f51744b66582427f2c094e48675b40530341d470c26d63bbd&client_secret=243a91065893d1e701d7f5d4ddf6d564a0e0559dfe872e6e6dfba849440af81d",
                             headers = {"Accept" : "application/smhw.v3+json"},
                             data = {"grant_type" : "password", "username" : username, "password" : password, "school_id" : GetSchoolID(subdomain) })
    return [json.loads(response.text), datetime.datetime.now()]
# Signs in and returns the JSON sent in a array with the date and time of login.

def RefreshToken(loginresponse):
    response = requests.post("https://api.showmyhomework.co.uk/oauth/token?client_id=a44486a71714841f51744b66582427f2c094e48675b40530341d470c26d63bbd&client_secret=243a91065893d1e701d7f5d4ddf6d564a0e0559dfe872e6e6dfba849440af81d",
                             headers = {"Accept" : "application/smhw.v3+json"},
                             data = {"grant_type" : "refresh_token", "refresh_token" : loginresponse[0]["refresh_token"]})
    return [json.loads(response.text), datetime.datetime.now()]
# Refreshes the token and returns the JSON sent in a array with the date and time of login.

def GetStudentInfo(loginresponse):
    response = requests.get("https://api.showmyhomework.co.uk/api/students",
                           headers = {"Accept" : "application/smhw.v3+json", "Authorization" : "Bearer " +  loginresponse[0]["smhw_token"]})
    return json.loads(response.text)["students"][0]
# Gets student info and returns it in JSON form.

def GetStudentTodo(loginresponse):
    response = requests.get("https://api.showmyhomework.co.uk/api/todos",
                           headers = {"Accept" : "application/smhw.v3+json", "Authorization" : "Bearer " +  loginresponse[0]["smhw_token"]})
    return json.loads(response.text)
# Gets the student todo list and returns it in JSON form.

def IsTokenExpired(loginresponse):
    timedelta = datetime.datetime.now() - loginresponse[1]
    if timedelta.total_seconds() >= 7200:
        return True
    else:
        return False
# Returns true if the token is out of date.

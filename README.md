# smhw.py
This is a Python client for the Show My Homework API.

## Installation
To install this library, simply clone the repository and open the root folder in whatever command terminal your OS uses (Terminal and cmd are the main ones). From here, type `python setup.py install` or `py setup.py install` (if one does not work try the other) unless you want to specify a Python version, in which case replace the `py/python` with (if we are using Python 3.6 as a example) `python3.6`. 

## Documentation
This part of the `README` lists all the commands and what they do with some examples:

**PLEASE NOTE BEFORE DOING ANY OF THESE YOU NEED TO `import smhw`**

- `smhw.GetResponse(resource, request)` - Not that important to the end user as this is just a definition called by other definitions in the client. It sends a HTTP GET request with their special headers and gets a response from the SMHW API.

- `smhw.SearchSchools(Filter, maxquery=None)` - Allows you to search for schools that are on SMHW. Setting the max query (this is a int) allows you to change the amount of schools that show up. The filter is something to find the specific area/schools you want.

- `smhw.GetSchoolID(subdomain)` - Once again not that important to the end user as this is just a definition called by other definitions in the client. Gets the ID of a school by its subdomain as it is needed for some requests.

- `smhw.GetSchoolStaff(subdomain, Filter=None)` - Gets the staff at a school. Please note that it is strongly suggested to filter the staff as it is a **BIG** request otherwise.

- `smhw.GetSchoolSubjects(subdomain)` - Gets all the subjects at a school. Please note that due to the fact there is no way to filter this that I can find (PLEASE submit a pull request if you find one), it is a **BIG** request.

- `smhw.GetSchoolCalendar(subdomain)` - Gets the school calendar for a school. Please note that due to the fact there is no way to filter this that I can find that still works (PLEASE submit a pull request if you find one), it is a **BIG** request.

- `smhw.LoginStudent(username, password, subdomain)` - Signs in and returns the JSON sent in a array with the date and time of login. For future reference, this array is called the login response.

- `smhw.RefreshToken(loginresponse)` - Allows you to refresh your token. You should replace your sign in definition with the response from this command as it is the same array type. You should run this 7,200 seconds after you were initially signed in.

- `smhw.IsTokenExpired(loginresponse)` - Allows you to check if it has been 7,200 seconds since sign in, therefore allowing you to quickly know if the token needs refreshing.

- `smhw.GetStudentInfo(loginresponse)` - Gets info on the signed in student and returns the JSON sent.

- `smhw.GetStudentTodo(loginresponse)` - Gets information on the signed in students SMHW profile and returns the JSON sent.

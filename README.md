# smhw.py
The **unofficial** Python API for Show My Homework.

## What does this do?
The job of this is to be a API. It sits between your application and Show My Homework using things such as decorators. For instance, here is a simple script that shows all of the functions.
```python
import smhw, logging
logging.basicConfig(level=logging.INFO)
cli = smhw.student_client("username", "password", "subdomain")

@cli.event
async def on_ready():
    print("This is " + cli.profile.forename + " " + cli.profile.surname)
    for homework in cli.get_homeworks():
        print(homework.title)

@cli.event
async def on_token_refresh():
    logging.info("Token refreshed.")

@cli.event
async def on_homework_set(homework):
    print("This is ran when a homework is set, for instance the title of this homework is " + homework.title)

@cli.event
async def on_homework_removed(homework):
    print("This is ran when a homework is removed from the API. Please note this does not mean it is overdue or has been done, just that it can no longer be seen on the API.")

cli.run()
```
As you can see, the main things you can define are `on_homework_removed`, `on_homework_set`, `on_token_refresh` and `on_ready` but more are planned in the future.

## Installation
Installation is simple, just install it like you would any other Python package. The command you need to run is `py install.py install` as administrator.

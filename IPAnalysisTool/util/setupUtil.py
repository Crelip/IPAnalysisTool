def setupDatabaseLogin():
    from os.path import expanduser
    from yaml import dump
    print("No database login details found. Please enter the following details: host, user, password, database name."
          "These details will be stored in ~/.config/IPAnalysisTool/config.yml")
    dbLogin = {}
    dbLogin['database_host'] = input('Enter the host name: ')
    dbLogin['database_user'] = input('Enter the user name: ')
    dbLogin['database_password'] = input('Enter the password: ')
    dbLogin['database_name'] = input('Enter the database name: ')
    # Put the login details into a YAML file
    with open(expanduser("~/.config/IPAnalysisTool/config.yml"), "w") as f:
        dump(dbLogin, f)
def setup_database_login():
    """
    Prompt the user to enter the database login details and store them in ~/.config/ip_analysis_tool/config.yml
    """
    from os.path import expanduser
    from yaml import dump
    print("No database login details found. Please enter the following details: host, user, password, database name."
          "These details will be stored in ~/.config/ip_analysis_tool/config.yml")
    db_login = {}
    db_login['database_host'] = input('Enter the host name: ')
    db_login['database_user'] = input('Enter the user name: ')
    db_login['database_password'] = input('Enter the password: ')
    db_login['database_name'] = input('Enter the database name: ')
    # Put the login details into a YAML file
    with open(expanduser("~/.config/IPAnalysisTool/config.yml"), "w") as f:
        dump(db_login, f)
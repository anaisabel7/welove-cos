import argparse

SETTINGS_FILE_NAME = '../welove_cos/email_settings.py'


def create_email_settings(email, password):
    f = open(SETTINGS_FILE_NAME, 'w+')
    if "@gmail" not in email:
        raise Exception("A 'gmail' email address is required.")
    mystr = "email = '{}'\n".format(email)
    print(mystr)
    f.write("email = '{}'\n".format(email))
    f.write("password = '{}'\n".format(password))
    f.close()


def main():
    parser = argparse.ArgumentParser(
        description="Parse email and password values"
    )
    parser.add_argument('--email', type=str, help="Your gmail email address")
    parser.add_argument(
        '--password', type=str, help="Password for your gmail email address"
    )
    args = parser.parse_args()
    create_email_settings(email=args.email, password=args.password)

if __name__ == "__main__":

    main()

import argparse
import os


def find_settings_file():

    script_path = os.path.dirname(__file__)
    if script_path:
        script_path = "{}/".format(script_path)
    settings_path = '{}../welove_cos/email_settings.py'.format(script_path)
    return settings_path


def create_email_settings(email, password):
    settings_file_name = find_settings_file()
    f = open(settings_file_name, 'w+')
    if "@gmail" not in email:
        raise Exception("A 'gmail' email address is required.")
    f.write("email = '{}'\n".format(email))
    f.write("password = '{}'\n".format(password))
    f.close()


def main():
    print(find_settings_file())
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

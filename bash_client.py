"""
A simple console-based ftp client for taXaminer datasets
"""
import ftplib
import os
from ftputil import FTPHost
from configparser import ConfigParser


def main():
    """
    Main program loop. Requests user input for host, login credentials and
    dataset to download
    :return:
    """
    # greetings
    print("\033[7mFTP Client for taXaminer Files 1.0\033[0m")
    while True:
        if os.path.exists('./static/ftp_config.ini'):
            load_config = input(
                "A config file was found. Would you like to load it? [y/n]")
            if load_config in ['y', 'yes']:
                config = ConfigParser()
                config.read('./static/ftp_config.ini')

                # read config
                host = config['Login']['host']
                user = config['Login']['user']
                password = config['Login']['password']

            # enter config manually
            elif load_config in ['n', 'no']:
                host = input("Enter hostname: ")
                user = input("Enter username: ")
                password = input("Enter password")

            else:
                # skip program loop
                print("\033[31mInvalid Input!\033[0m")
                continue

            # connect
            try:
                ftp = FTPHost(host=host, user=user, passwd=password)
            except ftplib.all_errors as e:
                print("\033[31m" + str(e) + "\033[0m")
                continue

            # get files
            directories = ftp.listdir(".")

            # download loop
            while True:
                # list all files with indices
                print("\n\033[7mListed Datasets\033[0m")
                for i, file in enumerate(directories):
                    print("[" + str(i) + "]" + "\t" + str(file))

                # file to download
                try:
                    target_index = int(input("Enter a number 0-" + str(len(directories) - 1) + " to download the corresponding dataset"))
                except ValueError:
                    print("\033[31mInvalid Input!\033[0m")
                    continue

                if not (0 <= target_index < len(directories)):
                    print("\033[31mInvalid Input!\033[0m")
                    continue

                # download directory
                os.chdir("./data")
                try:
                    for item in ftp.walk(directories[target_index]):
                        print("Creating dir " + item[0])
                        os.mkdir(item[0])
                        for file in item[2]:
                            print("Copying File " + str(item[0]) + "/" + str(file))
                            ftp.download(ftp.path.join(item[0], file),
                                         os.path.join(item[0], file))

                except FileExistsError:
                    print("\033[33m" +
                          "A local copy of this dataset already exists!" +
                          "\033[0m")
                    continue

                print("\033[32mDownload successful!\033[0m")
                print("Restart your dashboard to make the dataset available")

                # return to top directory for next download
                os.chdir("../")


if __name__ == "__main__":
    main()

import datetime, play_scraper, re, requests, subprocess, sys, time

TERMINAL_ENCODING = 'latin-1'
FILE_ENCODING = 'utf-16'

def main():
    print("\nFind-Optimise: Find what apps are continuously being optimised\n" +
          "Code by Wilko Grunefeld. Licensed under AGPLv3\n" +
          "---")
    result = ""

    if len(sys.argv) == 2:
        f = open(sys.argv[1], "rb")
        raw = f.read()
        result = raw.decode(FILE_ENCODING)
        f.close()
    else:
        print("To analyse a log file, enter its name or press enter to\n" +
        "reboot and analyse a connected phone. If choosing latter option, please verify that USB\n" +
        "debugging is enabled on target device.")
        given_input = input("> ")
        print("")

        if len(given_input) == 0:
            start_time = datetime.datetime.now().strftime('%m-%d %H:%M:%S') + ".000"

            subprocess.run(['adb', 'reboot'])

            print("Waiting for phone to boot.\r", end='')

            check_cmd = ['adb','shell','getprop sys.boot_completed']
            while subprocess.run(check_cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL).stdout.decode(TERMINAL_ENCODING).rstrip() != '1':
                time.sleep(1)

            print("Phone has finished booting.")

            logcat_cmd = ['adb', 'logcat', '-t', start_time, 'dex2oat:I']
            result_bytes = subprocess.run(logcat_cmd, stdout=subprocess.PIPE).stdout

            results = result_bytes.decode(TERMINAL_ENCODING)
        else:
            f = open(given_input, "rb")
            raw = f.read()
            result = raw.decode(FILE_ENCODING)
            f.close()

    regex = re.compile('([A-z]{1}[A-Za-z\d_]*\.)+([A-z]{1}[A-Za-z\d_]*\.)+[A-Za-z][A-Za-z\d_]*')
    apps = []

    result_array = result.splitlines()

    for counter, line in enumerate(results_array):
        print(str(100*counter/len(result_array)))
        if 'I/dex2oat' in line and '.odex' not in line and '.jar' not in line:
            curr_app = regex.search(line)
            if curr_app is not None:
                apps.append(App(curr_app.group()))

    if len(apps) == 0:
        print("Sorry! Unfortunately I couldn't uncover anything for you.")
    else:
        for app in apps:
            print(app.list_item())

    print("---\nProcessed " + str(len(apps)) + " apps\n")

class App:
    def __init__(self, package_id):
        super().__init__()
        self._id = package_id

        # Attempt to get Play Store info
        try:
            app_data = play_scraper.details(self._id)
            self._title = app_data["title"]
            self._dev = app_data["developer"]
            self._play = True
        except Exception:
            self._play = False
    def __str__(self):
        return "App (" + self._id + ")"
    def __repr__(self):
        return f"App({self._id!r})"
    def list_item(self):
        if self._play:
            return "* " + self._title + " by " + self._dev + " (" + self._id + ")"
        else:
            return "* " + self._id

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)

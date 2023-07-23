import requests
import subprocess
from pathlib import Path

from connector.custom_exceptions import NetworkNotFound

CONFIGS_DIR = Path(__file__).parent.joinpath("network_configs").as_posix()
DEFAULT_CONFIG = Path("config_sample").with_suffix(".txt").as_posix()


class Connector:
    def __init__(
            self,
            config_dir: str = CONFIGS_DIR,
            config_sample: str = DEFAULT_CONFIG,
    ):

        self.config_dir = config_dir
        self.config_sample = config_sample

        self.available_networks = self.list_available_networks()
        self.open_networks = self.list_open_networks()

    @property
    def known_networks(self) -> list:

        return list(
            set(self.available_networks.keys()).intersection(
                set(self.list_known_networks())
            )
        )

    @staticmethod
    def design_std_output(cmd_output: str) -> dict:
        if not isinstance(cmd_output, str):
            cmd_output = str(cmd_output)

        blocks = cmd_output.split('SSID ')[1:]

        networks = {}
        for b in blocks:
            parts = b.split('\\r\\n')
            network_name = parts[0].split(':')[-1].strip(' \r\n')
            ssid = parts[0].split(':')[0].strip(' \r\n')
            networks[network_name] = {}
            networks[network_name]['ssid'] = ssid
            for p in parts[1:-2]:
                key_ = p.split(':')[0].strip(' \r\n')
                value_ = p.split(':')[-1].strip(' \r\n')
                networks[network_name][key_] = value_

        return networks

    @staticmethod
    def design_known_ouput(networks: str) -> list:
        if not isinstance(networks, str):
            networks = str(networks)

        return [n.split(':')[-1].strip('\\r ')
                for n in networks.split('\\n')
                if "User Profile" in n]

    @staticmethod
    def connected_to_internet(url: str = 'http://www.google.com/',
                              timeout: int = 5) -> bool:
        try:
            _ = requests.head(url, timeout=timeout)
            return True
        except requests.ConnectionError:
            return False

    @staticmethod
    def request_password() -> str:
        passwrd = input('Network is Password-Protected. Enter password: ')
        return passwrd

    @staticmethod
    def get_permission() -> bool:
        answ = input("Do You Allow to Connect to Open Network? [y/n] ")
        if answ.lower() in ['y', 'yes']:
            return True

    @staticmethod
    def get_config(network_name: str,
                   password: str,
                   config_file: str) -> str:
        with open(config_file, 'r') as f:
            config = f.read()

        return config.format(network=network_name,
                             password=password)

    @staticmethod
    def save_config(network_name: str,
                    config: str,
                    config_dir: str) -> str:

        file_name = f'{config_dir}/{network_name}.xml'
        with open(file_name, 'w') as f:
            f.write(config)
        return file_name

    def ask_for_preferred_network(self) -> str:

        question_text = f'Following Networks are Available\n{", ".join(self.available_networks.keys())}'
        action_text = 'Type Your Preferred Network or Hit Enter: '

        user_answ = input(question_text + '\n' + action_text)

        return user_answ

    def list_available_networks(self) -> dict:
        try:
            visible_networks = subprocess.check_output(["netsh",
                                                        "wlan",
                                                        "show",
                                                        "networks"])

            return self.design_std_output(
                visible_networks
            )

        except subprocess.CalledProcessError:
            print('MAKE SURE WIFI IS TURNED ON')
            exit()

    def list_known_networks(self) -> list:
        known_networks = subprocess.check_output(["netsh",
                                                  "wlan",
                                                  "show",
                                                  "profiles"])

        return self.design_known_ouput(known_networks)

    def list_open_networks(self) -> list:
        return [n[0] for n in self.available_networks.items() if n[1]['Authentication'] == "Open"]

    def add_network_profile(self,
                            network_name: str) -> None:
        password = self.request_password()
        config = self.get_config(network_name,
                                 password,
                                 config_file=f'{self.config_dir}/{self.config_sample}')
        config_filename = self.save_config(network_name,
                                           config,
                                           self.config_dir)

        try:

            _ = subprocess.check_output(["netsh",
                                         "wlan",
                                         "add",
                                         "profile",
                                         f'filename="{config_filename}"'])

        except:
            print('PASSWORD IS INCORRECT. EXITING...')
            exit()

    def verify_name(self,
                    network_name: str) -> None:
        if network_name not in self.available_networks.keys():
            raise NetworkNotFound(network_name)
        if network_name not in self.known_networks and network_name not in self.open_networks:
            self.connect_with_password(network_name)

    def connect_to_network(self,
                           network_name: str) -> None:
        self.verify_name(network_name)
        message = subprocess.check_output(["netsh",
                                           "wlan",
                                           "connect",
                                           f"name={network_name}"])

        if "success" in str(message):
            print(f'CONNECTED TO "{network_name}"')
            exit()

    def connect_with_password(self,
                              network_name: str) -> None:
        self.add_network_profile(network_name)
        self.connect_to_network(network_name)

    def connect_to_known_network(self) -> None:
        if self.known_networks:
            print('CONNECTING TO ONE OF THE KNOWN NETWORKS')
            self.connect_to_network(self.known_networks[0])

    def connect_to_open_network(self) -> None:
        if self.open_networks:
            if self.get_permission():
                print('CONNECTING TO ONE OF THE OPEN NETWORKS')
                self.connect_to_network(self.open_networks[0])

    def final_attempt(self) -> None:
        print('NO KNOWN OR OPEN NETWORKS WERE FOUND.')
        preferred_network = self.ask_for_preferred_network()
        if not preferred_network:
            print('EXITING...')
            exit()
        self.connect_to_network(preferred_network)

    def establish_connection(self) -> None:
        preferred_network = self.ask_for_preferred_network()
        if preferred_network:
            self.connect_to_network(preferred_network)
        self.connect_to_known_network()
        self.connect_to_open_network()
        self.final_attempt()

    def run(self) -> None:
        if not self.connected_to_internet():
            self.establish_connection()
        else:
            print('CONNECTED TO INTERNET')

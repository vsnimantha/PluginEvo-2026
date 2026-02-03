import configparser
from configparser import ExtendedInterpolation
from typing import Any, Dict
import os

class ConfigManager:
    _instance = None  # Class variable to store the singleton instance
    _initialized = False  # Track if initialization has occurred

    def __new__(cls, config_file: str = 'Config/config.ini'):
        """
        Singleton pattern implementation - controls instance creation
        """
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, config_file: str = 'Config/config.ini'):
        """
        Initialize configuration manager (only once)
        """
        if self._initialized:
            return
            
        self.config_file = config_file
        self._config = configparser.ConfigParser(interpolation=ExtendedInterpolation())
        self._config.optionxform = str
        self._data: Dict[str, Dict[str, Any]] = {}
        self.load_config()
        self._initialized = True

    def load_config(self) -> None:
        """
        Load and parse the configuration file
        (Your existing implementation preserved exactly)
        """
        if not os.path.exists(self.config_file):
            raise FileNotFoundError(f"Config file not found: {self.config_file}")

        try:
            self._config.read(self.config_file)
            # Convert to dictionary for easier access
            for section in self._config.sections():
                self._data[section] = {}
                for key, value in self._config.items(section):
                    # Auto-convert boolean strings
                    if value.lower() in ('true', 'false'):
                        self._data[section][key] = self._config.getboolean(section, key)
                    # Auto-convert numbers
                    elif value.isdigit():
                        self._data[section][key] = self._config.getint(section, key)
                    else:
                        try:
                            # Try converting to float if possible
                            self._data[section][key] = self._config.getfloat(section, key)
                        except ValueError:
                            self._data[section][key] = value
        except Exception as e:
            raise RuntimeError(f"Error loading config: {str(e)}")

    def get(self, section: str, key: str, default: Any = None) -> Any:
        """
        Get a configuration value with optional default
        (Your existing implementation preserved exactly)
        """
        try:
            return self._data[section][key]
        except KeyError:
            if default is not None:
                return default
            raise AttributeError(f"Config key '{key}' not found in section '{section}'")

    def __getattr__(self, name: str) -> Dict[str, Any]:
        """
        Allow dot notation access to sections (e.g., config.database)
        (Your existing implementation preserved exactly)
        """
        if name in self._data:
            return SectionProxy(self._data[name])
        else:
            print(f"No such config section: '{name}'")
        # raise AttributeError(f"No such config section: '{name}'")
    
    def update_config_value(self, section: str, key: str, value: Any) -> None:
        """
        Update a configuration value both in memory and in the config file
        
        Args:
            section: The section name in the config file
            key: The key to update
            value: The new value to set
        """
        # Update in-memory data
        if section not in self._data:
            self._data[section] = {}
        self._data[section][key] = value
        
        # Update the configparser object
        if not self._config.has_section(section):
            self._config.add_section(section)
        self._config.set(section, key, str(value))
        
        # Write changes back to file
        with open(self.config_file, 'w') as configfile:
            self._config.write(configfile)

class SectionProxy:
    """
    Proxy class for dot notation access to section values
    (Your existing implementation preserved exactly)
    """
    def __init__(self, section_data: Dict[str, Any]):
        self._section_data = section_data

    def __getattr__(self, name: str) -> Any:
        try:
            return self._section_data[name]
        except KeyError:
            raise AttributeError(f"No such config key: '{name}'")


if __name__ == "__main__":
    try:
        # First instance will create and load the config
        config = ConfigManager('Config/config.ini')
        
        # This will return the same instance, config file path won't change
        config2 = ConfigManager()  
        
        # Verify they're the same instance
        print(f"Same instance? {config is config2}")  # Will print True
        
        # Your existing test case
        print(config.GRAMMAR.print_function_bnf)
        
    except Exception as e:
        print(f"Configuration error: {e}")
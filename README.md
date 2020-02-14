# geckodriver-autoinstaller
Automatically download and install [geckodriver](https://github.com/mozilla/geckodriver/releases/latest) that supports the currently installed version of firefox. This installer supports Linux, MacOS and Windows operating systems.

## Installation

```bash
pip install geckodriver-autoinstaller
```

## Usage
Just type `import geckodriver_autoinstaller` in the module you want to use geckodriver.

## Example
```
from selenium import webdriver
import geckodriver_autoinstaller


geckodriver_autoinstaller.install()  # Check if the current version of geckodriver exists
                                     # and if it doesn't exist, download it automatically,
                                     # then add geckodriver to path

driver = webdriver.Firefox()
driver.get("http://www.python.org")
assert "Python" in driver.title
```

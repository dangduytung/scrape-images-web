# Scrape Images Web

Scrape all images from input URL web

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install needed libraries.

```bash
pip install requests
pip install fake_useragent
pip install bs4
pip install cssutils
pip install tk
```

## Console

```bash
# Console
py app/main.py [url]

# Window (use library tkinter)
py app/main_gui.py
```


## GUI
Using `tkinter` to build file `exe`<br>
Referece [https://pyinstaller.org/en/stable/usage.html](https://pyinstaller.org/en/stable/usage.html)
```bash
# Create file scrape.spec (add some files, favicon...)
pyi-makespec --add-data "app/logging.conf;."  --add-data "app/assets/user_agents.txt;assets/" --windowed --icon=app/favicon.ico --name scrape app/main_gui.py
```

```bash
# Build exe from scrape.spec (output is folder `dist`)
pyinstaller --clean scrape.spec
```

### Finally run file `scrape.exe` will open a window to input URL. Output is folder `data` contain images, folder `logs` for check log requests

## Contributing

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License

[MIT](https://choosealicense.com/licenses/mit/)
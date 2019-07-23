# youdao-tr-free

Youdao translate for free -- local cache. Let's hope it lasts.
### Limitation
Maximum of 50 characters per query -- you'll have to do some processing if you want to handle longer text.

### Installation

```pip install youdao-tr-free```

or

* Install (pip or whatever) necessary requirements, e.g. ```
pip install requests_cache`` or ```
pip install -r requirements.txt```
* Drop the file youdao_tr.py in any folder in your PYTHONPATH (check with import sys; print(sys.path)
* or clone the repo (e.g., ```git clone https://github.com/ffreemt/youdao-tr-free.git``` or download https://github.com/ffreemt/youdao-tr-free/archive/master.zip and unzip) and change to the youdao-tr-free folder and do a ```
python setup.py develop```

### Usage

```
from youdao_tr import youdao_tr
print(youdao_tr('hello world'))  # ->'你好，世界'
print(youdao_tr('hello world', to_lang='de'))  # ->'Hallo Welt'
print(youdao_tr('hello world', to_lang='fr'))  # ->'Bonjour le monde'
print(youdao_tr('hello world', to_lang='ja'))  # ->'こんにちは世界'
```

Consult the official website for language pairs supported.

### Acknowledgments

* Thanks to everyone whose code was used
